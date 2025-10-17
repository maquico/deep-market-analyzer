import json
import base64
import boto3
import requests
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from prompts import (
    pdf_parser_v1_prompt,
    messages_extraction_v1_prompt,
    images_query_generation_v1_prompt
)
from tools.gen_img import call_img_gateway
from dynamo_handler import add_document_record

API_URL = "https://e6znu0x2lk.execute-api.us-east-1.amazonaws.com/dev/generate-pdf"

template = """<div style="padding:8px 0 24px 0;">  <div style="display:flex;justify-content:space-between;align-items:center;">    <div>      <h1 style="margin:0;font-size:28pt;color:#0b3c5d;font-weight:700;">{{main_title}}</h1>      <p style="margin:6px 0 0 0;color:#556; font-size:11pt;">{{subtitle}}</p>    </div>    <div style="text-align:right;color:#777;font-size:10pt;">      <div>Prepared by: {{prepared_by}}</div>      <div>{{date}}</div>    </div>  </div></div><section style="margin-top:12px;">  <h2 style="font-size:14pt;color:#0b3c5d;margin:0 0 6px 0;">Executive Summary</h2>  <h3 style="font-size:11pt;color:#2e5160;margin:0 0 8px 0;">{{summary_title}}</h3>  <p style="margin:0 0 12px 0;color:#333;line-height:1.45;">{{executive_paragraph}}</p></section>{{#each highlights}}<section style="margin-top:14px;">  <h2 style="font-size:14pt;color:#0b3c5d;margin:0 0 8px 0;">{{this.title}}</h2>  <h3 style="font-size:11pt;color:#2e5160;margin:0 0 8px 0;">{{this.subtitle}}</h3>  <p style="margin:0 0 10px 0;color:#333;line-height:1.45;">{{this.paragraph}}</p>  <div style="border:1px solid #eef2f5;border-radius:8px;padding:10px;background:#fff;">    <div style="font-size:10pt;color:#444;margin-bottom:8px;font-weight:600;">Image: {{this.image_title}}</div>    <div style="background:{{this.image_bg}};padding:12px;border-radius:6px;display:flex;align-items:center;justify-content:center;">      {{{this.image_svg}}}    </div>  </div></section>{{/each}}<section style="margin-top:18px;">  <h2 style="font-size:13pt;color:#0b3c5d;margin:0 0 8px 0;">Closing notes</h2>  <p style="margin:0;color:#333;line-height:1.45;">{{closing_paragraph}}</p></section>"""

class BaseHighlight(BaseModel):
    title: str = Field(..., description="Title of the highlight")
    subtitle: str = Field(..., description="Subtitle of the highlight")
    paragraph: str = Field(..., description="Paragraph text of the highlight")
    image_title: str = Field(..., description="Short Title of the image")


class GenerationHighlight(BaseHighlight):
    image_id: str = Field(default="", description="Short identifier for the image, e.g., 'img_12345'. Empty string if no image.")
    
class BaseReportDefinition(BaseModel):
    summary_title: str = Field(..., description="Summary title of the report")
    executive_paragraph: str = Field(..., description="Executive summary paragraph")
    highlights: list[GenerationHighlight] = Field(..., description="List of highlights in the report, 1 to 6 items")
    closing_paragraph: Optional[str]= Field(..., description="Closing paragraph of the report")

class FinalHighlight(BaseHighlight):
    image_svg: str = Field(default="", description="SVG content for the image, or empty string if no image")

    image_bg: str = Field(..., description="Background color for the image in hex format, e.g., '#f7fbf8'")

class FinalReportDefinition(BaseReportDefinition):
    date: str = Field(default=datetime.now().isoformat(), description="Date of the report in ISO-like format, e.g., 'October 12, 2025'")
    highlights: list[FinalHighlight]

class ModelInput(BaseModel):
    model_id: str
    temperature: float = 0.3

def call_pdf_gateway(data=None, template=template):
    payload = {
        "template": template,
        "data": data
    }
    resp = requests.post(API_URL, json=payload, timeout=120)

    # Try JSON
    try:
        body = resp.json()
    except ValueError:
        body = None

    # --- Case 2: JSON metadata with presigned URL ---
    if isinstance(body, dict) and "url" in body:
        url = body["url"]
        return url

    print("Unexpected response:")
    print(resp.text[:500])
    return {"ok": False, "response": resp.text}

def extract_info_from_messages(messages: list[AnyMessage],
                               model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                               temperature: float = 0.3) -> str:
    "Extracts the relevant information from the messages to be included in the report"
    prompt_template = PromptTemplate.from_template(messages_extraction_v1_prompt)
    parser = StrOutputParser()
    llm = ChatBedrock(model=model_id,
                     temperature=temperature)

    method_chain = (
        prompt_template
        | llm
        | parser
    )
    conversation = ""
    for m in messages:
        if isinstance(m, AIMessage):
            m.type = "AIMessage"
        elif isinstance(m, HumanMessage):
            m.type = "HumanMessage"
        elif isinstance(m, SystemMessage):
            m.type = "SystemMessage"
        elif isinstance(m, ToolMessage):
            m.type = "ToolMessage"
        conversation = conversation + f"<{m.type}>\n{m.content}\n</{m.type}>\n"
    report_info = method_chain.invoke({"conversation": conversation})
    return report_info

def generate_image_query(info: str,
                         model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                         temperature: float = 0.3):
    "generates query and calls image generation tool"
    prompt_template = PromptTemplate.from_template(images_query_generation_v1_prompt)
    parser = StrOutputParser()
    llm = ChatBedrock(model=model_id,
                     temperature=temperature)

    method_chain = (
        prompt_template
        | llm
        | parser
    )
    image_query = method_chain.invoke({"report_information": info})
    return image_query

def generate_images_for_report(info: str,
                               chat_id: str,
                               user_id: str,
                               model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                               temperature: float = 0.3) -> list:
    "Generate images to be included in the report"
    query = generate_image_query(info, model_id=model_id, temperature=temperature)
    images = call_img_gateway(use_case=query, chat_id=chat_id, user_id=user_id)
    
    return images


def generate_report_definition(info: str,
                               images: list,
                               model_id: str,
                               temperature: float) -> dict:
    "Structured output with images included"
    prompt_template = PromptTemplate.from_template(pdf_parser_v1_prompt)

    llm = ChatBedrock(model=model_id,
                 temperature=temperature)
    
    structured_llm = llm.with_structured_output(schema=BaseReportDefinition)
    

    # Use JsonOutputParser with Pydantic model
    method_chain = (
        prompt_template
        | structured_llm
    )
    base_report_object = method_chain.invoke({"info": info,
                                              "images": images})
    
    if not isinstance(base_report_object, BaseReportDefinition):
        raise ValueError("Failed to generate valid report definition")
    return base_report_object


def build_final_report(report: BaseReportDefinition, images: list) -> FinalReportDefinition:
    final_highlights = []
    for h in report.highlights:
        image_svg = ""
        if h.image_id:
            image_record = next((img for img in images if img["image_id"] == h.image_id), None)
            if image_record and "presigned_url" in image_record:
                image_svg = f'<img src="{image_record["presigned_url"]}" alt="{h.image_title}" style="max-width: 400px; height: auto;" />'  
        final_highlight = FinalHighlight(
            title=h.title,
            subtitle=h.subtitle,
            paragraph=h.paragraph,
            image_title=h.image_title,
            image_bg="#f7fbf8",
            image_svg=image_svg
        )
        final_highlights.append(final_highlight)

    final_report = FinalReportDefinition(
        summary_title=report.summary_title,
        executive_paragraph=report.executive_paragraph,
        highlights=final_highlights,
        closing_paragraph=report.closing_paragraph
    )
    return final_report

def execute_pdf_report_generation_flow(messages: list[AnyMessage],
                  chat_id: str,
                  user_id: str,
                  extract_model: ModelInput,
                  images_query_model: ModelInput,
                  report_def_model: ModelInput) -> dict:
    "Create a report from the messages"
    info = extract_info_from_messages(messages=messages,
                                      model_id=extract_model.model_id,
                                      temperature=extract_model.temperature)
    print("\n\nExtracted info:", info)
    images = generate_images_for_report(info=info,
                                        chat_id=chat_id,
                                        user_id=user_id,
                                        model_id=images_query_model.model_id,
                                        temperature=images_query_model.temperature)
    images = images.get("images", [])
    print("\n\nGenerated images:", images)
    report = generate_report_definition(info=info,
                                        images=images,
                                        model_id=report_def_model.model_id,
                                        temperature=report_def_model.temperature)
    print("\n\nGenerated report definition:", report)
    
    final_report = build_final_report(report=report, images=images)
    print("\n\nFinal report with images:", final_report)

    pdf_presigned_url = call_pdf_gateway(data=final_report.model_dump(), template=template)
    print("\n\nPDF generation response:", pdf_presigned_url)

    # Store report record in DynamoDB
    document_record = {
        "chat_id": chat_id,
        "user_id": user_id,
        "report_data": final_report.model_dump(),
        "pdf_url": pdf_presigned_url if isinstance(pdf_presigned_url, str) else "",
    }
    add_document_record(document_record)

    return pdf_presigned_url

if __name__ == "__main__":
    # Example HTML (you can wrap with wrapInHtmlPage(content))
    data = {
        "date": "October 12, 2025",
        "summary_title": "Quick takeaways",
        "executive_paragraph": "This quarter shows measured growth in payments and selective expansion in renewables. Short notes and illustrative images follow.",
        "highlights": [
          {
            "title": "Company Highlight — GreenGrid",
            "subtitle": "Why it matters",
            "paragraph": "GreenGrid is scaling rooftop deployments via local partners. Contract wins and improved unit economics are driving adoption.",
            "image_title": "GreenGrid installation",
            "image_bg": "#f7fbf8",
            "image_svg": "<img src=\"https://aws-s3-images-hackaton.s3.us-east-1.amazonaws.com/angel27/generated_image_196499096_1.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAWO23YXWVJKB4TRMP%2F20251013%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251013T033305Z&X-Amz-Expires=300&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEJT%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQCdSuaMlcIcB%2BPUSaPa78f2fYoLqjEIklHjDFOsvVKLnQIgLjJIDIsXt62hp4RvWDHhGgr%2FyaEf74jXkmgKSQpB5w8q7gIIPRABGgw0NDQxODQ3MDY0NzQiDKuDB47Mj95lupMk6irLApfjH%2FUmAIXkCGQt6q1Q22if6bWDy5HGi44%2F%2B5zbRKfgKvp%2B162VzlaNbPSB%2BZYTqHHWktId1teAEpuEUp%2FS9loT9327G8xtWUNXfyQ%2Bu7jpq8YNwHDyVNcgkdH9bXyqXhgR1%2BJTGWAprkA9h5x3CaXPPj%2Fj7vXzQJJmITCcnYBG3ekByvCGnJdybatX0o7UvrSLptpM4TLpZJRQZLRjHwzw9mjo8Xtkm0rMDLRbKVlgnpxXwSFl%2BfRRFAz2iLSpa9Hi%2B22C6gOOlLcduPCvCyKmBjw0DBlRwjlMgp%2BpAiz3TFatxHyeeDiKBiI8AdlkitFpx0w6fPYwkO2ACjHeSf6ZNkDBPqW8cnm8YqCpsE%2FZ1Qo4f753WIUB6ktCEbVv8cYNUFqTonvPPH8p65PRbU5uVfvcvFDwDziYUmJhzMsD9AniRRICOOJQxYswx9KvxwY6rQKOR5%2B%2Fdj6GrUlCW%2FHChGx1nkpJpSIc1mycVRoTCq4vBZH8XPCJLUCnioD5r%2BlUdpeRtkFdAnVD%2Fo%2FXLbOG5Xjyjpn4oy1%2BTHbbZGPmllvmPKiH2OKpIadooj%2BLQdCRh23n1r6k%2F1pFynKtlicWIIkuH9a3ceKS1jmDh6lWdf90wnztBKlGiZvcfRQmyoVSpXT%2BUxHg8Ph8UTSfS%2BMCfGVi5lIWXDWlxlYC%2F356l1idYMzhEJd2BhD6nyLDh0Ts%2BEiB%2FPw1A3aOMUa1kNOO5%2FbzsoxjvTmmCpiBKiZ8qH8WoiC66xqeLfbrf%2F93nm3TBIZ8glkAFsfCmPRJq%2BmiOHFb%2BDPTdKni3emPAAq1XbWTQJiC%2B7d9K2nFXz7mPZ630KkhI7o5HBePqocWqMOK&X-Amz-Signature=65836f23146d6bc2fc75453a4ae4365c6d266a21d2231aa546d3b187919bd689&X-Amz-SignedHeaders=host&response-content-disposition=inline\" alt=\"Imagen de prueba\" style=\"max-width: 400px; height: auto;\" />"
            },
          {
            "title": "Use Case — FastPay",
            "subtitle": "Short narrative",
            "paragraph": "FastPay's API-first settlement platform is expanding across SMB ecosystems; monitor margins as volumes scale.",
            "image_title": "FastPay integration mock",
            "image_bg": "#f3f8ff",
            "image_svg": ""
          }
        ],
        "closing_paragraph": "Use these sections as simple slides or single-page summaries. If you want exported PNG images instead of inline SVGs, I can include base64-encoded raster images."
    }

    # Call the PDF generation gateway
    #result = call_pdf_gateway(template=json.dumps(template)[1:-1][1:-1], data=data)
    #print("Result:", result)

    # Extract info from messages
    messages = [
        HumanMessage(content="Hola, estoy planeando lanzar un producto SaaS que use modelos de lenguaje para resumen automático de documentos. ¿Qué pasos debo considerar primero?"),
        AIMessage(content="¡Genial! Primero define claramente el caso de uso (qué tipo de documentos y qué nivel de resumen necesitas), luego: 1) selecciona modelos y proveedor (latencia, coste, privacidad), 2) diseña el pipeline de ingestión y preprocesado, 3) planifica el almacenamiento de datos y el control de versiones, 4) establece métricas de calidad (ROUGE/BLEU + evaluación humana) y 5) prepara el plan de despliegue y monitoreo. ¿Quieres que te detalle la arquitectura técnica?"),
        HumanMessage(content="Sí — detállame la arquitectura ideal para producción, incluyendo manejo de costos y privacidad de datos."),
        AIMessage(content="Arquitectura propuesta (resumen): 1) Frontend ligero que envía documentos a un API; 2) API Gateway + servicio de ingestión (validación, OCR si hace falta); 3) cola (SQS/Kafka) para desacoplar procesamiento; 4) workers que llaman a modelos LLM (on-demand o inferencia en batch) y almacenan metadatos/artefactos en base de datos; 5) almacenamiento de objetos (S3) con cifrado; 6) sistema de auditoría y retrain, y 7) capa de observabilidad (trazas, métricas coste por petición). Para controlar costos: caching de respuestas, batching, límites de tokens, y usar modelos distilados para tareas de baja complejidad. Para privacidad: encriptación en tránsito y reposo, anonimización y acuerdos con proveedores (SLA/TOU). ¿Preparo un diagrama o la lista de componentes con tecnologías recomendadas?"),
        HumanMessage(content="Antes de eso, ¿me puedes dar una investigación breve y concreta del mercado de IA ahora (tamaño, crecimiento, adopción empresarial y riesgos principales)? Necesito datos reales para justificar la inversión."),
        AIMessage(content=(
            "Breve investigación del mercado de IA (resumen ejecutiva):\n\n"
            "1) Tamaño y crecimiento: el mercado global de IA fue valorado en cientos de miles de millones de dólares en 2024–2025 y las proyecciones para la próxima década muestran un crecimiento anual compuesto (CAGR) alto —reportes estiman cifras que varían según la metodología, pero apuntan a un mercado que puede crecer desde ~USD 233–279B en 2024 hacia varios billones en los próximos 8–10 años. :contentReference[oaicite:0]{index=0}\n\n"
            "2) Adopción empresarial: el uso de IA (y, más recientemente, de generative AI) se ha acelerado: encuestas de adopción muestran que una mayoría creciente de organizaciones ya usan IA en al menos una función de negocio (más del 70% en algunos estudios recientes). Esto incluye aplicaciones en atención al cliente, generación de contenido, automatización de procesos, análisis y soporte de decisión. :contentReference[oaicite:1]{index=1}\n\n"
            "3) Infraestructura y jugadores clave: la inversión en infraestructura (chips, centros de datos) es masiva —los fabricantes de semiconductores y proveedores cloud (Nvidia, TSMC, AWS, Microsoft, Google) son piezas críticas en la cadena de valor. Recientes movimientos del mercado y previsiones de fabricantes de chips confirman demanda sostenida por hardware especializado. :contentReference[oaicite:2]{index=2}\n\n"
            "4) Oportunidades y riesgos: las oportunidades incluyen automatización de tareas, aumento de productividad (generative AI con impacto económico potencial en trillones) y nuevos productos/servicios. Los riesgos significativos son: sobrevaloración/efervescencia en startups, dependencia de proveedores de infraestructuras clave, preocupaciones regulatorias y de privacidad, y retos de confianza/seguridad en modelos generativos. Informes de mercado y análisis financieros recientes advierten sobre valoraciones muy elevadas en el segmento privado. :contentReference[oaicite:3]{index=3}\n\n"
            "Conclusión corta: el mercado ofrece una oportunidad grande y acelerada, pero la decisión de inversión debe incluir mitigaciones por riesgo tecnológico, control de costes infraestructurales, y un plan claro de cumplimiento y privacidad."
        )),
        HumanMessage(content="Perfecto — por favor genera el reporte completo basándote en la investigación anterior: estructura ejecutiva, datos clave, implicaciones para nuestro producto SaaS, recomendaciones técnicas y de negocio, y una sección de riesgos con mitigaciones.")
    ]

    output = execute_pdf_report_generation_flow(
        messages=messages,
        chat_id="test_conv3",
        user_id="angel27",
        extract_model=ModelInput(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", temperature=0.3),
        images_query_model=ModelInput(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", temperature=0.3),
        report_def_model=ModelInput(model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", temperature=0.3)
    )

    print("Final output:", output)


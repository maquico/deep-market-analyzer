import json
import base64
import requests
import os

API_URL = "https://e6znu0x2lk.execute-api.us-east-1.amazonaws.com/dev/generate-pdf"

template = """<div style="padding:8px 0 24px 0;">  <div style="display:flex;justify-content:space-between;align-items:center;">    <div>      <h1 style="margin:0;font-size:28pt;color:#0b3c5d;font-weight:700;">{{main_title}}</h1>      <p style="margin:6px 0 0 0;color:#556; font-size:11pt;">{{subtitle}}</p>    </div>    <div style="text-align:right;color:#777;font-size:10pt;">      <div>Prepared by: {{prepared_by}}</div>      <div>{{date}}</div>    </div>  </div></div><section style="margin-top:12px;">  <h2 style="font-size:14pt;color:#0b3c5d;margin:0 0 6px 0;">Executive Summary</h2>  <h3 style="font-size:11pt;color:#2e5160;margin:0 0 8px 0;">{{summary_title}}</h3>  <p style="margin:0 0 12px 0;color:#333;line-height:1.45;">{{executive_paragraph}}</p></section>{{#each highlights}}<section style="margin-top:14px;">  <h2 style="font-size:14pt;color:#0b3c5d;margin:0 0 8px 0;">{{this.title}}</h2>  <h3 style="font-size:11pt;color:#2e5160;margin:0 0 8px 0;">{{this.subtitle}}</h3>  <p style="margin:0 0 10px 0;color:#333;line-height:1.45;">{{this.paragraph}}</p>  <div style="border:1px solid #eef2f5;border-radius:8px;padding:10px;background:#fff;">    <div style="font-size:10pt;color:#444;margin-bottom:8px;font-weight:600;">Image: {{this.image_title}}</div>    <div style="background:{{this.image_bg}};padding:12px;border-radius:6px;display:flex;align-items:center;justify-content:center;">      {{{this.image_svg}}}    </div>  </div></section>{{/each}}<section style="margin-top:18px;">  <h2 style="font-size:13pt;color:#0b3c5d;margin:0 0 8px 0;">Closing notes</h2>  <p style="margin:0;color:#333;line-height:1.45;">{{closing_paragraph}}</p></section>""",

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


    result = call_pdf_gateway(template=json.dumps(template)[1:-1][1:-1], data=data)
    print("Result:", result)

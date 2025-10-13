// handler.mjs
import chromium from "@sparticuz/chromium";
import puppeteerCore from "puppeteer-core";
import { marked } from "marked";
import Handlebars from "handlebars";
import { S3Client } from "@aws-sdk/client-s3";

/**
 * Entrada esperada (JSON en el body):
 * {
 *   "html": "<h1>Hola</h1>",
 *   "markdown": "# Título",
 *   "template": "<h1>{{title}}</h1>",
 *   "data": { "title": "Factura #123" },
 *   "pdfOptions": { "format": "A4", "margin": { "top":"20mm","bottom":"20mm" } },
 *   "filename": "documento.pdf", // opcional
 *   "user_id": "user123" // opcional, carpeta donde se guardará el PDF
 * }
 */

const isLambda = !!process.env.AWS_REGION;
const S3_BUCKET_NAME = process.env.S3_BUCKET_NAME;
const AWS_REGION = process.env.AWS_REGION;

// Cliente S3
const s3Client = new S3Client({ region: AWS_REGION });

/**
 * Parsea el payload del evento de API Gateway o invocación directa
 * @param {object} event - Evento de Lambda
 * @returns {object} Payload parseado
 */
function parseEventPayload(event) {
  const isApiGateway =
    typeof event?.body === "string" || event?.isBase64Encoded !== undefined;

  if (isApiGateway) {
    const bodyString = event.isBase64Encoded
      ? Buffer.from(event.body, "base64").toString("utf8")
      : event.body || "{}";
    return JSON.parse(bodyString);
  }

  return event || {};
}

/**
 * Genera HTML a partir de template, markdown o HTML directo
 * @param {object} options - Opciones con html, markdown, template, data
 * @returns {string} HTML generado
 */
function generateHtml({ html, markdown, template, data }) {
  if (html) {
    return html;
  }

  if (template) {
    const compiled = Handlebars.compile(template);
    return compiled(data || {});
  }

  if (markdown) {
    return marked.parse(markdown);
  }

  return "<h1>Hello PDF</h1><p>Provide html | markdown | template+data.</p>";
}

/**
 * Envuelve el contenido HTML en una página completa con estilos
 * @param {string} content - Contenido HTML
 * @returns {string} Página HTML completa
 */
function wrapInHtmlPage(content) {
  return `
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        html, body { margin: 0; padding: 0; }
        body { font-family: system-ui, -apple-system, Arial, sans-serif; font-size: 12pt; }
        @page { size: A4; margin: 20mm; }
        header { position: running(header); }
        footer { position: running(footer); }
        .page-header { font-size: 11pt; color: #555; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 12px; }
        .page-footer { font-size: 10pt; color: #777; border-top: 1px solid #eee; padding-top: 6px; margin-top: 12px; }
        .page-break { page-break-before: always; }
      </style>
    </head>
    <body>
      <header class="page-header">AI Generated Document</header>
      ${content}

    </body>
    </html>
  `.trim();
}

/**
 * Obtiene la configuración de Chromium según el entorno
 * @returns {Promise<object>} Configuración de Chromium
 */
async function getChromiumConfig() {
  if (isLambda) {
    return {
      executablePath: await chromium.executablePath(),
      args: chromium.args,
      headless: chromium.headless,
      defaultViewport: chromium.defaultViewport,
    };
  }

  // En local, usa Chromium de puppeteer completo
  const puppeteer = (await import("puppeteer")).default;
  return {
    executablePath: puppeteer.executablePath(),
    args: [],
    headless: true,
    defaultViewport: chromium.defaultViewport,
  };
}

/**
 * Genera un PDF a partir de HTML usando Puppeteer
 * @param {string} html - HTML a convertir
 * @param {object} pdfOptions - Opciones para la generación del PDF
 * @returns {Promise<Buffer>} Buffer del PDF generado
 */
async function generatePdfFromHtml(html, pdfOptions = {}) {
  const config = await getChromiumConfig();

  const browser = await puppeteerCore.launch({
    args: config.args,
    defaultViewport: config.defaultViewport,
    executablePath: config.executablePath,
    headless: config.headless,
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "load" });

    const defaultPdfOptions = {
      printBackground: true,
      format: "A4",
      margin: { top: "20mm", right: "15mm", bottom: "20mm", left: "15mm" },
    };

    const pdfBuffer = await page.pdf({
      ...defaultPdfOptions,
      ...pdfOptions,
    });

    return pdfBuffer;
  } finally {
    await browser.close();
  }
}

/**
 * Genera un nombre único para el archivo PDF
 * @param {string} filename - Nombre base del archivo
 * @param {string} userId - ID del usuario (carpeta donde se guardará)
 * @returns {string} Nombre único con timestamp
 */
function generateUniqueFilename(filename, userId) {
  const timestamp = Date.now();
  const randomString = Math.random().toString(36).substring(2, 8);
  const baseName = (filename || 'document.pdf').replace(/[^\w.-]/g, '_');
  const nameWithoutExt = baseName.replace(/\.pdf$/i, '');
  const folder = userId ? `${userId}/pdfs` : 'pdfs';
  return `${folder}/${timestamp}-${randomString}-${nameWithoutExt}.pdf`;
}

/**
 * Sube el PDF a S3 y genera un presigned URL
 * @param {Buffer} pdfBuffer - Buffer del PDF
 * @param {string} filename - Nombre del archivo
 * @param {string} userId - ID del usuario (carpeta donde se guardará)
 * @returns {Promise<object>} Objeto con URL y metadata
 */
async function uploadPdfToS3AndGetUrl(pdfBuffer, filename, userId) {
  const { PutObjectCommand, GetObjectCommand } = await import("@aws-sdk/client-s3");
  const { getSignedUrl } = await import("@aws-sdk/s3-request-presigner");
  
  const s3Key = generateUniqueFilename(filename, userId);
  
  // Subir PDF a S3
  const putCommand = new PutObjectCommand({
    Bucket: S3_BUCKET_NAME,
    Key: s3Key,
    Body: pdfBuffer,
    ContentType: 'application/pdf',
    ContentDisposition: `inline; filename="${filename || 'document.pdf'}"`,
  });

  await s3Client.send(putCommand);
  
  // Generar presigned URL válida por 7 días (máximo permitido)
  const getCommand = new GetObjectCommand({
    Bucket: S3_BUCKET_NAME,
    Key: s3Key,
  });
  
  const presignedUrl = await getSignedUrl(s3Client, getCommand, {
    expiresIn: 7 * 24 * 60 * 60, // 7 días en segundos (máximo permitido)
  });

  return {
    s3Key,
    presignedUrl,
    bucket: S3_BUCKET_NAME,
    region: AWS_REGION,
  };
}

/**
 * Crea la respuesta exitosa con el presigned URL
 * @param {object} s3Data - Datos de S3 (presignedUrl, s3Key)
 * @param {string} filename - Nombre del archivo
 * @param {number} pdfSize - Tamaño del PDF en bytes
 * @returns {object} Respuesta formateada
 */
function createSuccessResponse(s3Data, filename, pdfSize) {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
    body: JSON.stringify({
      ok: true,
      message: 'PDF generated and uploaded successfully',
      filename: filename || 'document.pdf',
      url: s3Data.presignedUrl,
      s3Key: s3Data.s3Key,
      bucket: S3_BUCKET_NAME,
      size: pdfSize,
      expiresIn: '7 days',
    }),
  };
}

/**
 * Crea una respuesta de error
 * @param {Error} error - Error capturado
 * @returns {object} Respuesta de error formateada
 */
function createErrorResponse(error) {
  return {
    statusCode: 500,
    headers: { "Content-Type": "application/json" },
    isBase64Encoded: false,
    body: JSON.stringify({
      ok: false,
      error: true,
      message: error?.message || "PDF error",
    }),
  };
}


export const handler = async (event) => {
  try {
    const payload = parseEventPayload(event);
    const { html, markdown, template, data, pdfOptions, filename, user_id } = payload;

    // 1) Construcción del HTML
    console.log('Generando HTML...');
    const contentHtml = generateHtml({ html, markdown, template, data });
    const pageHtml = wrapInHtmlPage(contentHtml);

    // 2) Generar PDF
    console.log('Generando PDF...');
    const pdfBuffer = await generatePdfFromHtml(pageHtml, pdfOptions);
    console.log(`PDF generado: ${pdfBuffer.length} bytes`);

    // 3) Subir a S3 y obtener presigned URL
    console.log('Subiendo PDF a S3...');
    const s3Data = await uploadPdfToS3AndGetUrl(pdfBuffer, filename, user_id);
    console.log(`PDF subido exitosamente: ${s3Data.s3Key}`);

    // 4) Crear respuesta con el presigned URL
    return createSuccessResponse(s3Data, filename, pdfBuffer.length);
  } catch (err) {
    console.error('Error generando o subiendo PDF:', err);
    return createErrorResponse(err);
  }
};

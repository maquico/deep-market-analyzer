# Lambda PDF Generator

Lambda function para generar PDFs desde HTML, Markdown o Templates Handlebars y subirlos automáticamente a S3.

## 🚀 Características

- ✅ Genera PDFs desde HTML, Markdown o Templates Handlebars
- ✅ Sube automáticamente a S3
- ✅ Genera presigned URLs válidas por 7 días
- ✅ Soporte para imágenes en HTML
- ✅ Organización por carpetas de usuario
- ✅ Configuración de márgenes y formato personalizado

## 📦 Instalación

```bash
npm install
```

## 🧪 Pruebas Locales

```bash
npm start
```

## 🚀 Despliegue

```bash
serverless deploy
```
## 📝 Uso

### Endpoint

```
POST https://e6znu0x2lk.execute-api.us-east-1.amazonaws.com/dev/generate-pdf
```

### Payload

```json
{
  "user_id": "user123",              // Opcional - carpeta del usuario en S3
  "filename": "documento.pdf",        // Opcional - nombre del archivo
  "html": "<h1>Hola</h1>",           // Opción 1: HTML directo
  "markdown": "# Título",             // Opción 2: Markdown
  "template": "<h1>{{title}}</h1>",  // Opción 3: Template Handlebars
  "data": { "title": "Hola" },       // Datos para el template
  "pdfOptions": {                     // Opcional - opciones del PDF
    "format": "A4",
    "margin": {
      "top": "20mm",
      "right": "15mm",
      "bottom": "20mm",
      "left": "15mm"
    }
  }
}
```

### Respuesta

```json
{
  "ok": true,
  "message": "PDF generated and uploaded successfully",
  "filename": "documento.pdf",
  "url": "https://s3.amazonaws.com/bucket/path/to/file.pdf?X-Amz-...",
  "s3Key": "user123/pdfs/1234567890-abc123-documento.pdf",
  "bucket": "{s3_name}",
  "size": 45678,
  "expiresIn": "7 days"
}
```

## 🗂️ Estructura en S3

Si se proporciona `user_id`:
```
s3://{s3_name}/
└── {user_id}/
    └── pdfs/
        └── {timestamp}-{random}-{filename}.pdf
```

Si NO se proporciona `user_id`:
```
s3://{s3_name}/
└── pdfs/
    └── {timestamp}-{random}-{filename}.pdf
```

## 🎨 Ejemplos

### Ejemplo 1: HTML Simple

```json
{
  "user_id": "user123",
  "html": "<h1>Hello World</h1><p>This is a test.</p>",
  "filename": "hello.pdf"
}
```

### Ejemplo 2: HTML con Imagen

```json
{
  "user_id": "user123",
  "html": "<h1>Report</h1><img src='https://example.com/image.png' style='max-width: 400px;' />",
  "filename": "report.pdf"
}
```

### Ejemplo 3: Markdown

```json
{
  "user_id": "user123",
  "markdown": "# Title\n\nThis is **bold** text.",
  "filename": "document.pdf"
}
```

### Ejemplo 4: Template con Datos

```json
{
  "user_id": "user123",
  "template": "<h1>{{title}}</h1><p>Client: {{client}}</p>",
  "data": {
    "title": "Invoice #12345",
    "client": "John Doe"
  },
  "filename": "invoice.pdf"
}
```

## ⚙️ Variables de Entorno

- `AWS_REGION`: Región de AWS (default: `us-east-1`)

## 📄 Permisos IAM Requeridos

La Lambda necesita los siguientes permisos en S3:
- `s3:PutObject`
- `s3:GetObject`
- `s3:PutObjectAcl`

## 🔧 Configuración

### Memoria y Timeout

- **Memoria**: 1536 MB
- **Timeout**: 30 segundos

### Arquitectura

- **Runtime**: Node.js 20.x
- **Architecture**: x86_64

## 📚 Dependencias

- `@sparticuz/chromium`: Chromium para Lambda
- `puppeteer-core`: Control de navegador headless
- `@aws-sdk/client-s3`: Cliente S3 de AWS
- `@aws-sdk/s3-request-presigner`: Generación de presigned URLs
- `handlebars`: Motor de templates
- `marked`: Parser de Markdown

## 🎯 Notas Importantes

1. **Presigned URLs**: Las URLs generadas expiran en 7 días (máximo permitido por AWS)
2. **Imágenes**: Pueden ser URLs externas o base64 embebidas
3. **Formato**: Por defecto es A4, pero se puede cambiar con `pdfOptions`
4. **User ID**: Opcional, pero recomendado para organizar PDFs por usuario

## 👥 Autores

William Ferreira, Luis Adames, Angel Moreno

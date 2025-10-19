# Lambda PDF Generator Service

AWS Lambda service that generates PDF documents from HTML, Markdown, or Handlebars templates and automatically uploads them to S3 with presigned URLs.

## 📋 Features

- **📄 PDF Generation**: Convert HTML, Markdown, or Handlebars templates to PDF
- **☁️ S3 Integration**: Automatic upload to S3 with presigned URLs
- **🎨 Customization**: Support for custom margins, formats, and styling
- **🖼️ Image Support**: Embed external URLs or base64 images
- **📁 Organization**: User-based folder structure in S3
- **⏰ Presigned URLs**: 7-day validity for secure access

## 🚀 Project Structure

```
.
├── handler.mjs          # Main Lambda function with PDF generation logic
├── serverless.yml       # Serverless Framework configuration
├── package.json         # Node.js dependencies
├── local_test.mjs       # Local testing script
└── README.md           # This file
```

## 📦 Prerequisites

1. **AWS CLI** configured with credentials
2. **Serverless Framework** installed:
   ```bash
   npm install -g serverless
   ```
3. **Node.js 20+** installed
4. **S3 Bucket** for PDF storage

## 🔧 Configuration

### 1. Clone and setup the project

```bash
# Install dependencies
npm install
```

### 2. Configure environment variables

Set up the following environment variables in your `serverless.yml` or `.env`:

```env
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
DYNAMO_DOCUMENTS_TABLE_NAME=your-documents-table
```

## 🚢 Deployment

### Deploy to AWS

```bash
# Deploy to staging (dev)
serverless deploy

# Deploy to production
serverless deploy --stage prod

# Deploy to specific region
serverless deploy --region us-west-2
```

### View logs

```bash
serverless logs -f generatePdf --tail
```

### Remove the service

```bash
serverless remove
```

## 📡 API Usage

### Endpoint

After deployment, you'll get this endpoint:

```
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/generate-pdf
```

### Request Payload

You can generate PDFs in three ways: **HTML**, **Markdown**, or **Handlebars Template**.

#### Option 1: Direct HTML

```json
{
  "html": "<h1>Hello World</h1><p>This is a test.</p>",
  "filename": "hello.pdf",
  "user_id": "user123",
  "pdfOptions": {
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

#### Option 2: Markdown

```json
{
  "markdown": "# Title\n\nThis is **bold** text.",
  "filename": "document.pdf",
  "user_id": "user123"
}
```

#### Option 3: Handlebars Template

```json
{
  "template": "<h1>{{title}}</h1><p>Client: {{client}}</p>",
  "data": {
    "title": "Invoice #12345",
    "client": "John Doe"
  },
  "filename": "invoice.pdf",
  "user_id": "user123"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `html` | string | No* | - | Direct HTML content |
| `markdown` | string | No* | - | Markdown content to convert |
| `template` | string | No* | - | Handlebars template |
| `data` | object | No | {} | Data for Handlebars template |
| `filename` | string | No | `document.pdf` | Output filename |
| `user_id` | string | No | null | User folder in S3 |
| `chat_id` | string | No | null | Chat/session identifier |
| `pdfOptions` | object | No | See below | PDF generation options |

*At least one of `html`, `markdown`, or `template` is required.

#### PDF Options

```json
{
  "format": "A4",           // A4, Letter, Legal, etc.
  "margin": {
    "top": "20mm",
    "right": "15mm",
    "bottom": "20mm",
    "left": "15mm"
  },
  "printBackground": true,  // Include background colors/images
  "landscape": false        // Portrait or landscape
}
```

### Response

```json
{
  "ok": true,
  "message": "PDF generated and uploaded successfully",
  "filename": "invoice.pdf",
  "url": "https://s3.amazonaws.com/bucket/path/to/file.pdf?X-Amz-...",
  "s3Key": "user123/pdfs/1234567890-abc123-invoice.pdf",
  "bucket": "your-bucket-name",
  "size": 45678,
  "expiresIn": "7 days"
}
```

---

## 📂 S3 Storage Structure

### With user_id:
```
s3://your-bucket/
└── {user_id}/
    └── pdfs/
        └── {timestamp}-{random}-{filename}.pdf
```

### Without user_id:
```
s3://your-bucket/
└── pdfs/
    └── {timestamp}-{random}-{filename}.pdf
```

---

## 🎨 Examples

### Example 1: Simple HTML Report

```bash
curl -X POST https://your-api-endpoint/dev/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<h1>Monthly Report</h1><p>Sales increased by 25%</p>",
    "filename": "monthly-report.pdf",
    "user_id": "user123"
  }'
```

### Example 2: HTML with Image

```bash
curl -X POST https://your-api-endpoint/dev/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<h1>Product Catalog</h1><img src=\"https://example.com/product.png\" style=\"max-width: 400px;\" />",
    "filename": "catalog.pdf",
    "user_id": "user123"
  }'
```

### Example 3: Markdown Document

```bash
curl -X POST https://your-api-endpoint/dev/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "markdown": "# Project Documentation\\n\\n## Features\\n\\n- Feature 1\\n- Feature 2",
    "filename": "documentation.pdf",
    "user_id": "user123"
  }'
```

### Example 4: Invoice Template

```bash
curl -X POST https://your-api-endpoint/dev/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "template": "<h1>Invoice {{invoiceNumber}}</h1><p>Client: {{clientName}}</p><p>Total: ${{total}}</p>",
    "data": {
      "invoiceNumber": "#12345",
      "clientName": "John Doe",
      "total": "1,250.00"
    },
    "filename": "invoice-12345.pdf",
    "user_id": "user123"
  }'
```

---

## 🧪 Local Testing

You can test the function locally by running:

```bash
npm start
```

This will execute the test cases included in `local_test.mjs`.

---

## 💡 Use Cases

### Business Reports
- Generate monthly/quarterly reports with charts and tables
- Executive summaries with custom branding
- Financial statements

### Invoices & Receipts
- Dynamic invoice generation from templates
- Order confirmations
- Payment receipts

### Documentation
- Convert Markdown documentation to PDF
- Technical specifications
- User manuals

### Marketing Materials
- Product catalogs with images
- Promotional flyers
- Case studies

---

## ⚙️ Technical Details

### Lambda Configuration
- **Runtime**: Node.js 20.x
- **Memory**: 1536 MB
- **Timeout**: 30 seconds
- **Architecture**: x86_64

### Dependencies
- **@sparticuz/chromium**: Chromium binary optimized for Lambda
- **puppeteer-core**: Headless browser automation
- **@aws-sdk/client-s3**: S3 operations
- **@aws-sdk/s3-request-presigner**: Generate presigned URLs
- **@aws-sdk/client-dynamodb**: DynamoDB integration
- **handlebars**: Template engine
- **marked**: Markdown parser

### IAM Permissions Required

```yaml
- s3:PutObject
- s3:GetObject
- s3:PutObjectAcl
- dynamodb:PutItem
- dynamodb:GetItem
```

---

## 🎯 Important Notes

1. **Presigned URLs**: Generated URLs expire after 7 days (AWS maximum)
2. **Images**: Support for external URLs and base64-encoded images
3. **File Size**: Lambda has a 50 MB response limit; PDFs larger than this will only be available via S3
4. **Fonts**: Custom fonts can be embedded in CSS via base64 or external URLs
5. **User Organization**: Using `user_id` helps organize PDFs by user/tenant

---

## 👥 Authors

William Ferreira, Luis Adames, Angel Moreno

## 📄 License

This project is under the MIT license.

---

**Developed for AWS Hackathon 2025** 🚀

// local_test.mjs
import dotenv from 'dotenv';

// Cargar variables de entorno ANTES de importar el handler
dotenv.config();

// Verificar que las variables de entorno se cargaron
console.log("Variables de entorno cargadas:");
console.log("  AWS_REGION:", process.env.AWS_REGION);
console.log("  S3_BUCKET_NAME:", process.env.S3_BUCKET_NAME);
console.log("  DYNAMO_DOCUMENTS_TABLE_NAME:", process.env.DYNAMO_DOCUMENTS_TABLE_NAME);
console.log();

import { handler } from "./handler.mjs";

console.log("🚀 Iniciando prueba del generador de PDF...\n");

// Prueba 1: HTML simple con imagen (con user_id)
console.log("📄 Test 1: HTML con imagen (Usuario: user123, Chat: chat001)");
const test1 = await handler({
  user_id: "user123",
  chat_id: "chat001",
  html: `
    <h1>¡Hola Mundo!</h1>
    <p>Este es un párrafo de prueba con una imagen.</p>
    <img src="https://aws-s3-images-hackaton.s3.amazonaws.com/default_user/generated_image_790558060_2.png?AWSAccessKeyId=AKIAWO23YXWVKQ5E25ZX&Signature=NacyGEwD7mbJlio6UPzjLl%2FM5Bw%3D&Expires=1760293301" 
         alt="Imagen de prueba" 
         style="max-width: 400px; height: auto;" />
    <p>Texto después de la imagen.</p>
  `,
  pdfOptions: { format: "A4", printBackground: true },
  filename: "test-html-con-imagen.pdf"
});

printResult("Test 1", test1);

// Prueba 2: Markdown (con user_id diferente)
// console.log("\n📝 Test 2: Markdown (Usuario: user456, Chat: chat002)");
// const test2 = await handler({
//   user_id: "user456",
//   chat_id: "chat002",
//   markdown: `
// # Título Principal

// Este es un **documento markdown** de prueba.

// ## Subtítulo

// - Item 1
// - Item 2
// - Item 3

// ### Código
// \`\`\`javascript
// console.log("Hola desde markdown");
// \`\`\`
//   `,
//   filename: "test-markdown.pdf"
// });

// printResult("Test 2", test2);

// Prueba 3: Template con Handlebars (sin user_id - carpeta por defecto)
console.log("\n🎨 Test 3: Template con Handlebars (Usuario: user789, Chat: chat003)");
const test3 = await handler({
  user_id: "user789",
  chat_id: "chat003",
  template: `
    <h1>{{titulo}}</h1>
    <p>Cliente: <strong>{{cliente}}</strong></p>
    <p>Fecha: {{fecha}}</p>
    <table style="width: 100%; border-collapse: collapse;">
      <thead>
        <tr style="background-color: #f0f0f0;">
          <th style="border: 1px solid #ddd; padding: 8px;">Item</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Cantidad</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Precio</th>
        </tr>
      </thead>
      <tbody>
        {{#each items}}
        <tr>
          <td style="border: 1px solid #ddd; padding: 8px;">{{nombre}}</td>
          <td style="border: 1px solid #ddd; padding: 8px;">{{cantidad}}</td>
          <td style="border: 1px solid #ddd; padding: 8px;">\${{precio}}</td>
        </tr>
        {{/each}}
      </tbody>
    </table>
    <p><strong>Total: \${{total}}</strong></p>
  `,
  data: {
    titulo: "Factura #12345",
    cliente: "Juan Pérez",
    fecha: new Date().toLocaleDateString(),
    items: [
      { nombre: "Producto A", cantidad: 2, precio: 100 },
      { nombre: "Producto B", cantidad: 1, precio: 250 },
      { nombre: "Producto C", cantidad: 5, precio: 50 }
    ],
    total: 600
  },
  filename: "test-factura-template.pdf"
});

printResult("Test 3", test3);

// Función auxiliar para imprimir resultados
function printResult(testName, response) {
  if (response.statusCode === 200) {
    const body = JSON.parse(response.body);
    console.log(`✅ ${testName} - Éxito`);
    console.log(`   🆔 Document ID: ${body.document_id}`);
    console.log(`   📁 Archivo: ${body.filename}`);
    console.log(`   📦 Tamaño: ${(body.size / 1024).toFixed(2)} KB`);
    console.log(`   🗂️  S3 Key: ${body.s3Key}`);
    console.log(`   🌐 Bucket: ${body.bucket}`);
    console.log(`   🔗 URL (expira en ${body.expiresIn}):`);
    console.log(`      ${body.url}...`);
  } else {
    const body = JSON.parse(response.body);
    console.log(`❌ ${testName} - Error`);
    console.log(`   Mensaje: ${body.message}`);
  }
}

console.log("\n✨ Pruebas completadas!");
console.log("\n💡 Los PDFs se han subido a S3. Usa los URLs generados para acceder a ellos.");

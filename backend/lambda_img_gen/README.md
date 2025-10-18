# Lambda Image Generator

Lambda function para generar imágenes usando Amazon Bedrock Nova Canvas basado en descripciones de casos de uso empresariales, con almacenamiento automático en S3.

## 🚀 Características

- ✅ Genera imágenes usando **Amazon Bedrock Nova Canvas**
- ✅ Análisis inteligente de casos de uso con **Amazon Nova Pro**
- ✅ Generación de prompts optimizados automáticamente
- ✅ Genera 3 variaciones de imágenes por solicitud
- ✅ Sube automáticamente a S3
- ✅ Genera presigned URLs válidas por 1 hora
- ✅ Organización por carpetas de usuario
- ✅ Soporte para API Gateway e invocación directa
- ✅ Imágenes de alta calidad (1024x1024 px)

## 📦 Instalación

```bash
# Instalar Serverless Framework
npm install -g serverless

# Instalar dependencias de Python (opcional para desarrollo local)
pip install -r requirements.txt
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
S3_BUCKET_NAME=tu-bucket-nombre
AWS_REGION=us-east-1
```

### Configurar Credenciales AWS

```bash
serverless config credentials --provider aws --key TU_ACCESS_KEY --secret TU_SECRET_KEY
```

## 🚀 Despliegue

```bash
serverless deploy
```

Después del despliegue, obtendrás una URL como:
```
POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/generate-image
```

## 📝 Uso

### Endpoint

```
POST https://your-api-gateway-url/generate-image
```

### Payload

```json
{
  "use_case": "A mobile app that helps users track their daily water intake and reminds them to stay hydrated.",
  "user_id": "user123"  // Opcional - default: "default_user"
}
```

### Respuesta Exitosa

```json
{
  "image_urls": [
    "https://bucket.s3.us-east-1.amazonaws.com/user123/generated_image_123456_1.png?X-Amz-Algorithm=...",
    "https://bucket.s3.us-east-1.amazonaws.com/user123/generated_image_123456_2.png?X-Amz-Algorithm=...",
    "https://bucket.s3.us-east-1.amazonaws.com/user123/generated_image_123456_3.png?X-Amz-Algorithm=..."
  ],
  "use_case": "A mobile app that helps users track their daily water intake...",
  "user_id": "user123",
  "count": 3
}
```

### Respuesta de Error

```json
{
  "error": "Missing required parameter: use_case",
  "error_type": "ValueError"
}
```

## 🗂️ Estructura en S3

```
s3://{bucket_name}/
└── {user_id}/
    └── generated_image_{seed}_{number}.png
```

Ejemplo:
```
s3://my-bucket/
└── user123/
    ├── generated_image_123456_1.png
    ├── generated_image_123456_2.png
    └── generated_image_123456_3.png
```

## 🎨 Ejemplos de Uso

### Ejemplo 1: Producto Físico

```json
{
  "use_case": "Rugged handheld device for retail shelf audits with barcode scanning and offline ERP sync capabilities.",
  "user_id": "retail_team"
}
```

### Ejemplo 2: Software Dashboard

```json
{
  "use_case": "Web application that forecasts supply chain risks with interactive scenario sliders and geospatial risk map visualization.",
  "user_id": "analytics_team"
}
```

### Ejemplo 3: IoT Device

```json
{
  "use_case": "Smart water bottle for athletes that tracks hydration levels, temperature, sends haptic reminders, and pairs with mobile app.",
  "user_id": "fitness_team"
}
```

### Ejemplo 4: Invocación Directa (Sin API Gateway)

```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

response = lambda_client.invoke(
    FunctionName='aws-lambda-image-generation-dev-generateImage',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'use_case': 'A mobile fitness tracking app',
        'user_id': 'test_user'
    })
)

result = json.loads(response['Payload'].read())
print(result['image_urls'])
```

## 🧪 Pruebas Locales

```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Ejecutar prueba local
python handler.py
```

## 🤖 Modelos de IA Utilizados

### Amazon Bedrock Nova Pro (Texto)
- **Model ID**: `amazon.nova-pro-v1:0`
- **Propósito**: Análisis de casos de uso y generación de prompts optimizados
- **Características**: 
  - Comprensión avanzada del contexto empresarial
  - Generación de prompts estructurados
  - Output en formato JSON

### Amazon Bedrock Nova Canvas (Imágenes)
- **Model ID**: `amazon.nova-canvas-v1:0`
- **Propósito**: Generación de imágenes de productos
- **Especificaciones**:
  - Resolución: 1024x1024 px
  - Calidad: Standard
  - Formato: PNG
  - Cantidad: 3 imágenes por solicitud

## 📄 Permisos IAM Requeridos

La Lambda necesita los siguientes permisos:

### Amazon Bedrock
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream",
    "bedrock:Converse",
    "bedrock:ConverseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-canvas-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"
  ]
}
```

### Amazon S3
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:PutObjectAcl",
    "s3:GetObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::your-bucket-name",
    "arn:aws:s3:::your-bucket-name/*"
  ]
}
```

### CloudWatch Logs
```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "arn:aws:logs:*:*:*"
}
```

## ⚙️ Configuración de Lambda

### Recursos
- **Memoria**: 1024 MB
- **Timeout**: 300 segundos (5 minutos)
- **Runtime**: Python 3.12
- **Architecture**: x86_64

### API Gateway
- **CORS**: Habilitado para todos los orígenes (`*`)
- **Binary Media Types**: `image/png`, `image/jpeg`, `application/json`
- **Métodos**: POST, OPTIONS

## 📚 Dependencias

```txt
boto3>=1.34.0
botocore>=1.34.0
python-dotenv>=1.0.0
```

**Nota**: `boto3` y `botocore` ya vienen incluidos en el entorno de AWS Lambda, por lo que no es necesario empaquetarlos para producción.

## 🎯 Prompt Engineering

La función utiliza un sistema de prompt engineering avanzado con:

1. **Few-shot Learning**: Ejemplos de productos físicos, dashboards y dispositivos IoT
2. **Structured Output**: Prompts y negativos en formato JSON estructurado
3. **Caption-Style Prompts**: Descripciones naturales en lugar de comandos
4. **Negative Prompts**: Exclusión de defectos de calidad, artefactos y estilos no deseados

### Anatomía de un Prompt Generado

```json
{
  "prompt": "sleek stainless smart water bottle on a gym bench, subtle LED ring near cap, condensation beads on brushed metal, phone beside it showing hydration rings, morning window light, shallow depth, three-quarter product render",
  "negativeText": "brand labels, text artifacts, extra buttons, distorted reflections, bad anatomy, harsh glare, jpeg artifacts"
}
```

## 🔒 Seguridad

- ✅ URLs pre-firmadas con expiración de 1 hora
- ✅ No requiere bucket S3 público
- ✅ Acceso temporal sin credenciales
- ✅ CORS configurado para seguridad
- ✅ Validación de parámetros de entrada

## 🚨 Limitaciones y Consideraciones

1. **Presigned URLs**: Expiran después de 1 hora
2. **Timeout**: La generación puede tardar hasta 2-3 minutos por solicitud
3. **Costos**: 
   - Amazon Bedrock cobra por tokens (texto) e imágenes generadas
   - S3 cobra por almacenamiento y transferencia
4. **Límites de Bedrock**: Consultar cuotas de servicio de AWS
5. **Región**: Los modelos Nova deben estar disponibles en la región seleccionada

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
serverless logs -f generateImage --tail
```

### CloudWatch Metrics
- Invocaciones
- Duración
- Errores
- Throttles

## 🔄 Comandos Útiles

```bash
# Ver información del deployment
serverless info

# Invocar la función directamente
serverless invoke -f generateImage --data '{"use_case":"test","user_id":"test"}'

# Ver logs
serverless logs -f generateImage

# Eliminar el deployment
serverless remove
```

## 🐛 Troubleshooting

### Error: "Missing required parameter: use_case"
- **Causa**: El payload no incluye el campo `use_case`
- **Solución**: Asegúrate de enviar el campo requerido en el body

### Error: "Failed to parse JSON from model response"
- **Causa**: El modelo Nova Pro no retornó JSON válido
- **Solución**: Revisa los prompts del sistema o intenta con un caso de uso más claro

### Error: "Access Denied" en S3
- **Causa**: La Lambda no tiene permisos para escribir en S3
- **Solución**: Verifica los permisos IAM del rol de Lambda

### Error: "Model not found"
- **Causa**: Los modelos Nova no están disponibles en la región
- **Solución**: Cambia a `us-east-1` o verifica disponibilidad regional

## 📞 Soporte

Para problemas o preguntas:
- Revisa los logs de CloudWatch
- Verifica la configuración de variables de entorno
- Confirma que los modelos Bedrock están habilitados en tu cuenta

## 👥 Autores

William Ferreira, Luis Adames, Angel Moreno

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**Desarrollado para AWS Hackathon 2025** 🚀

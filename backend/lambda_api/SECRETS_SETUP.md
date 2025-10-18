# Guía: Configurar AWS Secrets Manager

## 📋 Resumen

Este proyecto usa **AWS Secrets Manager** en producción para manejar secretos de forma segura, y archivos `.env` para desarrollo local.

---

## 🏠 Desarrollo Local (usando .env)

1. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus valores reales:
   ```bash
   ENVIRONMENT=development
   AWS_REGION=us-east-1
   DYNAMO_CHATS_TABLE_NAME=mi-tabla-chats
   # ... otros valores
   ```

3. La aplicación cargará automáticamente desde `.env`

---

## ☁️ Producción (usando AWS Secrets Manager)

### Paso 1: Crear el Secret en AWS

**Opción A: Usando AWS Console**

1. Ve a AWS Secrets Manager en la consola
2. Click en "Store a new secret"
3. Selecciona "Other type of secret"
4. En "Key/value pairs", agrega tus secretos en formato JSON o key-value:
   ```json
   {
     "AWS_REGION": "us-east-1",
     "DYNAMO_CHATS_TABLE_NAME": "prod-chats-table",
     "DYNAMO_USERS_TABLE_NAME": "prod-users-table",
     "DYNAMO_USERNAMES_TABLE_NAME": "prod-usernames-table",
     "DYNAMO_MESSAGES_TABLE_NAME": "prod-messages-table"
   }
   ```
5. Nombre del secret: `hackaton-api-secrets` (o el que definas en AWS_SECRET_NAME)
6. Configura rotación (opcional)
7. Guarda el secret

**Opción B: Usando AWS CLI**

```bash
aws secretsmanager create-secret \
    --name hackaton-api-secrets \
    --description "Secretos para la API del hackaton" \
    --secret-string '{
      "AWS_REGION": "us-east-1",
      "DYNAMO_CHATS_TABLE_NAME": "prod-chats-table",
      "DYNAMO_USERS_TABLE_NAME": "prod-users-table",
      "DYNAMO_USERNAMES_TABLE_NAME": "prod-usernames-table",
      "DYNAMO_MESSAGES_TABLE_NAME": "prod-messages-table"
    }' \
    --region us-east-1
```

### Paso 2: Configurar Permisos IAM

Tu Lambda o instancia EC2 necesita permisos para leer el secret:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:hackaton-api-secrets-*"
    }
  ]
}
```

### Paso 3: Configurar Variables de Entorno en Lambda/EC2

Solo necesitas estas dos variables de entorno:

```bash
ENVIRONMENT=production
AWS_SECRET_NAME=hackaton-api-secrets
```

La aplicación automáticamente:
- Detectará que está en producción
- Se conectará a Secrets Manager
- Cargará todos los secretos del JSON

---

## 🔄 Actualizar Secretos en Producción

**Usando AWS Console:**
1. Ve a Secrets Manager
2. Selecciona tu secret
3. Click en "Retrieve secret value"
4. Click en "Edit"
5. Modifica los valores
6. Guarda

**Usando AWS CLI:**
```bash
aws secretsmanager update-secret \
    --secret-id hackaton-api-secrets \
    --secret-string '{
      "AWS_REGION": "us-east-1",
      "DYNAMO_CHATS_TABLE_NAME": "nuevo-valor",
      ...
    }'
```

**Reinicia tu aplicación** para que cargue los nuevos valores.

---

## 🔐 Buenas Prácticas

✅ **SÍ hacer:**
- Usar Secrets Manager para producción
- Usar `.env` solo en desarrollo local
- Agregar `.env` al `.gitignore`
- Usar IAM roles con permisos mínimos necesarios
- Habilitar rotación automática de secretos cuando sea posible
- Usar diferentes secrets para dev/staging/prod

❌ **NO hacer:**
- Commitear archivos `.env` al repositorio
- Hardcodear secretos en el código
- Usar el mismo secret en múltiples entornos
- Dar permisos excesivos de IAM

---

## 🧪 Probar Localmente con Secrets Manager

Si quieres probar la carga desde Secrets Manager localmente:

1. Configura AWS CLI con credenciales válidas:
   ```bash
   aws configure
   ```

2. Cambia el `.env`:
   ```bash
   ENVIRONMENT=production
   AWS_SECRET_NAME=hackaton-api-secrets
   ```

3. Ejecuta la aplicación - cargará desde Secrets Manager

---

## 📝 Agregar Nuevos Secretos

1. Agrega el campo en `config.py` dentro de `_load_from_secrets_manager()` y `_load_from_env()`:
   ```python
   self.NEW_SECRET = secret.get('NEW_SECRET')  # en _load_from_secrets_manager
   self.NEW_SECRET = os.getenv('NEW_SECRET')   # en _load_from_env
   ```

2. Actualiza `.env.example`:
   ```bash
   NEW_SECRET=valor-ejemplo
   ```

3. Actualiza el secret en AWS Secrets Manager con el nuevo campo

---

## 💰 Costos

AWS Secrets Manager cobra:
- $0.40 por secret por mes
- $0.05 por cada 10,000 llamadas a la API

Para una API con tráfico moderado, el costo mensual suele ser < $1 USD.

---

## 🆘 Troubleshooting

**Error: "Secret not found"**
- Verifica que el nombre del secret sea correcto
- Verifica que estés en la región correcta
- Verifica los permisos IAM

**Error: "Access Denied"**
- Revisa los permisos IAM de tu Lambda/EC2
- Asegúrate de tener `secretsmanager:GetSecretValue`

**La app no carga los secretos**
- Verifica que `ENVIRONMENT=production`
- Revisa los logs de la aplicación
- Verifica la conexión de red a AWS

---

## 📚 Referencias

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Boto3 Secrets Manager](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)

# API con FastAPI + AWS Secrets Manager

API construida con FastAPI que utiliza AWS Secrets Manager para gestión segura de secretos en producción.

## 🚀 Características

- ✅ FastAPI con documentación automática
- ✅ Integración con DynamoDB
- ✅ **AWS Secrets Manager para producción**
- ✅ Variables de entorno (.env) para desarrollo
- ✅ Configuración centralizada
- ✅ CORS configurado
- ✅ Versionado de API (v1)

## 📦 Instalación

1. **Crear un entorno virtual:**
   ```powershell
   python -m venv .venv
   ```

2. **Activar el entorno virtual:**
   ```powershell
   .venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```powershell
   cp .env.example .env
   # Edita .env con tus valores reales
   ```

## 🏃 Ejecutar la aplicación

### Desarrollo Local (con .env)

```powershell
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### Producción (con AWS Secrets Manager)

Configura las variables de entorno:
```bash
export ENVIRONMENT=production
export AWS_SECRET_NAME=hackaton-api-secrets
```

Luego ejecuta normalmente. La app cargará los secretos desde AWS Secrets Manager.

📖 **[Ver guía completa de configuración de Secrets Manager](SECRETS_SETUP.md)**

## 📚 Documentación API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🗂️ Estructura del Proyecto

```
Lambda API/
├── main.py              # Punto de entrada de la aplicación
├── config.py            # ⭐ Configuración centralizada (Secrets Manager + .env)
├── requirements.txt     # Dependencias
├── .env.example         # Plantilla de variables de entorno
├── SECRETS_SETUP.md     # Guía completa de AWS Secrets Manager
└── app/
    ├── models.py        # Modelos Pydantic
    ├── dynamo.py        # Configuración de DynamoDB
    └── api/
        └── v1/
            ├── api.py   # Router principal v1
            └── chats.py # Endpoints de chats
```

## 🔐 Gestión de Secretos

Este proyecto sigue las **mejores prácticas de seguridad**:

### Desarrollo Local
- Usa archivo `.env` (nunca lo commitees)
- Variables cargadas con `python-dotenv`

### Producción
- **AWS Secrets Manager** para todos los secretos
- Detección automática del entorno
- Sin archivos `.env` en Lambda/EC2
- Rotación de secretos soportada

### Configuración

El sistema detecta automáticamente el entorno:

```python
# En desarrollo: carga desde .env
ENVIRONMENT=development

# En producción: carga desde AWS Secrets Manager
ENVIRONMENT=production
AWS_SECRET_NAME=hackaton-api-secrets
```

Ver **[SECRETS_SETUP.md](SECRETS_SETUP.md)** para instrucciones paso a paso.

## 🛠️ Endpoints Disponibles

### General
- `GET /` - Mensaje de bienvenida
- `GET /health` - Health check

### Chats (v1)
- `GET /api/v1/chats` - Listar todos los chats
- `GET /api/v1/chats/{chat_id}` - Obtener un chat específico
- `POST /api/v1/chats` - Crear un nuevo chat
- `DELETE /api/v1/chats/{chat_id}` - Eliminar un chat

## 🧪 Testing

```powershell
# Ejecutar tests (cuando los agregues)
pytest

# Con coverage
pytest --cov=app
```

## 🌐 Deploy en AWS Lambda

1. Empaqueta la aplicación
2. Configura las variables de entorno en Lambda:
   - `ENVIRONMENT=production`
   - `AWS_SECRET_NAME=hackaton-api-secrets`
3. Asegúrate de que Lambda tenga permisos IAM para Secrets Manager
4. Despliega

## 📝 Agregar Nuevos Endpoints

1. Crea un nuevo archivo en `app/api/v1/` (ej: `users.py`)
2. Define tu router:
   ```python
   from fastapi import APIRouter
   router = APIRouter()
   
   @router.get("/")
   def get_users():
       return {"users": []}
   ```
3. Registra en `app/api/v1/api.py`:
   ```python
   from app.api.v1 import chats, users
   api_router.include_router(users.router, prefix="/users")
   ```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

MIT

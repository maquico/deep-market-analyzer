from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="Mi API",
    description="API básica con FastAPI",
    version="1.0.0",
    redirect_slashes=False
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://main.d1zc9xcg5a2lei.amplifyapp.com/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Bienvenido a mi API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Handler para AWS Lambda
handler = Mangum(app)

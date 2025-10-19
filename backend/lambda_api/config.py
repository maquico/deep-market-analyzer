import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Cargar variables de entorno locales (para desarrollo)
load_dotenv()


class Config:
    """
    Configuración de la aplicación.
    En desarrollo: usa .env
    En producción: usa AWS Secrets Manager
    """
    
    def __init__(self):
        # Determinar si estamos en producción o desarrollo
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.use_secrets_manager = self.environment == "production"
        
        # Nombre del secret en AWS Secrets Manager
        self.secret_name = os.getenv("AWS_SECRET_NAME", "aws-secret-manager-api")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Cargar configuración
        if self.use_secrets_manager:
            self._load_from_secrets_manager()
        else:
            self._load_from_env()
    
    def _load_from_secrets_manager(self):
        """Cargar secretos desde AWS Secrets Manager"""
        try:
            # Crear cliente de Secrets Manager
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=self.aws_region
            )
            
            # Obtener el secret
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
            
            # Parsear el secret (JSON)
            if 'SecretString' in get_secret_value_response:
                secret = json.loads(get_secret_value_response['SecretString'])
                
                # Asignar valores a las propiedades
                self.DYNAMO_CHATS_TABLE_NAME = secret.get('DYNAMO_CHATS_TABLE_NAME')
                self.DYNAMO_USERS_TABLE_NAME = secret.get('DYNAMO_USERS_TABLE_NAME')
                self.DYNAMO_USERNAMES_TABLE_NAME = secret.get('DYNAMO_USERNAMES_TABLE_NAME')
                self.DYNAMO_MESSAGES_TABLE_NAME = secret.get('DYNAMO_MESSAGES_TABLE_NAME')
                self.DYNAMO_DOCUMENTS_TABLE_NAME = secret.get('DYNAMO_DOCUMENTS_TABLE_NAME')
                self.MEMORY_ID_BEDROCK_AGENT_CORE = secret.get('MEMORY_ID_BEDROCK_AGENT_CORE')
                self.ARN_BEDROCK_AGENTCORE = secret.get('ARN_BEDROCK_AGENTCORE')
                self.DYNAMO_IMAGES_TABLE_NAME = secret.get('DYNAMO_IMAGES_TABLE_NAME')
                self.S3_BUCKET_NAME = secret.get('S3_BUCKET_NAME')
                
                # Puedes agregar más secretos aquí
                # self.DATABASE_URL = secret.get('DATABASE_URL')
                # self.API_KEY = secret.get('API_KEY')
                
                print(f"✅ Secretos cargados desde AWS Secrets Manager: {self.secret_name}")
            else:
                raise ValueError("Secret no contiene SecretString")
                
        except Exception as e:
            raise Exception(f"Error inesperado al cargar secretos: {str(e)}")
    
    def _load_from_env(self):
        """Cargar configuración desde variables de entorno (.env)"""
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        self.DYNAMO_CHATS_TABLE_NAME = os.getenv("DYNAMO_CHATS_TABLE_NAME")
        self.DYNAMO_USERS_TABLE_NAME = os.getenv("DYNAMO_USERS_TABLE_NAME")
        self.DYNAMO_USERNAMES_TABLE_NAME = os.getenv("DYNAMO_USERNAMES_TABLE_NAME")
        self.DYNAMO_MESSAGES_TABLE_NAME = os.getenv("DYNAMO_MESSAGES_TABLE_NAME")
        self.DYNAMO_DOCUMENTS_TABLE_NAME = os.getenv("DYNAMO_DOCUMENTS_TABLE_NAME")
        self.MEMORY_ID_BEDROCK_AGENT_CORE = os.getenv("MEMORY_ID_BEDROCK_AGENT_CORE")
        self.DYNAMO_IMAGES_TABLE_NAME = os.getenv("DYNAMO_IMAGES_TABLE_NAME")
        self.ARN_BEDROCK_AGENTCORE = os.getenv("ARN_BEDROCK_AGENTCORE")
        self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
        
        print(f"📝 Configuración cargada desde variables de entorno (.env)")


# Instancia global de configuración
config = Config()

import boto3
import hashlib
import uuid
import json
import os  # Para acceder a las variables de entorno
from datetime import datetime, timedelta

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        body = event.get('body', {})  # Deserializamos el body si es un string JSON
        body = json.loads(body)  # Deserializa el body si es un string JSON

        tenant_id = body.get('tenant_id')  # Accedemos al tenant_id dentro de body
        password = body.get('password')

        if not tenant_id or not password:
            return {
                'statusCode': 400,
                'body': 'Faltan parámetros: tenant_id o password'
            }

        hashed_password = hash_password(password)

        # Cliente de DynamoDB
        dynamodb = boto3.resource('dynamodb')

        # Obtener el nombre de las tablas desde las variables de entorno
        USERS_TABLE = os.environ['TABLE_NAME_USERS']
        print("Using DynamoDB table:", USERS_TABLE)

        # Obtener usuario de la tabla
        table_users = dynamodb.Table(USERS_TABLE)
        response = table_users.get_item(Key={'tenant_id': tenant_id})

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': 'Usuario no existe'
            }

        hashed_password_bd = response['Item']['password']
        if hashed_password != hashed_password_bd:
            return {
                'statusCode': 403,
                'body': 'Contraseña incorrecta'
            }

        # Generar Token (expira en 60 minutos)
        token = str(uuid.uuid4())  # Aquí renombramos `access_token` a `token`
        token_expiry = datetime.now() + timedelta(minutes=60)

        # Generar Refresh Token (expira en 30 días)
        refresh_token = str(uuid.uuid4())
        refresh_token_expiry = datetime.now() + timedelta(days=30)

        # Obtener el nombre de la tabla de tokens desde las variables de entorno
        TOKENS_TABLE = os.environ['TABLE_NAME_TOKENS']
        print("Using DynamoDB table:", TOKENS_TABLE)

        # Guardar tokens en DynamoDB
        table_tokens = dynamodb.Table(TOKENS_TABLE)

        # Registro de Token y Refresh Token
        token_record = {
            'tenant_id': tenant_id,  # Clave de partición
            'token': token,          # Clave de clasificación (Sort Key)
            'token_expiry': token_expiry.isoformat(),
            'refresh_token': refresh_token,
            'refresh_token_expiry': refresh_token_expiry.isoformat()
        }

        table_tokens.put_item(Item=token_record)

        return {
            'statusCode': 200,
            'tenant_id': tenant_id,
            'token': token,  # Devuelve el token (antes `access_token`)
            'refresh_token': refresh_token,
            'expires_in': token_expiry.isoformat()
        }

    except Exception as e:
        print(f"Error al procesar la solicitud: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Error interno del servidor'
        }

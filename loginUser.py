import boto3
import hashlib
import uuid
import json

from datetime import datetime, timedelta

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    
    body = event.get('body', {})  # Deserializamos el body si es un string JSON
        
    tenant_id = body['tenant_id']  # Ahora accedemos al tenant_id dentro de body
    password = body['password']
    hashed_password = hash_password(password)

    dynamodb = boto3.resource('dynamodb')

    # Obtener usuario de la tabla `Pt_users`
    table_users = dynamodb.Table('Pt_users')
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
            'body': 'Password incorrecto'
        }

    # Generar Token (expira en 60 minutos)
    token = str(uuid.uuid4())  # Aquí renombramos `access_token` a `token`
    token_expiry = datetime.now() + timedelta(minutes=60)

    # Generar Refresh Token (expira en 30 días)
    refresh_token = str(uuid.uuid4())
    refresh_token_expiry = datetime.now() + timedelta(days=30)

    # Guardar tokens en DynamoDB
    table_tokens = dynamodb.Table('Pt_tokens_acceso')

    # Registro de Token y Refresh Token
    token_record = {
        'tenant_id': tenant_id,       # Clave de partición
        'token': token,               # Clave de clasificación (Sort Key)
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

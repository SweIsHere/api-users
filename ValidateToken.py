from boto3.dynamodb.conditions import Key
import boto3
import uuid
from datetime import datetime, timedelta

def lambda_handler(event, context):
    try:
        # Obtener tenant_id y token del evento
        tenant_id = event.get('tenant_id')
        token = event.get('token')

        if not tenant_id or not token:
            return {
                'statusCode': 400,
                'body': 'Faltan parámetros tenant_id o token'
            }

        dynamodb = boto3.resource('dynamodb')
        table_tokens = dynamodb.Table('Pt_tokens_acceso')

        # Buscar el token en DynamoDB
        response = table_tokens.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('token').eq(token)
        )

        # Validar si el token existe
        if not response.get('Items'):
            return {
                'statusCode': 403,
                'body': 'Token no existe'
            }

        # Extraer la información del registro
        item = response['Items'][0]
        token_expiry = item['token_expiry']
        refresh_token = item['refresh_token']
        refresh_token_expiry = item['refresh_token_expiry']

        # Validar expiración del Access Token
        now = datetime.now()
        token_expiry_dt = datetime.fromisoformat(token_expiry)

        if now > token_expiry_dt:
            # El token ha expirado, validar el Refresh Token
            refresh_token_expiry_dt = datetime.fromisoformat(refresh_token_expiry)

            if now > refresh_token_expiry_dt:
                return {
                    'statusCode': 403,
                    'body': 'Refresh Token expirado. Por favor, inicia sesión nuevamente.'
                }

            # Generar un nuevo Access Token
            new_token = str(uuid.uuid4())
            new_token_expiry = datetime.now() + timedelta(minutes=60)

            # Eliminar el registro antiguo
            table_tokens.delete_item(
                Key={
                    'tenant_id': tenant_id,
                    'token': token  # Eliminar el token actual (Sort Key)
                }
            )

            # Crear un nuevo registro con el nuevo token
            table_tokens.put_item(
                Item={
                    'tenant_id': tenant_id,
                    'token': new_token,  # Nuevo token como Sort Key
                    'token_expiry': new_token_expiry.isoformat(),
                    'refresh_token': refresh_token,
                    'refresh_token_expiry': refresh_token_expiry
                }
            )

            return {
                'statusCode': 200,
                'body': {
                    'message': 'Token renovado',
                    'new_token': new_token,
                    'expires_in': new_token_expiry.isoformat()
                }
            }

        # El token es válido
        return {
            'statusCode': 200,
            'body': 'Token válido'
        }

    except Exception as e:
        print(f"Error en ValidarTokenAcceso: {e}")
        return {
            'statusCode': 500,
            'body': 'Error interno del servidor'
        }

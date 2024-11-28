from boto3.dynamodb.conditions import Key
import boto3
import uuid
import os  # Para acceder a las variables de entorno
from datetime import datetime, timedelta

def lambda_handler(event, context):
    try:
        # Obtener tenant_id y token del evento
        tenant_id = event.get('tenant_id')
        token = event.get('token')

        # Imprimir los valores recibidos
        print(f"Recibido tenant_id: {tenant_id}, token: {token}")

        if not tenant_id or not token:
            print("Faltan parámetros tenant_id o token.")
            return {
                'statusCode': 400,
                'body': 'Faltan parámetros tenant_id o token'
            }

        table_name = os.environ['TABLE_NAME_TOKENS']
        print(f"Usando la tabla DynamoDB: {table_name}")

        # Cliente DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        # Buscar el token en DynamoDB
        print(f"Consultando DynamoDB para tenant_id: {tenant_id} y token: {token}")
        response = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('token').eq(token)
        )

        # Imprimir la respuesta de la consulta
        print(f"Respuesta de la consulta: {response}")

        # Validar si el token existe
        if not response.get('Items'):
            print(f"Token no encontrado para tenant_id: {tenant_id} y token: {token}")
            return {
                'statusCode': 403,
                'body': 'Token no existe'
            }

        # Extraer la información del registro
        item = response['Items'][0]
        print(f"Registro encontrado: {item}")

        token_expiry = item['token_expiry']
        refresh_token = item['refresh_token']
        refresh_token_expiry = item['refresh_token_expiry']

        # Validar expiración del Access Token
        now = datetime.now()
        token_expiry_dt = datetime.fromisoformat(token_expiry)

        print(f"Token expiración: {token_expiry_dt}, Fecha actual: {now}")

        if now > token_expiry_dt:
            # El token ha expirado, validar el Refresh Token
            refresh_token_expiry_dt = datetime.fromisoformat(refresh_token_expiry)
            print(f"Refresh token expiración: {refresh_token_expiry_dt}")

            if now > refresh_token_expiry_dt:
                print("Refresh token expirado.")
                return {
                    'statusCode': 403,
                    'body': 'Refresh Token expirado. Por favor, inicia sesión nuevamente.'
                }

            # Generar un nuevo Access Token
            new_token = str(uuid.uuid4())
            new_token_expiry = datetime.now() + timedelta(minutes=60)

            # Imprimir los detalles del nuevo token
            print(f"Generando nuevo token: {new_token}, expiración: {new_token_expiry}")

            # Eliminar el registro antiguo
            table.delete_item(
                Key={
                    'tenant_id': tenant_id,
                    'token': token  # Eliminar el token actual (Sort Key)
                }
            )

            # Crear un nuevo registro con el nuevo token
            table.put_item(
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
        print("Token válido.")
        return {
            'statusCode': 200,
            'body': 'Token válido'
        }

    except Exception as e:
        # Imprimir el error para ayudar en la depuración
        print(f"Error en ValidarTokenAcceso: {e}")
        return {
            'statusCode': 500,
            'body': 'Error interno del servidor'
        }

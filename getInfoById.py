import boto3
import json
from boto3.dynamodb.conditions import Key

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
USERS_TABLE = 'Pt_users'
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    try:
        body = event.get('body', {})
        # Validar encabezado Authorization
        token = event['headers']['Authorization']

        if not token:
            return {
                'statusCode': 400,
                'message': 'Falta el encabezado Authorization'
            }

       

        # Obtener tenant_id del cuerpo
        body = event.get('body', {})
        tenant_id = body.get('tenant_id')
        if not tenant_id:
            return {
                'statusCode': 400,
                'message': 'Falta el parámetro tenant_id'
            }

        lambda_client = boto3.client('lambda')

        # Crear el payload como JSON
        payload = {
            "token": token,
            "tenant_id": tenant_id
        }

        # Invocar el Lambda ValidarTokenAcceso
        invoke_response = lambda_client.invoke(
            FunctionName="ValidateToken",
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Leer la respuesta del Lambda invocado
        response = json.loads(invoke_response['Payload'].read())
        print(f"Respuesta de ValidarTokenAcceso: {response}")

        # Validar la respuesta del Lambda invocado
        if 'statusCode' not in response:
            return {
                'statusCode': 500,
                'message': 'Respuesta inválida de ValidarTokenAcceso'
            }

        if response['statusCode'] == 403:
            return {
                'statusCode': 403,
                'message': 'Forbidden - Acceso No Autorizado'
            }

        if response['statusCode'] == 401:
            return {
                'statusCode': 401,
                'message': 'Unauthorized - Token Expirado'
            }

        # Token válido, continuar con la lógica
        # Consultar DynamoDB para obtener el usuario
        dynamo_response = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id)
        )
        items = dynamo_response.get('Items', [])

        if not items:
            return {
                "statusCode": 404,
                "message": "Usuario no encontrado"
            }

        # Retornar información del usuario
        user = items[0]
        return {
            "statusCode": 200,
            "photo": user.get("photo"),
            "username": user.get("username")
        }

    except Exception as e:
        # Manejo de errores
        print(f"Error en Lambda: {e}")
        return {
            "statusCode": 500,
            "message": "Error interno del servidor",
            "error": str(e)
        }

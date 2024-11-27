import json
import boto3
import hashlib

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
USERS_TABLE = 'Pt_users'
table = dynamodb.Table(USERS_TABLE)

# Función para hashear la contraseña
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def lambda_handler(event, context):
    try:
        print(f"Evento recibido: {json.dumps(event, indent=2)}")

        # Obtener encabezados de la solicitud de manera segura
        headers = event.get('headers', {})
        token = headers.get('Authorization')
        
        if not token:
            return {
                'statusCode': 400,
                'message': 'Falta el encabezado Authorization'
            }

        # Obtener el cuerpo de la solicitud
        body = event.get('body', '{}')  # Si el body es un string JSON, lo dejamos como string


        # Obtener tenant_id del cuerpo
        tenant_id = body.get('tenant_id')
        if not tenant_id:
            return {
                'statusCode': 400,
                'message': 'Falta el parámetro tenant_id'
            }

        # Crear el cliente de Lambda para invocar el Lambda de ValidarTokenAcceso
        lambda_client = boto3.client('lambda')

        # Crear el payload como JSON para validar el token
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

        # Continuar con la lógica si el token es válido
        new_password = body.get('new_password')
        current_password = body.get('current_password')

        # Validar que los parámetros necesarios estén presentes
        if not new_password or not current_password:
            return {
                "statusCode": 400,
                "message": "Faltan parámetros: 'current_password' o 'new_password'"
            }

        # Buscar el usuario en la base de datos usando tenant_id
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('tenant_id').eq(tenant_id)
        )

        # Verificar si el usuario existe
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                "statusCode": 404,
                "message": "Usuario no encontrado"
            }

        # Obtener el primer usuario encontrado (asumimos que hay solo uno por tenant_id)
        user = response['Items'][0]

        # Verificar si la contraseña actual coincide
        if hash_password(current_password) != user['password']:
            return {
                "statusCode": 401,
                "message": "Contraseña actual incorrecta"
            }

        # Hashear la nueva contraseña
        hashed_new_password = hash_password(new_password)

        # Actualizar la contraseña del usuario
        user['password'] = hashed_new_password

        # Actualizar el registro en DynamoDB
        table.put_item(Item=user)

        return {
            "statusCode": 200,
            "message": "Contraseña actualizada exitosamente"
        }

    except Exception as e:
        # Manejo de errores
        print(f"Error al actualizar la contraseña: {e}")
        return {
            "statusCode": 500,
            "message": f"Error interno del servidor: {str(e)}"
        }

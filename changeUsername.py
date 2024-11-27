import json
import boto3

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
USERS_TABLE = 'Pt_users'
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    # Obtener el cuerpo del evento (body)
    body = event.get('body', {})  # Si el body es un string, lo deserializamos
    
    # Validar encabezado Authorization
    token = event['headers'].get('Authorization')
    if not token:
        return {
            'statusCode': 400,
            'message': 'Falta el encabezado Authorization'
        }

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
    try:
        # Extraer los datos necesarios para cambiar el username
        new_username = body.get('new_username')
        
        # Validar que los parámetros requeridos estén presentes
        if not new_username:
            return {
                "statusCode": 400,
                "message": "Falta el parámetro 'new_username'"
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
        
        # Actualizar el username del usuario
        user['username'] = new_username
        
        # Actualizar el registro en DynamoDB
        table.put_item(Item=user)
        
        return {
            "statusCode": 200,
            "message": "Username actualizado exitosamente",
            "username": new_username
        }

    except Exception as e:
        # Manejo de errores
        print(f"Error al actualizar el username: {e}")
        return {
            "statusCode": 500,
            "message": "Error interno del servidor"
        }

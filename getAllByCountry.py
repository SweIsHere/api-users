import boto3
from boto3.dynamodb.conditions import Key

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
USERS_TABLE = 'Pt_users'
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    # Obtener el valor de 'country' directamente del evento
    country = event.get('country')  # Usar directamente event.get()

    if not country:
        return {
            "statusCode": 400,
            "message": "Falta el parámetro 'country'"
        }

    # Hacer la consulta en la tabla usando el índice GSI basado en 'country'
    try:
        # Consulta usando el GSI 'country-index' para filtrar por el campo 'country'
        response = table.query(
            IndexName='country-index',  # Asegúrate de que este sea el nombre del GSI en tu tabla
            KeyConditionExpression=Key('country').eq(country)
        )

        items = response.get('Items', [])
        
        if not items:
            return {
                "statusCode": 404,
                "message": f"No se encontraron usuarios para el país {country}"
            }

        # Retornar los usuarios encontrados
        return {
            "statusCode": 200,
            "message": f"Usuarios encontrados para el país {country}",
            "users": items
        }
    
    except Exception as e:
        # Manejo de errores
        print(f"Error al consultar los usuarios: {e}")
        return {
            "statusCode": 500,
            "message": "Error interno del servidor",
            "error": str(e)
        }

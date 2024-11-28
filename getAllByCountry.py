import boto3
import os
from boto3.dynamodb.conditions import Key
import json

# Cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

# Obtener el nombre de la tabla desde las variables de entorno
USERS_TABLE = os.environ['TABLE_NAME_USERS']
table = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    try:
       
        
        body = event['body'] 

        # Obtener el valor de 'country' del cuerpo
        country = body.get('country')

        if not country:
            return {
                "statusCode": 400,
                "message": "Falta el parámetro 'country'"
            }
            
        country = country.strip().lower()

        # Hacer la consulta en la tabla usando el índice GSI basado en 'country'
        response = table.query(
            IndexName='CountryIndex',  # Usar el índice GSI definido para 'country'
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

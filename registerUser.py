import boto3
import hashlib

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función lambda que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        # Obtener el email y el password
        tenant_id = event.get('tenant_id')
        password = event.get('password')
        country = event.get('country')
        username = event.get('username')
        
        # Verificar que el tenant_id y el password existen
        if tenant_id and password:
            # Normalizar el país ingresado (convertir a minúsculas)
            country_input = country.strip().lower()

            # Si el país ingresado es vacío o contiene caracteres no válidos, retornar un error
            if not country_input.isalpha():
                mensaje = {'error': 'Invalid country, please enter a valid name'}
                return {'statusCode': 400, 'body': mensaje}

            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('Pt_users')
            # Almacena los datos del user en la tabla de usuarios en DynamoDB
            t_usuarios.put_item(
                Item={
                    'tenant_id': tenant_id,
                    'password': hashed_password,
                    'country': country_input,
                    'username': username,
                    'photo': 'default-url',  # Corrige el error tipográfico
                }
            )
            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'tenant_id': tenant_id
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing tenant_id or password'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }

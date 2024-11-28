# API Users - Proyecto Backend para la Gestión de Usuarios

Este proyecto es una API RESTful desarrollada con AWS Lambda, DynamoDB y Serverless Framework. Permite gestionar usuarios con funcionalidades de registro, login, cambio de nombre de usuario y validación de tokens de acceso.

## Estructura del Proyecto

Este repositorio contiene el código para la API de usuarios, que incluye las siguientes funcionalidades:

- **Registro de usuarios** (`POST /users/register`)
- **Login de usuarios** (`POST /users/login`)
- **Cambio de nombre de usuario** (`PATCH /users/change-username`)
- **Cambio de contraseña** (`PATCH /users/change-password`)
- **Obtención de usuarios por país** (`GET /users/getallbycountry`)
- **Obtención de usuario por `tenant_id`** (`GET /users/info`)

## Además de un lambda "Validate Token"
Donde se crear un "token" y un refres_token por cada usuario. 

## Requisitos

- **Python**
- **AWS CLI**: Debes tener configurado tu AWS CLI con las credenciales necesarias.
- **Serverless Framework**: Instala el Serverless Framework globalmente usando el siguiente comando:
  
  ```bash
  npm install -g serverless

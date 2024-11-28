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
Donde se va a  crear un "token" y un refres_token por cada usuario. 

## Tabla Users:
![image](https://github.com/user-attachments/assets/3fb009a2-02cf-485b-a507-666b8bcca8c2)

## Tabla Tokens:

![image](https://github.com/user-attachments/assets/d3091f62-7f57-460d-bd0b-b88c69598f9a)

## Requisitos

- **Python**
- **AWS CLI**: Debes tener configurado tu AWS CLI con las credenciales necesarias.
- **Serverless Framework**: Instala el Serverless Framework globalmente usando el siguiente comando:
  
  ```bash
  npm install -g serverless

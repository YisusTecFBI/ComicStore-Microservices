from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import json_util
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import jwt
import datetime
import os

# Cargamos nuestras variables de entorno
load_dotenv()
# Creamos nuestro servidor app
app = Flask(__name__)
# Especificamos el uri de conección a mongoDB
app.config['MONGO_URI'] = os.getenv('connection_uri')
# Especificamos una llave secreta
app.config['SECRET_KEY'] = os.getenv('secret_key')
# Inicializamos nuestro objeto mongoDB para poder manipular la base de datos
mongo = PyMongo(app)

# Creamos un manejador de errores
@app.errorhandler(404)
# Especificamos la función del manejador de errores
def not_found(status=404, message='Resource not found'):
    # Cremos una respuesta advirtiendo que no se encontró ningún recurso
    response = jsonify({
        'ok': False,
        'message': message,
        'status': status
    })
    # Cambiamos el estatus de código de la respuesta
    response.status_code = status
    # Retornamos la respuesta
    return response

# Creamos una ruta de tipo POST para la creación de usuarios
@app.route('/users/create', methods=['POST'])
# Creamos el método de la ruta para crear el usuario
def createUser():
    # Obtenemos los datos enviados por el usuario
    name = request.json['name']
    age = request.json['age']
    user = request.json['user']
    password = request.json['password']
    # Si los datos no son campos vacíos
    if name and age and user and password:
        # Encriptamos la contraseña
        password = generate_password_hash(password)
        # Guardamos el usuario en la base de datos
        mongo.db.users.insert_one({
            'name': name,
            'age': age,
            'user': user,
            'password': password
        })
        # Creamos una respuesta indicando que el usuario fue creado exitosamente
        response = {
            'ok': True,
            'message': 'successful create user',
            'user': {
                'name': name,
                'age': age,
                'user': user,
                'password': password
            }
        }
        # Retornamos la respuesta
        return response
    # Si algún dato no es válido retornamos el manejador de errores
    return not_found()

# Creamos una ruta de tipo POST para el login de usuario
@app.route('/users/login', methods=['POST'])
# Creamos el método de la ruta para el login de usuario
def userLogin():
    # Obtenemos los datos enviados por el usuario
    user = request.json['user']
    password = request.json['password']
    # Si los datos no son campos vacíos
    if user and password:
        # Buscamos el usuario en la base de datos
        user = mongo.db.users.find_one({'user': user})
        # Si el usuario existe
        if user:
            # Si la contraseña encriptada coincide con la contraseña especificada por el usuario
            if check_password_hash(user['password'], password):
                # Convetimos a el usuario obtenido a formato json
                user = json_util._json_convert(user)
                # Agregamos un nuevo campo llamado id
                user['id'] = user['_id']['$oid']
                # Agregamos un nuevo campo llamado token
                user['token'] = jwt.encode({'id': user['id'], 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                # Eliminamos atributos del objeto usuario
                del user['_id']
                del user['user']
                del user['password']
                # Creamos una respuesta, indicando que el usuario ha iniciado sesión exitosamente
                response =  {
                    'ok': True,
                    'message': 'successful user logued',
                    'user': user
                }
                # Retornamos la respuesta
                return response
            # Si la contraseña introducida no es válida, creamos una respuesta con dicha advertencia
            response = not_found(404, 'invalid password')
            # Retornamos la respuesta
            return response
        # Si el usuario no existe, creamos una respuesta indicando que el usuario no es válido
        response = not_found(404, 'invalid user')
        # Retornamos la respuesta
        return response
    # Si algún dato no es válido retornamos el manejador de errores
    return not_found()

# Creamos una ruta de tipo POST para la validación del Json Web Token
@app.route('/users/validateJWT', methods=['POST'])
# Creamos el método de la ruta para la validación del JWT
def validateJWT():
    # Obtenemos el token enviado
    token = request.json['token']
    # Ponemosun try si ocurre un error al decodificar el token
    try:
        # Decodificamos el token
        decodeToken = jwt.decode(
            token, app.config['SECRET_KEY'],  algorithms=["HS256"])
        # Agregamos un atributo indicando que el token fue decodificado exitosamente
        decodeToken['ok'] = True
        # Retornamos el token decodificado
        return decodeToken
    # Si ocurrió un error al decodificar
    except:
        # Creamos una respuesta indicando que el token es inválido
        response = not_found(404, 'invalid token')
        # Retornamos la respuesta
        return response

# Si el módulo se está ejecutando como programa principal
if __name__ == '__main__':
    # Corremos el servidor app en el puerto 4000 y con impresiones de debug en consola
    app.run(host='0.0.0.0', port=4000, debug=True)

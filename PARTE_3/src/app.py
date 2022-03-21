import json
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import json_util
import requests
import os
from dotenv import load_dotenv

# Cargamos nuestras variables de entorno
load_dotenv()
# Creamos nuestro servidor app
app = Flask(__name__)
# Especificamos el uri de conección a mongoDB
app.config['MONGO_URI'] = os.getenv('connection_uri')
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

# Creamos una ruta de tipo POST para la creación de un apartado
@app.route('/addToLayaway', methods=['POST'])
# Creamos el método de la ruta para la creación de un apartado
def addToLayaway():
    # Obtenemos el token del encabezado
    token = request.headers['token']
    # Obtenemos el id del comic enviado por el cliente
    idComic = request.json['idComic']
    # Creamos una respuesta, consumiento una api para la validación del token
    response = requests.post(os.getenv('api_validateJWT'), data=json.dumps(
        {'token': token}), headers={'content-type': 'application/json'})
    # Obtenemos los datos devueltos por la respuesta
    data = response.json()
    # Si la respuesta fue exitosa
    if data['ok']:
        # Guardamos el id del usuario
        idUser = data['id']
        # Creamos una respuesta, consumiento una api para obtener la lista de comics
        response = requests.get(os.getenv('api_getComics'))
        # Obtenemos los datos devueltos por la respuesta
        data = response.json()
        # Obtenemos la lista de comics
        comics = data['comics']
        # Recorremos la lista de comics
        for comic in comics:
            # Si el id del comic es igual al id del comic enviado por el cliente
            if comic['id'] == idComic:
                # Obtenemos el apartado de dicho usuario
                presentLayaway = mongo.db.layaways.find_one(
                    {'idUser': idUser})
                # Si el apartado ya existe
                if presentLayaway:
                    # Convertimos el apartado a formato json
                    layaway = json_util._json_convert(presentLayaway)
                    # Si el id del comic no se encuentra en la lista de comics apartados
                    if idComic not in layaway['comics']:
                        # Hacemos una actualización en el apartado, agregando el id del comic
                        mongo.db.layaways.update_one({'idUser': idUser}, {
                            '$push': {'comics': idComic}})
                    # Si el id del comic ya está agregado
                    else:
                        # Creamos una respuesta, indicando que el comic ya ha sido agregado
                        response = {
                            'ok': True,
                            'message': 'comic already exist in user list!'
                        }
                        # Retornamos la respuesta
                        return response
                # Si el apartado no existe
                else:
                    # Insertamos un nuevo apartado en la base de datos
                    mongo.db.layaways.insert_one({
                        'idUser': idUser,
                        'comics': [idComic]
                    })
                # Creamos una respuesta indicando que el comic ha sido agregado a la lista
                response = {
                    'ok': True,
                    'message': 'comic add in user list'
                }
                # Retornamos la respuesta
                return response
        # Si en el ciclo no se encontró el comic, creamos una respuesta indicando que el comic especificado no existe
        response = not_found(404, 'comic not exist')
        # Retornamos la respuesta
        return response
    # Si la validación del token no fue exitosa
    else:
        # Creamos una respuesta indicando que el usuario es inválido
        response = not_found(404, 'invalid user')
        # Retornamos la respuesta
        return response

# Si el módulo se está ejecutando como programa principal
if __name__ == '__main__':
    # Corremos el servidor app en el puerto 5000 y con impresiones de debug en consola
    app.run(host='0.0.0.0', port=5000, debug=True)

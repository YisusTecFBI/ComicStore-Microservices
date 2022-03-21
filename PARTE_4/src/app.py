from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from bson import json_util
import os
import jwt
import requests

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

# Creamos una ruta de tipo GET para la lectura de registros de comics apartados
@app.route('/getLayawayList', methods=['GET'])
# Creamos el método de la ruta para la lectura de registros de comics apartados
def getLayawayList():
    # Obtenemos el token del encabezado
    token = request.headers['token']
    # Ponemosun try si ocurre un error al decodificar el token
    try:
        # Decodificamos el token
        decodeToken = jwt.decode(
            token, app.config['SECRET_KEY'],  algorithms=["HS256"])
        # Guardamos el id del usuario
        idUser = decodeToken['id']
        # Obtenemos el apartado de dicho usuario
        presentLayaway = mongo.db.layaways.find_one(
                    {'idUser': idUser})
        if presentLayaway:
            # Convertimos el apartado a formato json
            layaway = json_util._json_convert(presentLayaway)
            # Obtenemos la lista de comics apartados
            idComicsLayaway = layaway['comics']
            # Creamos una respuesta, consumiento una api para obtener la lista de comics
            response = requests.get(os.getenv('api_getComics'))
            # Obtenemos los datos devueltos por la respuesta
            data = response.json()
            # Obtenemos la lista de comics
            comics = data['comics']
            # Creamos una lista de comics apartados
            comicsLayaway = []
            # Recorremos la lista de comics
            for comic in comics:
                # Si el id del comic se encuentra en la lista de ids de comics apartados
                if comic['id'] in idComicsLayaway:
                    # Agregamos el comic a la lista de apartados
                    comicsLayaway.append(comic)
            # Creamos una respuesta incluyendo la lista de comics apartados
            response = {
                'ok': True,
                'message': 'successful get comics layaway',
                'comicsLayaway': comicsLayaway
            }
            # Retornamos la respuesta
            return response
        # Creamos una respuesta indicando que aún no se ha creado un apartado
        response = not_found(404, 'layaway has not been created')
        # Retornamos la respuesta
        return response
        
    # Si ocurrió un error al decodificar
    except:
        # Creamos una respuesta indicando que el token es inválido
        response = not_found(404, 'invalid token')
        # Retornamos la respuesta
        return response

# Si el módulo se está ejecutando como programa principal
if __name__ == '__main__':
    # Corremos el servidor app en el puerto 6000 y con impresiones de debug en consola
    app.run(host='0.0.0.0', port=6000, debug=True)

from flask import Flask, request
from marvel import Marvel
import os
from dotenv import load_dotenv

# Cargamos nuestras variables de entorno
load_dotenv()
# Creamos nuestro servidor app
app = Flask(__name__)
# Importamos los datos de la api marvel pasando como parámetros la llave pública y privada
m = Marvel(os.getenv('public_key'),
           os.getenv('private_key'))

# Método para obtener los personajes formateados
def formatCharacters():
    # Obtenemos todos los personajes
    characters = m.characters.all()
    # Obtenemos los resultados de la consulta de personajes
    results = characters['data']['results']
    # Creamos una lista vacía para agregar los personajes formateados
    formatCharacters = []
    # Recorremos todos los resultados
    for result in results:
        # Agregamos a la lista un nuevo diccionario con los campos id, name, image y appearances del personaje
        formatCharacters.append({'id': result['id'],
                                 'name': result['name'],
                                 'image': result['thumbnail']['path']+'.'+result['thumbnail']['extension'],
                                 'appearances': result['comics']['available']})
    # Retornamos la lista
    return formatCharacters

# Obtener comics formateados
def formatComics():
    # Obtenemos todos los comics
    comics = m.comics.all()
    # Obtenemos los resultados de la consulta de comics
    results = comics['data']['results']
    # Creamos una lista vacía para agregar los comics formateados
    formatComics = []
    # Recorremos todos los resultados
    for result in results:
        # Agregamos a la lista un nuevo diccionario con los campos id, title, image y onSaleDate del comic
        formatComics.append({'id': result['id'],
                             'title': result['title'],
                             'image': result['thumbnail']['path']+'.'+result['thumbnail']['extension'],
                             'onSaleDate': result['dates'][0]['date']})
    # Retornamos la lista
    return formatComics

# Función para filtrar resultados
def filterBySearch(results, word, nameField):
    # Creamos una lista vacía para almacenar los resultados filtrados
    resultsFilter = []
    # Recorremos los resultados de la consulta
    for result in results:
        # Dentro de un try es posible que ocurra la excepción de index
        try:
            # Preguntamos con el método index si la palabra word se encuentra dentro del nombre del campo
            result[nameField].index(word)
            # Si index no retornó un error, quiere decir que word se encuentra dentro del nombre del campo, el resultado se agrega a la lista
            resultsFilter.append(result)
        except:
            # Si ocurrió un error no hacemos absolutamente nada
            pass
    # Retornamos la lista filtrada
    return resultsFilter

# Creamos una ruta de tipo GET para obtener los personajes
@app.route('/searchComics/getCharacters', methods=['GET'])
# Creamos el método de la ruta para obtener los personajes
def getCharacters():
    # Obtenemos la lista de personajes formateada
    characters = formatCharacters()
    # Creamos una respuesta incluyendo la lista de personajes
    response = {
        'ok': True,
        'message': 'successful get characters',
        'characters': characters
    }
    # Retornamos la respuesta
    return response

# Creamos una ruta de tipo GET para obtener los comics
@app.route('/searchComics/getComics', methods=['GET'])
# Creamos el método de la ruta para obtener los comics
def getComics():
    # Obtenemos la lista de comics formateados
    comics = formatComics()
    # Creamos una respuesta incluyendo la lista de comics
    response = {
        'ok': True,
        'message': 'successful get comics',
        'comics': comics
    }
    # Retornamos la respuesta
    return response

# Creamos una ruta de tipo POST para obtener los personajes por búsqueda
@app.route('/searchComics/charactersBySearch', methods=['POST'])
# Creamos el método de la ruta para obtener los personajes por búsqueda
def getCharactersBySearch():
    # Obtenemos la palabra enviada por el cliente
    word = request.json['word']
    # Ejecutamos el método filterBySearch para filtrar la busqueda de personajes por el campo nombre
    characters = filterBySearch(formatCharacters(), word, 'name')
    # Creamos una respuesta incluyendo la lista de personajes filtrados
    response = {
        'ok': True,
        'message': 'successful get characters by search',
        'characters': characters
    }
    # Retornamos la respuesta
    return response

# Creamos una ruta de tipo POST para obtener los comics por búsqueda
@app.route('/searchComics/getComicsBySearch', methods=['POST'])
# Creamos el método de la ruta para obtener los comics por búsqueda
def getComicsBySearch():
    # Obtenemos la palabra enviada por el cliente
    word = request.json['word']
    # Ejecutamos el método filterBySearch para filtrar la busqueda de comics por el campo title
    comics = filterBySearch(formatComics(), word, 'title')
    # Creamos una respuesta incluyendo la lista de comics filtrados
    response = {
        'ok': True,
        'message': 'successful get comics by search',
        'comics': comics
    }
    # Retornamos la respuesta
    return response


# Creamos una ruta de tipo POST para obtener los personajes y comics por búsqueda
@app.route('/searchComics/getCharactersAndComicsBySearch', methods=['POST'])
# Creamos el método de la ruta para obtener los personajes y comics por búsqueda
def getCharactersAndComicsBySearch():
    # Obtenemos la palabra enviada por el cliente
    word = request.json['word']
    # Ejecutamos el método filterBySearch para filtrar la busqueda de personajes por el campo nombre
    characters = filterBySearch(formatCharacters(), word, 'name')
    # Ejecutamos el método filterBySearch para filtrar la busqueda de comics por el campo title
    comics = filterBySearch(formatComics(), word, 'title')
    # Juntamos en una sola lista los personajes y comics
    comicsAndCharacters = characters+comics
    # Creamos una respuesta incluyendo la lista de personajes y comics filtrados
    response = {
        'ok': True,
        'message': 'successful get characters and comics by search',
        'comicsAndCharacters': comicsAndCharacters
    }
    # Retornamos la respuesta
    return response


# Si el módulo se está ejecutando como programa principal
if __name__ == '__main__':
    # Corremos el servidor app en el puerto 3000 y con impresiones de debug en consola
    app.run(host='0.0.0.0', port=3000, debug=True)

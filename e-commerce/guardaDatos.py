# docker compose run app python seed2.py


from pydantic import BaseModel, FilePath, Field, EmailStr
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from typing import Any
import requests
import os

def imprimeQuery(query):
	for x in query:
		print(x)
	
def saveImage(url, directory):
	response =requests.get(url)
	image = response.content
	name = os.path.basename(url)
	path = os.path.join(directory, name)
	with open(path, 'wb') as f:
		f.write(image)
	return name

# https://requests.readthedocs.io/en/latest/
def getProductos(api):
	response = requests.get(api)
	return response.json()
				
# Esquema de la BD
# https://docs.pydantic.dev/latest/
# con anotaciones de tipo https://docs.python.org/3/library/typing.html
# https://docs.pydantic.dev/latest/usage/fields/

class Nota(BaseModel):
	rate: float = Field(ge=0., lt=5.)
	count: int = Field(ge=1)
				
class Producto(BaseModel):
	#_id: Any
	title: str
	price: float
	description: str
	category: str
	image: str | None
	rating: Nota

class Compra(BaseModel):
	#_id: Any
	userId: int
	date: datetime
	products: list	



productos = getProductos('https://fakestoreapi.com/products')
compras = getProductos('https://fakestoreapi.com/carts')

for p in productos:
	saveImage(p.get('image'), 'imágenes')
	p.pop('id')
	producto = Producto(**p)

# Valida con el esquema:
# daría error si no corresponde algún tipo 

# Conexión con la BD				
# https://pymongo.readthedocs.io/en/stable/tutorial.html
client = MongoClient('mongo', 27017)

tienda_db = client.tienda                   # Base de Datos
productos_collection = tienda_db.productos  # Colección  		
productos_collection.drop() # reiniciar los datos
productos_collection.insert_many(productos) 


for c in compras:
	c.pop('id')
    #valida
	c = Compra(**c)

## añade a BD
compras_collection = tienda_db.compras  # Colección
compras_collection.drop() # reiniciar los datos
compras_collection.insert_many(compras) 


# docker compose run app python seed2.py


from pydantic import BaseModel, FilePath, Field, EmailStr
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from typing import Any
import requests
import os


def imprime_query(query):
	for x in query:
		print(x)

def get_quantities():
	ids_quantities = []
	compras_totales = compras_collection.find()

	for c in compras_totales:
		pc = c.get('products')
		for p in pc:
			ids_quantities.append([p.get('productId'), p.get('quantity')])
	
	return ids_quantities

def get_price_and_quantity(id):
	prod = productos_collection.find_one({"_id":lista_productos_ids[id]})
	price_prod = prod.get('price')
	category = prod.get('category')

	return price_prod, category

def calcula_facturacion():
	facturacion_total = 0

	ids_quantities = get_quantities()
	
	for id in ids_quantities:
		id_on_list = id[0]-1 # los id de los productos empiezan en 1
		
		price_prod, category = get_price_and_quantity(id_on_list)

		facturacion_total += price_prod*id[1] # Cantidad comprada por precio
	return facturacion_total
		
def facturacion_por_categoria():
	facturacion_total_categoria = {}
	categories = productos_collection.distinct("category")
	for c in categories:
		facturacion_total_categoria[c] = 0

	ids_quantities = get_quantities()

	for id in ids_quantities:
		id_on_list = id[0]-1 # los id de los productos empiezan en 1
		price_prod, category = get_price_and_quantity(id_on_list)
		facturacion_total_categoria[category] += price_prod*id[1] # Cantidad comprada por precio de cada categoria

	return facturacion_total_categoria


# Conexión con la BD				
# https://pymongo.readthedocs.io/en/stable/tutorial.html
client = MongoClient('mongo', 27017)

tienda_db = client.tienda                   # Base de Datos
productos_collection = tienda_db.productos  # Colección  
compras_collection = tienda_db.compras  # Colección


## todos los productos
lista_productos_ids = []
for prod in productos_collection.find():
	lista_productos_ids.append(prod.get('_id')) # autoinsertado por mongo
	
separacion = "---------------------------------"
###### CONSULTA
print(separacion,"\n\tElectrónica entre 100 y 200€, ordenados por precio\n")
query = {"category": "electronics", "price": {"$gt":100, "$lt":200}}
imprime_query(productos_collection.find(query,{"_id":0, "title": 1, "price": 1}).sort("price", 1))

#    Productos que contengan la palabra 'pocket' en la descripción
print(separacion,"\n\tProductos que contengan la palabra 'pocket' en la descripción\n" )
#options i -> match upper and lower cases
query2 = {"description": {"$regex" : "pocket", "$options": "i"}}
imprime_query(productos_collection.find(query2,{"_id":0, "title": 1,  "description":1}))

#    Productos con puntuación mayor de 4
print(separacion,"\n\tProductos con puntuación mayor de 4\n")
query3= {"rating.rate": {"$gt":4}}
imprime_query(productos_collection.find(query3,{"_id":0, "title": 1, "rating":1}))

#    Ropa de hombre, ordenada por puntuación
print(separacion,"\n\tProductos con puntuación mayor de 4\n")
query4={"category": "men's clothing"}
imprime_query(productos_collection.find(query4,{"_id":0, "title": 1, "category":1, "rating":1}).sort("rating.rate", 1))

#    Facturación total
print(separacion, "\n\tFacturación total\n")
facturacion_total = calcula_facturacion()
print("Facturación total: ", round(facturacion_total,2), "€")

#    Facturación por categoría de producto
print(separacion,"\n\tFacturación por categoria de producto\n")
print("Facturación por categoria: ")

pprint(facturacion_por_categoria())

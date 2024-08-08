from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import requests
import pandas as pd

app = FastAPI()

# Configura tus credenciales de la API
ACCESS_TOKEN = 'tu_access_token'

# Define una función para buscar productos en Mercado Libre
def buscar_productos(query, limit=50, offset=0):
    url = 'https://api.mercadolibre.com/sites/MLA/search'
    
    params = {
        'q': query,
        'access_token': ACCESS_TOKEN,
        'limit': limit,
        'offset': offset
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Define una función para extraer los datos y escribirlos en un DataFrame de pandas
def extraer_datos(query, total_productos):
    productos = []
    limit = 50
    for offset in range(0, total_productos, limit):
        resultados = buscar_productos(query, limit=limit, offset=offset)
        for resultado in resultados['results']:
            producto = {
                'codigo': resultado['id'],
                'nombre': resultado['title'],
                'cantidad': resultado['available_quantity'],
                'ventas': resultado['sold_quantity'],
                'precio': resultado['price']
            }
            productos.append(producto)
    return pd.DataFrame(productos)

@app.get("/consultar-productos")
async def consultar_productos():
    total_productos = 100
    query = 'https://listado.mercadolibre.com.mx/bosch_CustId_344549261_NoIndex_True#D[A:bosch,on]'
    # Extrae los datos
    df_productos = extraer_datos(query, total_productos)
    
    return 'echo'
    
    # Guarda los datos en un archivo de Excel
    archivo_excel = 'productos_mercadolibre.xlsx'
    df_productos.to_excel(archivo_excel, index=False)
    
    # Devuelve el archivo como respuesta
    return FileResponse(archivo_excel, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=archivo_excel)

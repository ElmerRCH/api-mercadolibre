from fastapi import FastAPI, Response,Request
from fastapi.responses import FileResponse
import pandas as pd
import requests

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

@app.get("/callback")
async def callback(request: Request):

    code = request.query_params.get('code')
    if not code:
        return {"error": "No code found :/"}

    # Intercambia el código por un Access Token
    url = "https://api.mercadolibre.com/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': '5981985119336238',
        'client_secret': 'UjA6P4w0a0FuNWix3lj8TN8y0VIBXo3u',
        'code': code,
        'redirect_uri': 'http://localhost:8000/callback'
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        return {"access_token": access_token}
    else:
        return {"error": "Failed to get access token", "details": response.json()}
   
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

@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'holaaa'
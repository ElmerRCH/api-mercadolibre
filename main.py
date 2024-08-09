from fastapi import FastAPI, Response,Request
from fastapi.responses import FileResponse
from util.util_api import get_model_product
import pandas as pd
import requests
import openpyxl


app = FastAPI()

# Configura tus credenciales de la API
ACCESS_TOKEN = 'APP_USR-5981985119336238-080912-1a04a9b36b2697af2620ece436ccbf4c-191633463'

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


@app.get("/productos")
async def listar_productos(query: str = "all", limit: int = 260 ):
    url = "https://api.mercadolibre.com/sites/MLM/search"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    all_products = []
    offset = 0
    while len(all_products) < limit:
        params = {
            
            "limit": 50,  # Número de resultados por página
            "offset": offset,  # Página de resultados
            "q": "urrea",  # Palabra clave de búsqueda
            "seller_id": "344549261",  # ID del vendedor
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data["results"]

            # Extraer la información relevante
            for item in results:
                #break
                all_products.append({
                   
                    #"codigo_producto": item["attributes"][-1]["value_name"] if "attributes" in item and item["attributes"] else 0,
                    "codigo_producto": get_model_product(item["attributes"]),
                    "nombre_producto": item["title"],
                    "ventas": item.get("sold_quantity", 0),
                    "precio": item["price"]
                })
               
            # Verifica si hay más resultados
            if len(results) < params["limit"]:
                break  # Salir si no hay más resultados
            
            # Incrementar el offset para la siguiente página
            offset += params["limit"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Error al consultar los productos")
        
    #break
    #return item 
    # Limitar la cantidad total de productos devueltos al límite solicitado
    productos_a_escribir = all_products[:limit]

    # Crear un archivo Excel y escribir los datos
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    # Escribir los encabezados
    headers = ["CANT.", "CODIGO", "PRODUCTO", "VENTAS", "PRECIO","P.COMP","P.COSTO"]
    ws.append(headers)

    # Escribir los datos
    for idx, producto in enumerate(productos_a_escribir, start=1):
        ws.append([
            0,
            producto["codigo_producto"],
            producto["nombre_producto"],
            producto["ventas"],
            producto["precio"],
            0,
            0,
        ])

    # Guardar el archivo Excel
    nombre_archivo = "productos.xlsx"
    wb.save(nombre_archivo)
    return item
    return {
        "cantidad":len(all_products[:limit]),
        "productos": all_products[:limit]
        }


@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'holaaa'
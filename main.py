from fastapi import FastAPI, Response,HTTPException
# from fastapi.responses import FileResponse
from util.util_api import get_model_product
from enums.api_data import Url,Paths,Excel
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
import openpyxl

app = FastAPI()

# Configura tus credenciales de la API
ACCESS_TOKEN = 'APP_USR-5981985119336238-080918-ef40c64eab38d325a50ec6e864da2a8b-191633463'
url = Url.SEARCH_PRODUCT.value
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Función para buscar precios en Mercado Libre
def buscar_precios(nombre_producto: str):
    if pd.isna(nombre_producto):
        return {"nombre_producto": nombre_producto, "precios": [{"error": "Nombre de producto vacío"}]}

    params = {
        "q": nombre_producto,
        "limit": 10  # Puedes ajustar el número de resultados
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            # Obtener los precios de los productos encontrados
            precios = [
                {
                    "nombre": item["title"],
                    "precio": item["price"],
                    "vendedor": item["seller"]["nickname"]
                }
                for item in data["results"]
            ]
        else:
            precios = [{"error": "No se encontraron productos"}]
    else:
        precios = [{"error": "Error en la solicitud a Mercado Libre"}]
    
    return {"nombre_producto": nombre_producto, "precios": precios}



def comparar_y_actualizar_precio(row):

    nombre_producto = row[Excel.NOMBRE_PRODUCTO.value]
    precio_mio = row[Excel.PRECIO.value]

    if pd.isna(nombre_producto):
        return {"error": "Nombre de producto vacío"}

    params = {
        "q": nombre_producto,
        "limit": 10  # Puedes ajustar el número de resultados
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        precios = [
            item["price"] for item in data["results"] if item["price"] < precio_mio
        ]
        
        # Actualizar la columna P.COMP según la comparación
        if precios:
            row['P.COMP'] = min(precios)  # El precio más bajo encontrado
        else:
            row['P.COMP'] = '-'  # Si no hay un precio más bajo, se pone un '-'
        
        return row
    else:
        raise HTTPException(status_code=response.status_code, detail="Error en la solicitud a Mercado Libre")



@app.get("/productos")
async def listar_productos(query: str = "all", limit: int = 260 ):

  
    all_products = []
    offset = 0
    while len(all_products) < limit:
        params = {
            
            "limit": 50,  # Número de resultados por página
            "offset": offset,  # Página de resultados
            "q": "urrea",  # Palabra clave de búsqueda
            "seller_id": "344549261",  # ID del vendedor
        }

        response = requests.get(url, headers=HEADERS, params=params)
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

    NAME_EXCEL = "URREA"

    ws.title = NAME_EXCEL
    
    # Escribir los encabezados
    headers = ["CANT.", "CODIGO", "PRODUCTO", "VENTAS", "PRECIO","P.COMP","P.COSTO"]
    ws.append(headers)

    # Escribir los datos
    for _, producto in enumerate(productos_a_escribir, start=1):
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
    nombre_archivo = f"{NAME_EXCEL}.xlsx"
    
    wb.save(f"{Paths.PATH_EXCEL.value}{nombre_archivo}")

    return item
 
@app.get("/precios")
async def comparar_precios():
    try:
        # Leer el archivo Excel
        df = pd.read_excel('data_excel/URREA.xlsx')

        # Verificar si las columnas necesarias existen
        required_columns = [Excel.NOMBRE_PRODUCTO.value, Excel.PRECIO.value,Excel.PRECIO_COMPETENCIA.value]
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"La columna '{col}' no se encuentra en el archivo Excel.")

        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(comparar_y_actualizar_precio, [row for _, row in df.iterrows()]))

        # Actualizar el DataFrame con los resultados
        df_updated = pd.DataFrame(results)

        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        df_updated.to_excel("productos_actualizados.xlsx", index=False)

        return {"status": "Archivo actualizado exitosamente", "file": "productos_actualizados.xlsx"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")
    
@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'holaaa'
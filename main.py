from fastapi import FastAPI, Response,HTTPException
# from fastapi.responses import FileResponse
from util.util_api import ExcelMLUtility
from enums.api_data import Url,Paths,Excel
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
import openpyxl
# from openpyxl.styles import NamedStyle
# import re

app = FastAPI()

# Configura tus credenciales de la API
ACCESS_TOKEN = 'APP_USR-5981985119336238-081312-7872f3192991dc898d65071aacda66a2-191633463'
url = Url.SEARCH_PRODUCT.value

HEADERS = {
    
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


MARCA = "urrea"

# Función para obtener el modelo del producto desde los atributos

@app.get("/productos")
async def listar_productos(query: str = "all", limit: int = 260 ):

    all_products = []
    offset = 0
    while len(all_products) < limit:
        params = {
            
            "limit": 50,  # Número de resultados por página
            "offset": offset,  # Página de resultados
            "q": MARCA,  # Palabra clave de búsqueda
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
                    "codigo_producto": ExcelMLUtility.get_model_product(item["attributes"]),
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

@app.get("/get-excel")
async def listar_productos( limit: int = 260):

    try:
        # Leer el archivo Excel de Mercado Libre
        df_ml = ExcelMLUtility.read_excel("data_excel/general/mercadolibre.xlsx")

        # Filtrar productos que contengan la palabra clave en su nombre
    
        productos_filtrados = df_ml[
        df_ml
        [Excel.NOMBRE_PRODUCTO_ML.value].str.contains(ExcelMLUtility.re_escape_word(),
        case=False, na=False)
        ]

        # Limitar el número de productos a 'limit'
        productos_filtrados = productos_filtrados.head(None)
        nombre_archivo = ExcelMLUtility.crate_excel(productos_filtrados)
        return {"mensaje": "Archivo Excel generado exitosamente", "ruta": nombre_archivo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@app.get("/limpiar-repetidos-nombre")
async def limpiar_repetidos():
   
    try:
       
        return {"mensaje":ExcelMLUtility.delete_data_repeat()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@app.get("/precios")
async def comparar_precios():   
    try:

       
        df = ExcelMLUtility.read_excel()
        
        # Verificar si las columnas necesarias existen
        required_columns = [

            Excel.PRECIO.value,
            Excel.NOMBRE_PRODUCTO.value,
            Excel.PRECIO_COMPETENCIA.value,
            Excel.PRECIO.value,
            Excel.CODIGO.value
        ]
        
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"La columna '{col}' no se encuentra en el archivo Excel.")

        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(ExcelMLUtility.comparar_y_actualizar_precio, [row for _, row in df.iterrows()]))

        ExcelMLUtility.update_excel(results)
        return {"status": "Archivo actualizado exitosamente", "file": "productos_actualizados.xlsx"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")


@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'holaaa'
from fastapi import FastAPI, Response,HTTPException
# from fastapi.responses import FileResponse
from util.util_api import get_model_product
from enums.api_data import Url,Paths,Excel
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
import openpyxl
from openpyxl.styles import NamedStyle

app = FastAPI()

# Configura tus credenciales de la API
ACCESS_TOKEN = 'APP_USR-5981985119336238-081012-e00c0ed3fb093f3404a6b2354e691a80-191633463  '
url = Url.SEARCH_PRODUCT.value
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


# Función para obtener el modelo del producto desde los atributos
def get_model_from_attributes(attributes):
    for attribute in attributes:
        if attribute["id"] == "MODEL":
            return attribute["value_name"]
    return None

def comparar_y_actualizar_precio(row):

    nombre_producto = row[Excel.NOMBRE_PRODUCTO.value]
    precio_mio = row[Excel.PRECIO.value]
    modelo_mio = row[Excel.CODIGO.value]
    
    if pd.isna(nombre_producto) or pd.isna(modelo_mio):
        return row

    params = {
        "q": nombre_producto,
        "limit": 10  # Puedes ajustar el número de resultados
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # Filtrar productos que contengan "urrea" en el nombre y coincidan en modelo
        productos_filtrados = [
            item for item in data["results"]
            if "urrea" in item["title"].lower() and  get_model_from_attributes(item.get("attributes", [])) == modelo_mio
        ]   
        
        # Comparar precios solo con productos filtrados
        precios = [
            item["price"] for item in productos_filtrados if item["price"] < precio_mio
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

        EXCEL = f"{Paths.PATH_EXCEL.value}URREA.xlsx"
        # Leer el archivo Excel
        df = pd.read_excel(EXCEL)

        # Verificar si las columnas necesarias existen
        required_columns = [

            Excel.PRECIO.value,
            Excel.NOMBRE_PRODUCTO.value,
            Excel.PRECIO_COMPETENCIA.value,
            Excel.PRECIO.value,Excel.CODIGO.value
        ]
        
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"La columna '{col}' no se encuentra en el archivo Excel.")

        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(comparar_y_actualizar_precio, [row for _, row in df.iterrows()]))

        # Actualizar el DataFrame con los resultados
        df_updated = pd.DataFrame(results)

        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        df_updated.to_excel(EXCEL, index=False)

        return {"status": "Archivo actualizado exitosamente", "file": "productos_actualizados.xlsx"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@app.get("/actualizar-cantidad")
async def actualizar_cantidad():
   
    # Rutas locales de los archivos Excel
    tu_excel_path = "data_excel/urrea.xlsx"
    mercadolibre_excel_path = "data_excel/mercadolibre.xlsx"
    
    # Cargar tus archivos Excel
    df_tu_excel = pd.read_excel(tu_excel_path)
    df_mercadolibre = pd.read_excel(mercadolibre_excel_path)
    
    
    # Asegurarse de que las columnas están en los DataFrames
    if 'QUANTITY' not in df_mercadolibre.columns :
        raise HTTPException(status_code=400, detail="El archivo de Mercado Libre no tiene las columnas requeridas.")
    
    if 'Código' not in df_tu_excel.columns or 'Cant.' not in df_tu_excel.columns:
        raise HTTPException(status_code=400, detail="Tu archivo Excel no tiene las columnas requeridas.")
    
    # Crear un diccionario para buscar rápidamente la cantidad según SKU
    sku_to_cantidad = dict(zip(df_mercadolibre['SKU'], df_mercadolibre['Cantidad (Obligatorio)']))
    
    # Actualizar la columna "Cant." en tu archivo Excel según el SKU
    for index, row in df_tu_excel.iterrows():
        codigo = row['Código']
        if codigo in sku_to_cantidad:
            df_tu_excel.at[index, 'Cant.'] = sku_to_cantidad[codigo]
    
    # Guardar el archivo actualizado
    output_path = "tu_excel_actualizado.xlsx"
    df_tu_excel.to_excel(output_path, index=False)

    return {"mensaje": "Archivo Excel actualizado con éxito", "archivo_guardado_en": output_path}




@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'holaaa'
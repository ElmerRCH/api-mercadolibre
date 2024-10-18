from fastapi import HTTPException,Form
from fastapi import APIRouter, HTTPException, Depends
from enums.excel import Excel
from util.util_api import ApiUtility
from util.excel_util import ExcelUtility
import httpx
import requests

router = APIRouter()

@router.get("/actualizar-inventario")
async def get_productos_vendedor():
    # URL del API de MercadoLibre para obtener los productos de un vendedor
    url = f"https://api.mercadolibre.com/sites/MLM/search?seller_id=344549261"
    
    try:
        
        # Realizar la solicitud a la API de MercadoLibre
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo algún error HTTP
        
        # Obtener los datos de la respuesta en formato JSON
        data = response.json()
        
        # Devolver los productos
        return data["results"]  # La lista de productos está en la clave "results"
    
    except requests.exceptions.RequestException as e:
        # En caso de error en la solicitud, devolvemos un error HTTP 500
        raise HTTPException(status_code=500, detail=f"Error al obtener los productos: {str(e)}")


# Función para obtener el modelo del producto desde los atributos
"""@router.get("/actualizar-inventario")
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
        
        response, params = ExcelMLUtility.get_api(offset)
        
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
"""
@router.get("/check-connection")
async def check_connection():
    
    petition = ApiUtility.check_api_connection()
    return petition

@router.get("/precios")
async def comparar_precios():

    try:
        
        # funcion necesita parametro path
        df = ExcelUtility.read_excel()
        
        # Verificar si las columnas necesarias existen   
        for col in Excel.required_columns.value:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"La columna '{col}' no se encuentra en el archivo Excel.")
        
        """ for _, row  in df.iterrows():
            
            row = ExcelMLUtility.comparar_y_actualizar_precio(row)
            break
        return"""
        
        data, path = ExcelUtility.comparar_y_actualizar_precio_poll()
        ExcelUtility.update_excel(data['row'],path)
        return {"status": "Archivo actualizado exitosamente", "file": "productos_actualizados.xlsx"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@router.post("/search-price")
async def comparar_precios(name: str = Form()):
    
    response = ApiUtility.get_api(name)
 
    if response.status_code == 200:
        data = response.json()
        
        name_imagen = ApiUtility.get_mi_product_pic(name)

        for i in data["results"]:
            return i
            print('-------------------------')
            similarity = ExcelMLUtility.search_price_for_pic(i['thumbnail'],name_imagen)
            print('similitud',similarity)   
            print(i['title'])
            print(i['price'])
            print(i['permalink'])
        # os.remove(f"{Paths.PATH_IMG.value}{name_imagen}.jpg")  
    
    return 'echo'

# para conocer vendedores de un producto
@router.post("/search-seller")
async def serach_seller(query: str):
   
    try:
       
        response = ApiUtility.get_api(query)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al consultar MercadoLibre")

        data = response.json()

        # Extraer vendedores (seller_id y nombre del vendedor)
        vendedores = []
        for item in data.get("results", []):
            vendedor_info = {
                "seller_id": item.get("seller", {}).get("id"),
                "seller_name": item.get("seller", {}).get("nickname")
            }
            if vendedor_info["seller_id"] and vendedor_info["seller_name"]:
                vendedores.append(vendedor_info)

        return {"vendedores": vendedores}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

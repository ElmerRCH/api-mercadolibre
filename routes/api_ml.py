from fastapi import HTTPException,Form
from fastapi import APIRouter, HTTPException, Depends
from enums.excel import Excel
from util.util_api import ApiUtility
from util.excel_util import ExcelUtility
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
router = APIRouter()

# TO DO agilizar
@router.get("/actualizar-inventario")
async def actualizar_inventario(query: str = "all" ):
    
    for i in ApiUtility.brands_active:
       products,brand =  ApiUtility.actualizar_inventario_ml(i)
       _  = ExcelUtility.create_excel(products,brand)     

    return 'echo'

@router.get("/img-search")
async def get_producto():
    
    product_id = 'MLM927519009'
    url_api_ml = f"https://api.mercadolibre.com/items/{product_id}"
    response = requests.get(url_api_ml)
    if response.status_code == 200:
        data = response.json()
        return data
        imagen_url = data["pictures"][0]["url"] if data.get("pictures") else data.get("thumbnail")
        return {
            "product_id": product_id,
            "name": data["title"],
            "price": data["price"],
            "imagen_url": imagen_url
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Producto no encontrado")

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

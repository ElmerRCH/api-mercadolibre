from fastapi import HTTPException,Form
from fastapi import APIRouter, HTTPException, Depends
from enums.excel import Excel
from util.util_api import ApiUtility
from util.excel_util import ExcelUtility
from concurrent.futures import ThreadPoolExecutor, as_completed

router = APIRouter()

@router.get("/actualizar-inventario")
async def listar_productos(query: str = "all", limit: int = 300 ):

    all_products = []
    offset = 0
    marca = 'bellota'
    
    while len(all_products) < limit:
        params = {
            
            "limit": 50,  # Número de resultados por página
            "offset": offset,  # Página de resultados
            "q": marca,  # Palabra clave de búsqueda
            "seller_id": "344549261",  # ID del vendedor
        }
        
        response = ApiUtility.get_api(None,True,params)
        if response.status_code == 200:
            data = response.json()
            results = data["results"]

            # Extraer la información relevante
            for item in results:
                
                link_publicacion = item.get("permalink", "Link no disponible")
                
                # excepcion necesaria para cuando api trae mal link de publicacion
                if 'unknown' == item['permalink'][len(item['permalink'])-len('unknown' ):]:
                    link_publicacion = ApiUtility.obtener_link_publicacion(item)

                all_products.append({
                    #"codigo_producto": item["attributes"][-1]["value_name"] if "attributes" in item and item["attributes"] else 0,
                    Excel.CODIGO.value: ApiUtility.get_model_product(item["attributes"]),
                    Excel.NOMBRE_PRODUCTO.value: item["title"],
                    Excel.VENTAS.value: item.get("sold_quantity", 0),
                    Excel.PRECIO.value: item["price"],
                    Excel.MI_PUBLICACION.value: link_publicacion
                })
                
            # Verifica si hay más resultados
            if len(results) < params["limit"]:
                break  # Salir si no hay más resultados
        
            # Incrementar el offset para la siguiente página
            offset += params["limit"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Error al consultar los productos")
                
    _  = ExcelUtility.create_excel(all_products[:limit],marca)  
    return 'echo'

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

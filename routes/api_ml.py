from fastapi import FastAPI, Response,HTTPException,Form
from fastapi import APIRouter, HTTPException, Depends
from enums.api_data import Excel
from util.util_api import ExcelMLUtility
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv, set_key
router = APIRouter()


@router.post("/update-tokens/")
async def update_tokens(access_token: str, refresh_token: str, response: Response):
    try:
        # Ruta al archivo .env
        env_path = ".env"
        
        # Actualizar el archivo .env con los nuevos tokens
        set_key(env_path, "ACCESS_TOKEN", access_token)
        set_key(env_path, "REFRESH_TOKEN", refresh_token)

        # Recargar las variables de entorno
        load_dotenv(dotenv_path=env_path)

        return {"message": "Tokens actualizados exitosamente"}
    
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}

"""
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

@router.get("/precios")
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
        
        """ for _, row  in df.iterrows():
            
            row = ExcelMLUtility.comparar_y_actualizar_precio(row)
        return
        """
        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(ExcelMLUtility.comparar_y_actualizar_precio, [row for _, row in df.iterrows()]))
                
        ExcelMLUtility.update_excel(results)
        return {"status": "Archivo actualizado exitosamente", "file": "productos_actualizados.xlsx"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@router.post("/search-price")
async def comparar_precios(name: str = Form()):
    
    response = ExcelMLUtility.get_api(name)
        
    if response.status_code == 200:
        data = response.json()
        name_imagen = ExcelMLUtility.get_mi_product_pic(name)
        for i in data["results"]:
            
            print('-------------------------')
            similarity = ExcelMLUtility.search_price_for_pic(i['thumbnail'],name_imagen)
            print('similitud',similarity)   
            print(i['title'])
            print(i['price'])
            print(i['permalink'])
        # os.remove(f"{Paths.PATH_IMG.value}{name_imagen}.jpg")  
        return data["results"]
    return 'echo'

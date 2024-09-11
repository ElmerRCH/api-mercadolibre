from util.util_api import ExcelMLUtility
import asyncio
import json


async def tarea_periodica():
    name_productos = ['gamo','bellota','bosch']
    data_products = []
    
    while True:
        
        data_products = map(ExcelMLUtility.get_product_up, name_productos)
        data_products = sorted(list(data_products), key=lambda x: x['productos_con_precios_altos'], reverse=True)
        
        # Paso 3: Guardar el JSON en un archivo
        with open("data_excel/data_products.json", "w") as archivo:
            archivo.write(json.dumps(data_products, indent=None))
            
        await asyncio.sleep(20)


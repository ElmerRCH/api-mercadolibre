from util.excel_util import ExcelUtility

import asyncio
import json

name_brands = ['gamo','bellota','urrea']

async def brands_data_prices():
    data_products = []
     
    while True:
        
        data_products = map(ExcelUtility.get_product_up, name_brands)
        data_products = sorted(list(data_products), key=lambda x: x['productos_con_precios_altos'], reverse=True)
        
        # Paso 3: Guardar el JSON en un archivo
        with open("data_excel/data_products.json", "w") as archivo:
            archivo.write(json.dumps(data_products, indent=None))
            
        await asyncio.sleep(20)

async def brands_all_products_data():
    
    while True:
        
        for i in name_brands:
            ExcelUtility.comparar_y_actualizar_precio_poll(i)
  
        await asyncio.sleep(100)
    
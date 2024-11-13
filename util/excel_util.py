from concurrent.futures import ThreadPoolExecutor
from util.util_api import ApiUtility
from enums.api_data import Paths,Excel
from enums.excel import ExcelStruct
from pandas import DataFrame
import pandas as pd
import openpyxl
import json
import re
import os

class ExcelUtility:
    
    def read_excel(path) -> DataFrame:
        
        return pd.read_excel(path)
    
    # Crear un nuevo archivo Excel para guardar datos
    def create_excel(productos_filtrados,brand):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = brand
        ws.append(ExcelStruct.headers.value)
        # Escribir los datos
        
        for _, producto in enumerate(productos_filtrados, start=1):
            ws.append([
                producto[Excel.PRODUCTO_ID.value],
                0,
                producto[Excel.CODIGO.value],
                producto[Excel.NOMBRE_PRODUCTO.value],
                producto[Excel.VENTAS.value],
                producto[Excel.PRECIO.value],
                0,
                0,
                producto[Excel.MI_PUBLICACION.value],
                producto[Excel.MI_URL_IMG.value]
            ])

        # Guardar el archivo Excel
        nombre_archivo = f"{brand}{Excel.TYPE_EXTENSION.value}"
        ruta_directorio = f"{Paths.PATH_EXCEL.value}{brand}"
        
        if not os.path.exists(ruta_directorio):
            os.makedirs(ruta_directorio)
            
        wb.save(f"{ruta_directorio}/{brand}{Excel.TYPE_EXTENSION.value}")

        return nombre_archivo
    
    def update_excel(results,path):

        # Actualizar el DataFrame con los resultados
        df_updated = pd.DataFrame(results)
        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        df_updated.to_excel(path, index=False)

    def re_escape_word(bread) -> str:
        return r'\b' + re.escape(bread) + r'\b'
    
    
    def get_product_up(marca=None) -> object :

        path = f"{Paths.PATH_EXCEL.value}{marca}/{marca}.json"
        productos_arriba, productos_bajo_precio = 0,0
       
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Recorre los productos en el JSON y cuenta los precios altos y bajos
        for producto in data['data']:
            precio_competencia = str(producto.get('precio_competencia', ''))

            # Normaliza los valores de precios sin definir
            if precio_competencia in ['$0,00', '-', '$ -']:
                productos_bajo_precio += 1
            else:
                productos_arriba += 1
                   
        return {
            'name':marca,
            'productos_con_precios_altos': productos_arriba,
            'productos_con_precios_bajos': productos_bajo_precio,
            'total': productos_arriba + productos_bajo_precio
            }

    
    def comparar_y_actualizar_precio_poll(brand):

        path = f"{Paths.PATH_EXCEL.value}{brand}/{brand}{Excel.TYPE_EXTENSION.value}"
        
        df = ExcelUtility.read_excel(path)
        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        
        """ for _, row in df.iterrows():
            data = ApiUtility.comparar_y_actualizar_precio(row,brand)
            break
        """
        print('brand')
        with ThreadPoolExecutor() as executor:
           data = list(executor.map(ApiUtility.comparar_y_actualizar_precio, [row for _, row in df.iterrows()],[brand] * len(df)))
        
        data = [obj for obj in data if obj]

        with open(f"data_excel/{brand}/{brand}.json", "w") as archivo:
            archivo.write(json.dumps({'marca':brand,'data':data}, indent=None))
        
        # ExcelMLUtility.update_excel(data['row'])

        return data, path
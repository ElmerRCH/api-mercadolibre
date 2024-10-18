from concurrent.futures import ThreadPoolExecutor
from util.util_api import ApiUtility
from enums.api_data import Paths,Excel

from pandas import DataFrame
import pandas as pd
import openpyxl
import json
import re

class ExcelUtility:
    
    def read_excel(path) -> DataFrame:
        
        return pd.read_excel(path)
    
    # Crear un nuevo archivo Excel para guardar datos
    def create_excel(productos_filtrados,brand):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = ApiUtility.marca
        ws.append(ApiUtility.headers)
        # Escribir los datos

        for _, row in productos_filtrados.iterrows():
            ws.append([
                row[Excel.QUANTITY_ML.value],
                row[Excel.SKU_ML.value],
                row[Excel.NOMBRE_PRODUCTO_ML.value],
                0,
                row[Excel.MARKETPLACE_PRICE.value],
                0,  # P.COMP
                0,  # P.COSTO
            ])
        
        # Guardar el archivo Excel
        nombre_archivo = f"{brand}{Excel.TYPE_EXTENSION.value}"
        wb.save(f"{Paths.PATH_EXCEL.value}{brand}/{brand}{Excel.TYPE_EXTENSION.value}")

        return nombre_archivo
    
    def update_excel(results,path):

        # Actualizar el DataFrame con los resultados
        df_updated = pd.DataFrame(results)
        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        df_updated.to_excel(path, index=False)

    def re_escape_word(bread) -> str:
        return r'\b' + re.escape(bread) + r'\b'
    
    
     # Revisar
    
    def get_product_up(marca=None) -> object :

        
        path = f"{Paths.PATH_EXCEL.value}{marca}/{marca}{Excel.TYPE_EXTENSION.value}"

        productos_arriba, productos_bajo_precio = 0,0
        df = ExcelUtility.read_excel(path)
        for _, row in df.iterrows():
            row[Excel.PRECIO_COMPETENCIA.value] = str(row[Excel.PRECIO_COMPETENCIA.value])
            
            if row[Excel.PRECIO_COMPETENCIA.value] ==  '$0,00':
                row[Excel.PRECIO_COMPETENCIA.value] = '-'
            if  row[Excel.PRECIO_COMPETENCIA.value] == '-' or  row[Excel.PRECIO_COMPETENCIA.value] == '$ -':
                productos_bajo_precio += 1
                
            else:
                productos_arriba+=1
                
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
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            data = list(executor.map(ApiUtility.comparar_y_actualizar_precio, [row for _, row in df.iterrows()],[brand] * len(df)))
        print('len data::::',len(data))
        
        data = [obj for obj in data if obj]

        with open(f"data_excel/{brand}/{brand}.json", "w") as archivo:
            archivo.write(json.dumps({'marca':brand,'data':data}, indent=None))
        
        # ExcelMLUtility.update_excel(data['row'])
             
        return data, path
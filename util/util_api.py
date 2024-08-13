import re
import requests
import pandas as pd

from enums.api_data import Url,Paths,Excel
from fastapi import HTTPException
from pandas import DataFrame
import openpyxl

class ExcelMLUtility:
    marca = "vianney"
    path = f"{Paths.PATH_EXCEL.value}{marca}/{marca}{Excel.TYPE_EXTENSION.value}"
    #orden importa
    headers = [

        Excel.CANTIDAD.value,
        Excel.CODIGO.value,
        Excel.NOMBRE_PRODUCTO.value,
        Excel.PRECIO.value,
        Excel.PRECIO_COMPETENCIA.value,
        Excel.PRECIO_COSTO.value
    ]
    
    # para limpiar de momento

    paths = [
        
        # "data_excel/surtek/surtek.xlsx",
        # "data_excel/dica/dica.xlsx",
        # "data_excel/hyundai/hyundai.xlsx",
         "data_excel/vianney/vianney.xlsx",
        # "data_excel/labomed/labomed.xlsx",
        # "data_excel/man/man.xlsx",
        # "data_excel/urrea/urrea.xlsx",
        # "data_excel/gamo/gamo.xlsx",
        # "data_excel/bosch/bosch.xlsx"
    ]

    def re_escape_word() -> str:
        return r'\b' + re.escape(ExcelMLUtility.marca) + r'\b'

    def read_excel(path = path) -> DataFrame:
        return pd.read_excel(path)
    
    def update_excel(results):

        # Actualizar el DataFrame con los resultados
        df_updated = pd.DataFrame(results)
        # Guardar el DataFrame actualizado en un nuevo archivo Excel
        df_updated.to_excel(ExcelMLUtility.path, index=False)

    # Crear un nuevo archivo Excel para guardar datos
    def crate_excel(productos_filtrados):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = ExcelMLUtility.marca
        ws.append(ExcelMLUtility.headers)
        # Escribir los datos

        for _, row in productos_filtrados.iterrows():
            ws.append([
                row[Excel.QUANTITY_ML.value],
                row[Excel.SKU_ML.value],
                row[Excel.NOMBRE_PRODUCTO_ML.value],
                row[Excel.MARKETPLACE_PRICE.value],
                0,  # P.COMP
                0,  # P.COSTO
            ])
        
        # Guardar el archivo Excel
        nombre_archivo = f"{ExcelMLUtility.marca}{Excel.TYPE_EXTENSION.value}"
        wb.save(f"{Paths.PATH_EXCEL.value}{ExcelMLUtility.marca}/{ExcelMLUtility.marca}{Excel.TYPE_EXTENSION.value}")

        return nombre_archivo

    def process_duplicates(group):
                if len(group) > 1:
                    # Si hay duplicados
                    group = group.sort_values(by=Excel.CODIGO.value, ascending=False)
                    if group[Excel.CODIGO.value].notna().any():
                        # Mantener el primero con código
                        group = group.dropna(subset=[Excel.CODIGO.value])
                    return group.head(1)
                return group
    
    def delete_data_repeat() -> str:
        
        for i in ExcelMLUtility.paths:
            # Leer el archivo Excel
            print(f"Procesando: {i}")
            df = ExcelMLUtility.read_excel(i)

            # Limpiar espacios en blanco en los nombres de productos
            df[Excel.NOMBRE_PRODUCTO.value] = df[Excel.NOMBRE_PRODUCTO.value].str.strip()

            # Identificar y eliminar productos repetidos
            
            df = df.groupby(Excel.NOMBRE_PRODUCTO.value).apply(ExcelMLUtility.process_duplicates).reset_index(drop=True)
            
            # Guardar el archivo limpio
            df.to_excel(i, index=False)

        return "echo"

    def get_model_product(produc_attributes) -> str:
        
        name_model = ""
        
        for k in produc_attributes:
            if k["id"] == "MODEL":
                name_model = k["value_name"]
                break
                    
        return name_model


    def get_model_from_attributes(attributes):
        for attribute in attributes:
            if attribute["id"] == "MODEL":
                return attribute["value_name"]
        return None

    def comparar_y_actualizar_precio(row):


        ACCESS_TOKEN = 'APP_USR-5981985119336238-081312-7872f3192991dc898d65071aacda66a2-191633463'
        url = Url.SEARCH_PRODUCT.value

        HEADERS = {
            
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }

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

            # Filtrar productos que contengan "marca" en el nombre y coincidan en modelo
            productos_filtrados = [
                item for item in data["results"]
                if ExcelMLUtility.marca in item["title"].lower() and  ExcelMLUtility.get_model_product(item.get("attributes", [])) == modelo_mio
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


    def search_price():
        return
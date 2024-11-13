import requests
import pandas as pd

from enums.api_data import Url,Paths,Excel
from fastapi import HTTPException
from PIL import Image
from io import BytesIO
import numpy as np
import hashlib
import os
import json

class ApiUtility:
    
    
    path_json_picture = 'data_excel/url_pics.json'
    brands_active =  ['gamo','bellota','urrea']
    # path = f"{Paths.PATH_EXCEL.value}{marca}/{marca}{Excel.TYPE_EXTENSION.value}"

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    url = Url.SEARCH_PRODUCT.value
    
    HEADERS = {
        
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    # orden importa para excel
    headers = [
        
        Excel.CANTIDAD.value,
        Excel.CODIGO.value,
        Excel.NOMBRE_PRODUCTO.value,
        Excel.VENTAS.value,
        Excel.PRECIO.value,
        Excel.PRECIO_COMPETENCIA.value,
        Excel.PRECIO_COSTO.value,
        Excel.MI_PUBLICACION.value
    ]
    
    # para limpiar de momento
    paths = [
        
        # "data_excel/surtek/surtek.xlsx",
        # "data_excel/dica/dica.xlsx",
        # "data_excel/hyundai/hyundai.xlsx",
        #"data_excel/vianney/vianney.xlsx",
        # "data_excel/pretul/pretul.xlsx",
        #"data_excel/foset/foset .xlsx",
        # "data_excel/volteck/volteck.xlsx",
        # "data_excel/hermex/hermex.xlsx",
        #"data_excel/fiero/fiero.xlsx",
        #"data_excel/victorinox/victorinox.xlsx",
        #"data_excel/maglite/maglite.xlsx",
        #"data_excel/jf lhabo/jf lhabo.xlsx",
        
        # "data_excel/labomed/labomed.xlsx",
        # "data_excel/man/man.xlsx",
         "data_excel/urrea/urrea.xlsx",
        # "data_excel/gamo/gamo.xlsx",
        # "data_excel/bosch/bosch.xlsx"
    ]

    def get_api(nombre_producto,get_all_products = False,params = {}):
        url = Url.SEARCH_PRODUCT.value
        
        if get_all_products is False:
            params = {
                "q": nombre_producto,
                "limit": 10
            }

        
        return requests.get(url, headers=ApiUtility.HEADERS, params=params)

    def get_model_product(produc_attributes,brand = None) -> str:
        
        name_model = ""
        
        key_searched = "MODEL" if  brand != "vianney" else "MODEL"
        for k in produc_attributes:
          
            if k["id"] == key_searched:
                name_model = k["value_name"]
                break
        
        return name_model

    def get_model_from_attributes(attributes):
        for attribute in attributes:
            if attribute["id"] == "MODEL":
                return attribute["value_name"]
        return None
    
    def get_mi_product_pic(name):
        # Parámetros para la solicitud
        params = {
            "limit": 10,  # Número de resultados por página
            "q": name,  # Palabra clave de búsqueda
            "seller_id": "344549261",  # ID del vendedor
        }
        
        # Realizar la solicitud a la API de Mercado Libre
        response = requests.get(ApiUtility.url, headers=ApiUtility.HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()

            # Procesar la primera imagen encontrada
            if data["results"]:
                first_item = data["results"][0]
                # Descargar la imagen usando la URL ya disponible
                img_response = requests.get(first_item['thumbnail'])
                img_ml = Image.open(BytesIO(img_response.content))
                name_imagen = ApiUtility.generar_nombre_hash(img_response.content)

                img_ml.save(f"{Paths.PATH_IMG.value}{name_imagen}.jpg")
                
                return name_imagen  # Devolver el primer resultado si lo necesitas
        
        return None  # En caso de fallo
    
    def process_duplicates(group):
                if len(group) > 1:
                    # Si hay duplicados

                    group = group.sort_values(by=Excel.CODIGO.value, ascending=False)
                    
                    if group[Excel.CODIGO.value].notna().any():
                        # Mantener el primero con código
                        group = group.dropna(subset=[Excel.CODIGO.value])
                    return group.head(1)
                return group
    
    def check_api_connection():
        params = {
            "q": 'Brazo Para Pared Redondo De 40cm 4550brr Dica',
            "limit": 10  # Puedes ajustar el número de resultados
        }
        response = requests.get(ApiUtility.url, headers=ApiUtility.HEADERS, params=params)
        return response.status_code
    
    # revisar
    """ def delete_data_repeat(path) -> str:
        
        for i in ExcelMLUtility.paths:
            # Leer el archivo Excel
            print(f"Procesando: {i}")
            df = ExcelMLUtility.read_excel(i)

            # Limpiar espacios en blanco en los nombres de productos
            df[Excel.NOMBRE_PRODUCTO.value] = df[Excel.NOMBRE_PRODUCTO.value].str.strip()
           
            # Identificar y eliminar productos repetidos
            df = df.groupby(Excel.NOMBRE_PRODUCTO.value).apply(ExcelMLUtility.process_duplicates).reset_index(drop=True)
            
            if ExcelMLUtility.marca == 'vianney':
                df[Excel.CODIGO.value] = df[Excel.CODIGO.value].fillna(0).astype(int)
              
            # Guardar el archivo limpio
            df.to_excel(i, index=False)

        return "echo"
    """
    def comparar_y_actualizar_precio(row,brand):

        nombre_producto = row[Excel.NOMBRE_PRODUCTO.value]
        # precio_mio = float(row[Excel.PRECIO.value].replace('$', '').replace(',', '').strip())
        precio_mio = row[Excel.PRECIO.value]
        modelo_mio = row[Excel.CODIGO.value]
        publicacion = row[Excel.MI_PUBLICACION.value]

        if pd.isna(nombre_producto) and pd.isna(modelo_mio):
            return {}

        # solo para vianney
        """ nombre_producto = (
                    nombre_producto.replace(str(int(modelo_mio)), '').strip() 
                    if brand == "vianney" else nombre_producto
        )"""
        
        # si no trae modelo se le asigna nombre de producto
        if pd.isna(modelo_mio):
            modelo_mio = nombre_producto
        
        params = {
            "q": nombre_producto,
            "limit": 10  # Puedes ajustar el número de resultados
        }
        
        response = requests.get(ApiUtility.url, headers=ApiUtility.HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            
            productos_filtrados = []
            # Filtrar productos que contengan "marca" en el nombre y coincidan en modelo
            if brand != "vianney":
                
                """for item in  data["results"]:
                    seller_id = item.get("seller", {}).get("id")
                    
                    # Excluir vendedores con los IDs 1689066639 y 771779041
                    if seller_id not in [1689066639, 771779041, 344549261]:
                        if brand in item["title"].lower():
                            if ApiUtility.get_model_product(item.get("attributes", []),brand) == modelo_mio:
                                productos_filtrados.append(item)"""

                productos_filtrados = [
                    item for item in data["results"]
                    
                    if brand in item["title"].lower() 
                    and ApiUtility.get_model_product(item.get("attributes", []), brand) == modelo_mio
                    and item.get("seller", {}).get("id") not in [1689066639,344549261, 771779041]  # Excluir vendedores
                ]
                   
            else:
                
                similarity = 0.0
                name_imagen = ApiUtility.get_mi_product_pic(nombre_producto)

                for item in data["results"]:
                    if name_imagen != None:
                       
                        similarity = ApiUtility.search_price_for_pic(item['thumbnail'],name_imagen)
                        if similarity >= 0.85 and ApiUtility.product_word_match(item["title"].lower(),nombre_producto) :
                            productos_filtrados.append(item)      
                    else:
                        
                        if ApiUtility.product_word_match(item["title"].lower(),nombre_producto):
                            productos_filtrados.append(item)
                          
            """ if len(productos_filtrados) is 0:
                print('entro..........|')
                return {}
            """
            
            precios = [
                item["price"] for item in productos_filtrados if item["price"] < precio_mio
            ]
            link_competencia = productos_filtrados[0]['permalink'] if len(productos_filtrados) != 0 else '',
            
            # Actualizar la columna P.COMP según la comparación
            if precios:
                row[Excel.PRECIO_COMPETENCIA.value] = min(precios)  # El precio más bajo encontrado
            else:
                # return {}
                row[Excel.PRECIO_COMPETENCIA.value] = '-'  # Si no hay un precio más bajo, se pone un '-'
                link_competencia = ''  # Si no hay un precio más bajo, se pone un '-'
            
            
            return {
                
                "name": row[Excel.NOMBRE_PRODUCTO.value],
                "codigo": "" if pd.isna(row[Excel.CODIGO.value]) else row[Excel.CODIGO.value],
                "precio": row[Excel.PRECIO.value],
                "precio_competencia": row[Excel.PRECIO_COMPETENCIA.value],
                # "precio_compra": 0,
                # "precio_recomendado": 0,
                "link_mi_publicacion": publicacion,
                "Link_competencia_publicacion": link_competencia,
                "url_img": row[Excel.MI_URL_IMG.value]
            }
            
        else:
            raise HTTPException(status_code=response.status_code, detail="Error en la solicitud a Mercado Libre")

    def product_word_match(str1, str2):
        # Convertir las cadenas en listas de palabras
        palabras1 = str1.lower().split()
        palabras2 = str2.lower().split()
        
        # Verificar si ambas cadenas tienen al menos 3 palabras
        if len(palabras1) < 3 or len(palabras2) < 3:
            return False
    
        # Comparar las primeras tres palabras de ambas cadenas
        return palabras1[:3] == palabras2[:3]

    def search_price_for_pic(url,name_imagen):
        response = requests.get(url)
        img_ml = Image.open(BytesIO(response.content))
        img_local = Image.open(f"{Paths.PATH_IMG.value}{name_imagen}.jpg")
        
        # Convertir ambas imágenes a escala de grises
        img_ml_gray = img_ml.convert('L')
        img_local_gray = img_local.convert('L')

        size = (256, 256)
        img_ml_gray = img_ml_gray.resize(size)
        img_local_gray = img_local_gray.resize(size)
        
        # Calcular el histograma de ambas imágenes
        hist_ml = np.array(img_ml_gray.histogram())
        hist_local = np.array(img_local_gray.histogram())

        # Comparar los histogramas usando una métrica de similitud (por ejemplo, correlación)
        similarity = np.corrcoef(hist_ml, hist_local)[0, 1]
       
        return similarity
    
    def generar_nombre_hash(imagen_bytes):
        # Crear un objeto hash MD5
        hash_md5 = hashlib.md5()
        # Actualizar el hash con el contenido de la imagen
        hash_md5.update(imagen_bytes)
        
        # Devolver el hash en formato hexadecimal como nombre de archivo
        return hash_md5.hexdigest()

    def obtener_link_publicacion(item) -> str:
        
        url = f"https://api.mercadolibre.com/items/{item['id']}"
        response = requests.get(url)
        data = response.json()
        
        # Verificar si el vendedor es el correcto
        if data['seller_id'] == 344549261:
            return data['permalink']
        else:
            return None
       
    def actualizar_inventario_ml(brand):
        limit = 300
        all_products = []
        offset = 0
        
        while len(all_products) < limit:
            params = {
                
                "limit": 50,  # Número de resultados por página
                "offset": offset,  # Página de resultados
                "q": brand,  # Palabra clave de búsqueda
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
                        Excel.PRODUCTO_ID.value: item["id"],
                        #"codigo_producto": item["attributes"][-1]["value_name"] if "attributes" in item and item["attributes"] else 0,
                        Excel.CODIGO.value: ApiUtility.get_model_product(item["attributes"]),
                        Excel.NOMBRE_PRODUCTO.value: item["title"],
                        Excel.VENTAS.value: item.get("sold_quantity", 0),
                        Excel.PRECIO.value: item["price"],
                        Excel.MI_PUBLICACION.value: link_publicacion,
                        Excel.MI_URL_IMG.value: ApiUtility.get_picture(item["id"]),
                        
                    })
                
            # Verifica si hay más resultados
            if len(results) < params["limit"]:
                break  # Salir si no hay más resultados
        
            # Incrementar el offset para la siguiente página
            offset += params["limit"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Error al consultar los productos")
           
        return  all_products[:limit],brand
         
    def get_picture(product_id) -> str:
        
        url = ''
        if not os.path.exists(ApiUtility.path_json_picture):
            url = ApiUtility.get_url_pic(product_id)

            data_products = [
                {
                    "id":product_id,
                    "url": url
                }
            ]            
            with open(ApiUtility.path_json_picture, "w") as archivo:
                archivo.write(json.dumps(data_products, indent=None))
                
        else:

            with open(ApiUtility.path_json_picture, "r") as archivo:
                datos = json.load(archivo)
            
            producto = next((item for item in datos if item["id"] == product_id), None)
            url = producto['url'] if producto is not None else ApiUtility.get_url_pic(product_id,True, datos)
            
        return url 
          
    def get_url_pic(product_id,actualizar = False,datos = []):
        
        url_api_ml = f"https://api.mercadolibre.com/items/{product_id}"
        response = requests.get(url_api_ml)

        if response.status_code == 200:
            data = response.json()
            url = data["pictures"][0]["url"] if data.get("pictures") else data.get("thumbnail")
            # para actualizar json
            if actualizar:
        
                datos.append({"id":product_id,"url": url})                
                with open(ApiUtility.path_json_picture, "w") as archivo:
                    archivo.write(json.dumps(datos, indent=None))
                    
            return url
    
        else:
            return None
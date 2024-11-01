from util.excel_util import ExcelUtility
from fastapi import APIRouter, HTTPException,Form,Response
from enums.api_data import Excel
from pydantic import BaseModel

import json

router = APIRouter()

class Producto(BaseModel):
    marca: str
    
@router.get("/get-excel")
async def listar_productos( limit: int = 260):

    try:
        # revisar
        brand = ''
        # Leer el archivo Excel de Mercado Libre
        df_ml = ExcelUtility.read_excel("data_excel/general/mercadolibre.xlsx")

        # Filtrar productos que contengan la palabra clave en su nombre
    
        productos_filtrados = df_ml[
        df_ml
        [Excel.NOMBRE_PRODUCTO_ML.value].str.contains(ExcelUtility.re_escape_word(),
        case=False, na=False)
        ]

        # Limitar el número de productos a 'limit'
        productos_filtrados = productos_filtrados.head(None)
        nombre_archivo = ExcelUtility.create_excel(productos_filtrados,brand)
        return {"mensaje": "Archivo Excel generado exitosamente", "ruta": nombre_archivo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@router.get("/productos-arriba-precio")
async def get_product_up(response: Response = Response()):
    
    with open("data_excel/data_products.json", "r") as archivo:
        datos = json.load(archivo)
    return datos

@router.post("/productos")
async def get_products(producto: Producto):

    with open(f"data_excel/{producto.marca}/{producto.marca}.json", "r") as archivo:
        datos = json.load(archivo)
    return datos

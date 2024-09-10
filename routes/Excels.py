from fastapi import FastAPI, Response,HTTPException,Form
from fastapi import APIRouter, HTTPException, Depends
from enums.api_data import Url,Paths,Excel
from util.util_api import ExcelMLUtility

router = APIRouter()

@router.get("/get-excel")
async def listar_productos( limit: int = 260):

    try:
        # Leer el archivo Excel de Mercado Libre
        df_ml = ExcelMLUtility.read_excel("data_excel/general/mercadolibre.xlsx")

        # Filtrar productos que contengan la palabra clave en su nombre
    
        productos_filtrados = df_ml[
        df_ml
        [Excel.NOMBRE_PRODUCTO_ML.value].str.contains(ExcelMLUtility.re_escape_word(),
        case=False, na=False)
        ]

        # Limitar el número de productos a 'limit'
        productos_filtrados = productos_filtrados.head(None)
        nombre_archivo = ExcelMLUtility.create_excel(productos_filtrados)
        return {"mensaje": "Archivo Excel generado exitosamente", "ruta": nombre_archivo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@router.get("/limpiar-repetidos-nombre")
async def limpiar_repetidos():
   
    try:
       
        return {"mensaje":ExcelMLUtility.delete_data_repeat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo Excel: {str(e)}")

@router.get("/productos-arriba-precio")
async def get_product_up(response: Response = Response()):
    print('entro peticion.............')
    productos_arriba = 0
    productos_bajo_precio = 0
    productos_arriba,productos_bajo_precio =  ExcelMLUtility.get_product_up()
    
    return {'productos_con_precios_altos': productos_arriba,
            'productos_con_precios_bajos': productos_bajo_precio,
            "total": productos_arriba + productos_bajo_precio
            }

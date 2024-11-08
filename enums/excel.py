from enum import Enum


class Excel(Enum):
    
    TYPE_EXTENSION = ".xlsx"
    PRODUCTO_ID = 'ID'
    CANTIDAD = "CANT."
    CODIGO = "CODIGO"
    NOMBRE_PRODUCTO = "PRODUCTO"
    VENTAS = "VENTAS"
    PRECIO = "PRECIO"
    PRECIO_COMPETENCIA = "P.COMP"
    PRECIO_COSTO = "P.COSTO"
    MI_PUBLICACION = "PUBLICACION"
    MI_URL_IMG = "IMG"

    MARKETPLACE_PRICE = "MARKETPLACE_PRICE"
    NOMBRE_PRODUCTO_ML = "TITLE"
    QUANTITY_ML = "QUANTITY"
    SKU_ML = "SKU"
    
    required_columns = [
        PRECIO,
        NOMBRE_PRODUCTO,
        PRECIO_COMPETENCIA,
        CODIGO
    ]
    
class ExcelStruct(Enum):
    
    TYPE_EXTENSION = ".xlsx"

    CANTIDAD = "CANT."
    CODIGO = "CODIGO"
    NOMBRE_PRODUCTO = "PRODUCTO"
    VENTAS = "VENTAS"
    PRECIO = "PRECIO"
    PRECIO_COMPETENCIA = "P.COMP"
    PRECIO_COSTO = "P.COSTO"
    MI_PUBLICACION = "PUBLICACION"

    MARKETPLACE_PRICE = "MARKETPLACE_PRICE"
    NOMBRE_PRODUCTO_ML = "TITLE"
    QUANTITY_ML = "QUANTITY"
    SKU_ML = "SKU"
    
    # orden importa para excel
    headers = [
        Excel.PRODUCTO_ID.value,
        Excel.CANTIDAD.value,
        Excel.CODIGO.value,
        Excel.NOMBRE_PRODUCTO.value,
        Excel.VENTAS.value,
        Excel.PRECIO.value,
        Excel.PRECIO_COMPETENCIA.value,
        Excel.PRECIO_COSTO.value,
        Excel.MI_PUBLICACION.value,
        Excel.MI_URL_IMG.value
    ]
        

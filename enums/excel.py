from enum import Enum
class Excel(Enum):
    
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
    
    required_columns = [
        PRECIO,
        NOMBRE_PRODUCTO,
        PRECIO_COMPETENCIA,
        CODIGO
    ]
        

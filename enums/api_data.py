from enum import Enum

class Url(Enum):

    SEARCH_PRODUCT = "https://api.mercadolibre.com/sites/MLM/search"

class Paths(Enum):

    PATH_EXCEL = "data_excel/"

class Excel(Enum):
    
    TYPE_EXTENSION = ".xlsx"

    CANTIDAD = "CANT."
    CODIGO = "CODIGO"
    NOMBRE_PRODUCTO = "PRODUCTO"
    VENTAS = "VENTAS"
    PRECIO = "PRECIO"
    PRECIO_COMPETENCIA = "P.COMP"
    PRECIO_COSTO = "P.COSTO"

    MARKETPLACE_PRICE = "MARKETPLACE_PRICE"
    NOMBRE_PRODUCTO_ML = "TITLE"
    QUANTITY_ML = "QUANTITY"
    SKU_ML = "SKU"

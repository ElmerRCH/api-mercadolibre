from concurrent.futures import ThreadPoolExecutor
from util.util_api import ExcelMLUtility
from enums.api_data import Paths,Excel
import json

class ExcelUtility:
    
    def comparar_y_actualizar_precio_poll(brand):

        path = f"{Paths.PATH_EXCEL.value}{brand}/{brand}{Excel.TYPE_EXTENSION.value}"
        
        df = ExcelMLUtility.read_excel(path)
        # Usar ThreadPoolExecutor para manejar el procesamiento en paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            data = list(executor.map(ExcelMLUtility.comparar_y_actualizar_precio, [row for _, row in df.iterrows()],[brand] * len(df)))

        with open(f"data_excel/{brand}/{brand}.json", "w") as archivo:
            archivo.write(json.dumps({'marca':brand,'data':data}, indent=None))
        
        # ExcelMLUtility.update_excel(data['row'])
             
        # return results
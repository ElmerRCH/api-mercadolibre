import asyncio

async def tarea_periodica():
    
    while True:
        with open("archivo.txt", "w") as archivo:
            archivo.write("Este es el contenido del archivo.\n")
        await asyncio.sleep(10)  # Intervalo de 10 segundos


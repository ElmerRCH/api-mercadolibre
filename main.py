from routes import Excels,api_ml
from fastapi import FastAPI, Response
from middlewares.token_renewal import TokenRenewalMiddleware
from fastapi.middleware.cors import CORSMiddleware
from tasks.tasks import brands_data_prices,brands_all_products_data
import asyncio
from util.excel_util import ExcelUtility

app = FastAPI()
app.add_middleware(TokenRenewalMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4500","http://localhost:4209"],  # Aquí pones la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Permite todos los headers
)

app.include_router(Excels.router, prefix="/excel", tags=["excel"])
app.include_router(api_ml.router, prefix="/api-ml", tags=["api-ml"])

@app.get("/")
async def root(response: Response = Response()):

    """name_brands = ['gamo']
    data_products = list(map(ExcelUtility.comparar_y_actualizar_precio_poll, name_brands))
    """
    return 'activo'

@app.on_event("startup")
async def iniciar_tareas_periodicas():

    # Lanza la tarea periódica cuando la aplicación inicia
    asyncio.create_task(brands_all_products_data())
    asyncio.create_task(brands_data_prices())
    


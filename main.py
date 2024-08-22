from fastapi import FastAPI, Response
from routes import Excels,api_ml

app = FastAPI()
app.include_router(api_ml.router, prefix="/api-ml", tags=["api-ml"])
app.include_router(Excels.router, prefix="/excel", tags=["excel"])

@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'activo'
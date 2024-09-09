from routes import Excels,api_ml
from fastapi import FastAPI, Response
from middlewares.token_renewal import TokenRenewalMiddleware

app = FastAPI()
app.add_middleware(TokenRenewalMiddleware)

app.include_router(Excels.router, prefix="/excel", tags=["excel"])
app.include_router(api_ml.router, prefix="/api-ml", tags=["api-ml"])

@app.get("/")
async def root(response: Response = Response()):
    response.status_code = 403
    return 'activo'
from starlette.middleware.base import BaseHTTPMiddleware
from util.token_utils import renovar_token, token_expirado

# renovación del token
class TokenRenewalMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        
        # Verificar si el token ha expirado
        if token_expirado():
            # Renueva el token usando el refresh_token
            renovar_token()
        
        # Continúa con la solicitud
        response = await call_next(request)
        return response
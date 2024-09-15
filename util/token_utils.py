import os
import time
import requests
# from dotenv import load_dotenv

expiracion_token = time.time() + 3600  # Tiempo de expiración simulado (1 hora después)

def token_expirado() -> bool:
    return time.time() > expiracion_token

def renovar_token():
    global expiracion_token
    
    url = "https://api.mercadolibre.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        
        "grant_type": "refresh_token",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "refresh_token": os.getenv("REFRESH_TOKEN")
    }
    
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        expiracion_token = time.time() + data["expires_in"]
        with open(".env", "w") as env_file:
            env_file.write(f'ACCESS_TOKEN="{access_token}"\n')
            env_file.write(f'REFRESH_TOKEN="{refresh_token}"\n')
            env_file.write(f'CLIENT_ID="{os.getenv("CLIENT_ID")}"\n')
            env_file.write(f'CLIENT_SECRET="{os.getenv("CLIENT_SECRET")}"\n')
        
        print("Token renovado exitosamente")
    else:
        print("Error al renovar el token")
        
        
    

import requests
import os

# Acceder a las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Mensaje enviado con éxito a {CHAT_ID}")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")
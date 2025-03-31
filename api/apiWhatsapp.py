import requests
import os

# Acceder a las variables de entorno
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Mensaje enviado con éxito a {to}")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")
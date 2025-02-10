import requests

# Configuración de la API de WhatsApp
WHATSAPP_TOKEN = 'EAAYPi40p2DsBOZBFLFWxDIW9ThoUVRVo0113ghDz8ZCmrSEwaZCuoA5WfwiGajojBG5IKJRyXZCnZCuN5Hukds2zYEpa3Fr77rQBbEeNm4Bw95qNqJnA4LtiXW9mZAxU0Hl7ZBZAO5Pyo7IVgB23XEBRvhmNlES06uNlI9jH2PwFzV7KmBeFa8OtSq2I4HM71QxEvwIfbZCxeMgV4gZBVZA03x5oAiAzCAbhUQGQeuMNl5RvWUZD'  # Reemplaza con tu token de acceso
PHONE_NUMBER_ID = '592489833940207'
TO_PHONE_NUMBER = '525511343686'  

def send_whatsapp_message(to, message):
    url = "https://graph.facebook.com/v21.0/592489833940207/messages"
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

if __name__ == "__main__":
    # Mensaje que deseas enviar
    mensaje = "Hola, este es un mensaje de prueba enviado desde Python."
    
    # Enviar el mensaje
    send_whatsapp_message(TO_PHONE_NUMBER, mensaje)
import requests
import os

# Acceder a las variables de entorno
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY")
MAILJET_FROM_EMAIL = os.getenv("MAILJET_FROM_EMAIL")

def enviar_email(destinatario, asunto, cuerpo):
    url = "https://api.mailjet.com/v3.1/send"
    auth = (MAILJET_API_KEY, MAILJET_SECRET_KEY)
    data = {
        "Messages": [
            {
                "From": {"Email": MAILJET_FROM_EMAIL, "Name": "Omancilla"},
                "To": [{"Email": destinatario, "Name": "Destinatario"}],
                "Subject": asunto,
                "HTMLPart": cuerpo
            }
        ]
    }
    try:
        response = requests.post(url, auth=auth, json=data)
        if response.status_code == 200:
            print(f"Correo enviado con éxito! Status code: {response.status_code}\nCorreo: {destinatario}")
        else:
            print(f"Error al enviar el correo: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")
import requests

# Configuración de Mailjet
MAILJET_API_KEY = '8f66f7959c48d59077fd01f96cc4ed93'
MAILJET_SECRET_KEY = 'a485cde5407f62fe298d533ce8892d65'
MAILJET_FROM_EMAIL = 'omarmncllav04@gmail.com'

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
            print(f"Correo enviado con éxito! Status code: {response.status_code}")
        else:
            print(f"Error al enviar el correo: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")
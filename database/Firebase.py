import firebase_admin
from firebase_admin import credentials, firestore
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Firestore:
    def __init__(self):
        # Inicializar Firebase solo una vez
        if not firebase_admin._apps:
            cred_dict = {
                "type": os.getenv("FIREBASE_TYPE"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        self.users_ref = firestore.client().collection('users')
        self.bcrypt = Bcrypt()

    def get_user(self, field, value):
        if field == "email":    
            doc = self.users_ref.document(value).get()
            return doc.to_dict() if doc.exists else None
        else:
            query = self.users_ref.where(field, '==', value).limit(1).stream()
            user = next(query, None)
            return user.to_dict() if user else None

    def create_local_user(self, usuario, email, contrasena):
        bcrypt_hash = self.bcrypt.generate_password_hash(contrasena).decode('utf-8')
        self.users_ref.document(email).set({
            'usuario': usuario.strip(),
            'email': email,
            'contrasena': bcrypt_hash,
            'auth_type': 'local',
        })

    def create_google_user(self, usuario, email, google_id):
        self.users_ref.document(email).set({
            'usuario': usuario.strip(),
            'email': email,
            'google_id': google_id,
            'auth_type': 'google',
        })

    def update_user(self, email, update_data):
        self.users_ref.document(email).update(update_data)

    def update_password(self, email, nueva_contrasena):
        bcrypt_hash = self.bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
        self.update_user(email, {'contrasena': bcrypt_hash})
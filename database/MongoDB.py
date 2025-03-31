from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from os import getenv

class MongoDB:
    def __init__(self):
        client = MongoClient(getenv("MONGODB_URI"))
        self.db = client["loginbd"]["users"]
        self.bcrypt = Bcrypt()

    def get_user(self, field, value):
        return self.db.find_one({field: value})

    def create_local_user(self, usuario, email, contrasena):
        bcrypt_hash = self.bcrypt.generate_password_hash(contrasena).decode('utf-8')
        self.db.insert_one({
            'usuario': usuario.strip(),
            'email': email,
            'contrasena': bcrypt_hash,
            'auth_type': 'local',
        })

    def create_google_user(self, usuario, email, google_id):
        self.db.insert_one({
            'usuario': usuario.strip(),
            'email': email,
            'google_id': google_id,
            'auth_type': 'google',
        })

    def update_user(self, email, update_data):
        self.db.update_one({'email': email}, {'$set': update_data})

    def update_password(self, email, nueva_contrasena):
        bcrypt_hash = self.bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
        self.db.update_one({'email': email}, {'$set': {'contrasena': bcrypt_hash}})
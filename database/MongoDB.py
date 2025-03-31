# database.py
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from os import getenv

# Inicializar MongoDB
client = MongoClient(getenv("MONGODB_URI"))
db = client["loginbd"]["users"]

# Funciones CRUD
def get_user(field, value):
    return db.find_one({field: value})

def create_local_user(usuario, email, contrasena):
    bcrypt_hash = Bcrypt().generate_password_hash(contrasena).decode('utf-8')
    db.insert_one({
        'usuario': usuario.strip(),
        'email': email,
        'contrasena': bcrypt_hash,
        'auth_type': 'local',
    })

def create_google_user(usuario, email, google_id):
    db.insert_one({
        'usuario': usuario.strip(),
        'email': email,
        'google_id': google_id,
        'auth_type': 'google',
    })

def update_user(email, update_data):
    db.update_one({'email': email}, {'$set': update_data})

def update_password(email, nueva_contrasena):
    bcrypt_hash = Bcrypt().generate_password_hash(nueva_contrasena).decode('utf-8')
    db.update_one({'email': email}, {'$set': {'contrasena': bcrypt_hash}})
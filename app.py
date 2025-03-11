from flask import Flask, request, redirect, url_for, session, flash, render_template
from flask_dance.contrib.google import google
from datetime import timedelta
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import re
import os

# Importar funciones desde la carpeta api
from api import send_whatsapp_message, enviar_email, get_blueprint

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)

# Configuración MongoDB
db = MongoClient(os.getenv("MONGODB_URI"))["loginbd"]["users"]

# Serializador para tokens
serializer = URLSafeTimedSerializer(app.secret_key, salt='password-reset-salt')

# Funciones auxiliares
def get_user(field, value):
    return db.find_one({field: value})

def create_user(usuario, email, contrasena):
    hashed = bcrypt.generate_password_hash(contrasena).decode('utf-8')
    db.insert_one({
        'usuario': usuario.strip(),
        'email': email,
        'contrasena': hashed
    })

def send_registration_notification(usuario, email):
    mensaje = f"Nuevo usuario registrado:\nUsuario: {usuario}\nCorreo: {email}"
    send_whatsapp_message("525511343686", mensaje)

# Rutas principales
@app.route('/')
def home():
    return redirect(url_for('pagina_principal') if 'usuario' in session else url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        email = request.form['email']
        contrasena = request.form['contrasena']
        
        if get_user('email', email):
            flash("El correo electrónico ya está registrado.")
            return redirect(url_for('registro'))
            
        create_user(usuario, email, contrasena)
        send_registration_notification(usuario, email)
        session.permanent = True
        session['usuario'] = usuario
        return redirect(url_for('pagina_principal'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        user = get_user('usuario', usuario)
        
        if user and bcrypt.check_password_hash(user['contrasena'], contrasena):
            session.permanent = True
            session['usuario'] = usuario
            return redirect(url_for('pagina_principal'))
            
        flash("Usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/pagina_principal')
def pagina_principal():
    if 'usuario' not in session:
        flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", "error")
        return redirect(url_for('login'))
    return render_template('index.html', usuario=session['usuario'])

@app.route('/mi_perfil')
def mi_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user = get_user('usuario', session['usuario'])
    return render_template('mi_perfil.html', usuario=user['usuario'], email=user['email'])

@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user('email', email)
        if user:
            token = serializer.dumps(email)
            enlace = url_for('restablecer_contrasena', token=token, _external=True)
            enviar_email(email, "Recuperación de contraseña", 
                        f'<a href="{enlace}">Restablecer contraseña</a>')
            flash("Te hemos enviado un correo para recuperar tu contraseña.", "success")
        else:
            flash("El correo electrónico no está registrado.", "error")
    return render_template('recuperar_contrasena.html')

@app.route('/restablecer_contrasena/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    try:
        email = serializer.loads(token, max_age=3600)
    except:
        flash("El enlace de restablecimiento ha caducado o es inválido.", "error")
        return redirect(url_for('recuperar_contrasena'))
        
    if request.method == 'POST':
        nueva_contrasena = bcrypt.generate_password_hash(
            request.form['nueva_contrasena']
        ).decode('utf-8')
        db.update_one({'email': email}, {'$set': {'contrasena': nueva_contrasena}})
        flash("Tu contraseña ha sido restablecida con éxito.", "success")
        return redirect(url_for('login'))
        
    return render_template('restablecer_contrasena.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rutas de Google OAuth
app.register_blueprint(get_blueprint(), url_prefix="/google_login")

@app.route('/login_google')
def login_google():
    return redirect(url_for('google.login'))

@app.route('/google_login/callback')
def google_login_callback():
    if not google.authorized:
        return redirect(url_for('google.login'))
        
    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
    if not resp.ok or 'email' not in resp.json():
        flash("Error al obtener información de Google. Intenta nuevamente.", "error")
        return redirect(url_for('login'))
        
    user_info = resp.json()
    user = get_user('email', user_info['email'])
    
    if not user:
        create_user(user_info.get('name', 'Usuario'), user_info['email'], '')
        session['usuario'] = user_info.get('name', 'Usuario')
    else:
        session['usuario'] = user['usuario']
        
    return redirect(url_for('pagina_principal'))

if __name__ == '__main__':
    app.run(debug=True)
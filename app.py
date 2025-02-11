from flask import Flask, request, render_template, redirect, url_for, session, flash
from datetime import timedelta
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from itsdangerous import URLSafeTimedSerializer as Serializer
import re

# Importar funciones desde la carpeta api
from api import send_whatsapp_message, enviar_email

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Clave secreta para sesiones
app.secret_key = "advpjsh"

# Configurar la duración de la sesión (1 hora)
app.permanent_session_lifetime = timedelta(hours=1)

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://omancilla:2801@cluster0.kkt0x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["loginbd"]
collection = db["users"]

# Serializador para crear y verificar tokens
serializer = Serializer(app.secret_key, salt='password-reset-salt')

# Ruta principal
@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('pagina_principal'))

# Registro de usuario
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        contrasena = request.form['contrasena']
        # Verificar si el correo ya está registrado
        if collection.find_one({'email': email}):
            flash("El correo electrónico ya está registrado.")
            return redirect(url_for('registro'))
        user = re.sub(r"\s+", "", usuario)
        # Hashear la contraseña
        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        # Insertar usuario en la base de datos
        collection.insert_one({
            'usuario': user,
            'email': email,
            'contrasena': hashed_password
        })
        session['usuario'] = usuario
        # Enviar mensaje de WhatsApp
        mensaje = f"Nuevo usuario registrado:\nUsuario: {usuario}\nCorreo: {email}"
        send_whatsapp_message("525511343686", mensaje)
        return redirect(url_for('pagina_principal'))
    return render_template('register.html')

# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        # Buscar al usuario en la base de datos
        user = collection.find_one({'usuario': usuario})
        # Verificar si las credenciales son correctas
        if user and bcrypt.check_password_hash(user['contrasena'], contrasena):
            session.permanent = True  # Marcar la sesión como permanente
            session['usuario'] = usuario
            return redirect(url_for('pagina_principal'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return render_template('login.html')
    return render_template('login.html')

# Página principal
@app.route('/pagina_principal')
def pagina_principal():
    if 'usuario' not in session:
        flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", "error")
        return redirect(url_for('login'))
    return render_template('index.html', usuario=session['usuario'])

# Mi perfil
@app.route('/mi_perfil')
def mi_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    usuario = session['usuario']
    user_data = collection.find_one({'usuario': usuario})
    return render_template('mi_perfil.html', usuario=user_data['usuario'], email=user_data['email'])

# Recuperación de contraseña
@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form['email']
        usuario = collection.find_one({'email': email})
        if usuario:
            token = serializer.dumps(email, salt='password-reset-salt')
            enlace = url_for('restablecer_contrasena', token=token, _external=True)
            asunto = "Recuperación de contraseña"
            cuerpo = f"""
            <p>Hola, hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Si no has solicitado este cambio, ignora este mensaje.</p>
            <p>Para restablecer tu contraseña, haz clic en el siguiente enlace:</p>
            <a href="{enlace}">Restablecer contraseña</a>
            """
            enviar_email(email, asunto, cuerpo)
            flash("Te hemos enviado un correo para recuperar tu contraseña.", "success")
        else:
            flash("El correo electrónico no está registrado.", "error")
    return render_template('recuperar_contrasena.html')

# Restablecer contraseña
@app.route('/restablecer_contrasena/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash("El enlace de restablecimiento ha caducado o es inválido.", "error")
        return redirect(url_for('recuperar_contrasena'))
    if request.method == 'POST':
        nueva_contrasena = request.form['nueva_contrasena']
        hashed_password = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
        collection.update_one({'email': email}, {'$set': {'contrasena': hashed_password}})
        flash("Tu contraseña ha sido restablecida con éxito.", "success")
        return redirect(url_for('login'))
    return render_template('restablecer_contrasena.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
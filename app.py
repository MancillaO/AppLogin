from flask import Flask, request, redirect, url_for, session, flash, render_template
from flask_dance.contrib.google import google
from datetime import timedelta
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
import os

# Importar funciones desde la carpeta api
from api import send_telegram_message, enviar_email, get_blueprint
from database import get_user, create_local_user, create_google_user, update_user, update_password

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)

# Serializador para tokens
serializer = URLSafeTimedSerializer(app.secret_key, salt='password-reset-salt')

def send_registration_notification(usuario, email):
    message = (
        f"📢 Nuevo Registro de Usuario 📢\n\n"
        f"👤 Usuario: {usuario}\n"
        f"📧 Correo Electrónico: {email}\n\n"
        "✅ ¡Revisa el panel de administración para más detalles!"
    )
    # send_whatsapp_message("525511343686", message)
    send_telegram_message(message)

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
            
        create_local_user(usuario, email, contrasena)
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
        
        if user and user.get('auth_type') == 'local' and bcrypt.check_password_hash(user['contrasena'], contrasena):
            session.permanent = True
            session['usuario'] = usuario
            return redirect(url_for('pagina_principal'))
        elif user and user.get('auth_type') == 'google':
            flash("Este usuario se registró con Google. Por favor, usa el botón de inicio de sesión con Google.")
            return redirect(url_for('login'))
            
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
            # Verificar si es un usuario local antes de enviar el correo
            if user.get('auth_type') == 'google':
                flash("Este correo está registrado con Google. Por favor, usa el botón de inicio de sesión con Google.", "error")
                return redirect(url_for('login'))
                
            token = serializer.dumps(email)
            enlace = url_for('restablecer_contrasena', token=token, _external=True)
            
            # Leer la plantilla HTML
            with open('templates/email/correoRecuperacion.html', 'r', encoding='utf-8') as file:
                template = file.read()
            
            # Reemplazar el enlace en la plantilla
            mensaje_html = template.replace('{enlace}', enlace)
            
            # Enviar el correo con el HTML
            enviar_email(
                email, 
                "Recuperación de contraseña", 
                mensaje_html
            )
            
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
        
    user = get_user('email', email)
    if not user or user.get('auth_type') == 'google':
        flash("No se puede restablecer la contraseña para este usuario.", "error")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        nueva_contrasena = bcrypt.generate_password_hash(
            request.form['nueva_contrasena']
        ).decode('utf-8')
        update_password(email, request.form['nueva_contrasena'])
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
    email = user_info['email']
    user = get_user('email', email)
    
    if not user:
        # Crear nuevo usuario de Google
        google_id = user_info.get('sub')  # ID único de Google
        usuario = user_info.get('name', 'Usuario Google')
        create_google_user(usuario, email, google_id)
        send_registration_notification(usuario, email)
        session['usuario'] = usuario
    else:
        # Usuario existente
        if user.get('auth_type') == 'local':
            # Convertir usuario local a Google si coincide el email
            update_user(email, {'auth_type': 'google', 'google_id': user_info.get('sub')})
        session['usuario'] = user['usuario']
        
    session.permanent = True
    return redirect(url_for('pagina_principal'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(ssl_context='adhoc', debug=True)
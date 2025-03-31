from flask_dance.contrib.google import make_google_blueprint
import os

def get_blueprint():
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to='google_login_callback',
        scope=[
            "openid", 
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
    )
    return google_bp
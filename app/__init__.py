from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import openai
import os
from dotenv import load_dotenv
from flask_talisman import Talisman
import logging
from logging.handlers import RotatingFileHandler

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja aplikacji
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "domyślny_sekret")  # Klucz wczytany z .env
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Tworzenie obiektów rozszerzeń Flask bez ich inicjalizacji
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Funkcja ładująca użytkownika dla Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import w funkcji, aby uniknąć circular import
    return User.query.get(int(user_id))

# Inicjalizacja rozszerzeń z aplikacją
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)

# Konfiguracja Flask-Login
login_manager.login_view = 'login'  # Strona logowania
login_manager.login_message_category = 'info'

# Kontekst globalny dla szablonów
@app.context_processor
def utility_processor():
    return dict(enumerate=enumerate)

# Konfiguracja logowania błędów (tylko w trybie produkcyjnym)
if not app.debug:
    handler = RotatingFileHandler("error.log", maxBytes=10000, backupCount=3)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

# Inicjalizacja klucza API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Klucz wczytany z .env

# Konfiguracja folderu przesyłania
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Upewnij się, że folder istnieje
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Importowanie tras na końcu, aby uniknąć circular import
from app import routes
from app import training_routes  # noqa: F401 — rejestracja tras dziennika treningowego

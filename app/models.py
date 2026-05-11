from app import db, login_manager, bcrypt
from flask_login import UserMixin
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash


# Funkcja Flask-Login do ładowania użytkownika
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ✅ **Model użytkownika**
class User(db.Model, UserMixin):
    id_user = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(Enum('K', 'M', name='gender_enum'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    id_role = db.Column(db.Integer, db.ForeignKey('role.id_role'), nullable=False)
    role = db.relationship('Role', backref='users')

    club_id = db.Column(db.Integer, db.ForeignKey('club.id_club'), nullable=False)
    club = db.relationship('Club', backref='members')

    def set_password(self, password):
        """Hashowanie hasła"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Sprawdzanie poprawności hasła"""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Metoda wymagana przez Flask-Login do pobierania ID użytkownika"""
        return str(self.id_user)


# ✅ **Role użytkowników**
class Role(db.Model):
    id_role = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)


# ✅ **Kluby**
class Club(db.Model):
    id_club = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(120), nullable=False)
    club_city = db.Column(db.String(50), nullable=False)


# ✅ **Zawody**
class Competition(db.Model):
    id_competition = db.Column(db.Integer, primary_key=True)
    competition_name = db.Column(db.String(120), nullable=False)
    competition_city = db.Column(db.String(120), nullable=False)
    competition_date = db.Column(db.Date, nullable=False)
    id_club = db.Column(db.Integer, db.ForeignKey('club.id_club'), nullable=True)  # ✅ Nowa kolumna
    club = db.relationship('Club', backref='competitions')


# ✅ **Style pływackie**
class SwimmingStyle(db.Model):
    id_style = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Integer, nullable=False)
    style_name = db.Column(db.String(50), nullable=False)

    results = db.relationship('Result', backref='results_for_style', lazy=True, overlaps="swimming_style")


# ✅ **Wyniki zawodów**
class Result(db.Model):
    id_result = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    user = db.relationship('User', backref='results')

    id_club = db.Column(db.Integer, db.ForeignKey('club.id_club'), nullable=False)
    club = db.relationship('Club', backref='results')

    id_competition = db.Column(db.Integer, db.ForeignKey('competition.id_competition'), nullable=False)
    competition = db.relationship('Competition', backref='results')

    id_style = db.Column(db.Integer, db.ForeignKey('swimming_style.id_style'), nullable=False)
    swimming_style = db.relationship('SwimmingStyle', backref='style_results')

    distance_time = db.Column(db.Float, nullable=False)  # Przechowywane w sekundach
    formatted_time = db.Column(db.String(10), nullable=False)  # Nowe pole na format oryginalny
    reaction_time = db.Column(db.Float, nullable=False)

    def format_time(self, distance_time_in_seconds):
        """Konwertuj czas na format MM:SS.ss"""
        minutes = int(distance_time_in_seconds // 60)
        seconds = distance_time_in_seconds % 60
        return f"{minutes:02}:{seconds:05.2f}"

    def format_reaction_time(self, reaction_time_in_seconds):
        """Konwertuj czas reakcji na format SS.ss"""
        seconds = int(reaction_time_in_seconds)
        centiseconds = int((reaction_time_in_seconds - seconds) * 100)
        return f"{seconds:02}.{centiseconds:02}"

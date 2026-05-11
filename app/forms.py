from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional 

class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        validators=[
            DataRequired(message="Pole e-mail jest wymagane."),
            Email(message="Podaj poprawny adres e-mail."),
        ],
    )
    password = PasswordField(
        "Hasło",
        validators=[
            DataRequired(message="Pole hasło jest wymagane."),
            Length(min=6, message="Hasło musi mieć co najmniej 6 znaków."),
        ],
    )
    submit = SubmitField("Zaloguj się")

class EditProfileForm(FlaskForm):
    user_name = StringField("Imię", validators=[DataRequired()])
    last_name = StringField("Nazwisko", validators=[DataRequired()])
    email_address = StringField("E-mail", validators=[DataRequired(), Email()])
    current_password = PasswordField("Bieżące hasło", validators=[Optional()])
    new_password = PasswordField(
        "Nowe hasło",
        validators=[
            Optional(),
            Length(min=8),
            EqualTo("confirm_password", message="Hasła muszą być zgodne."),
        ],
    )
    confirm_password = PasswordField("Potwierdź nowe hasło", validators=[Optional()])
    photo = FileField("Zdjęcie profilowe")

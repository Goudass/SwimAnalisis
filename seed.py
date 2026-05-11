# from app import app, db
# from app.models import User, Competition, SwimmingStyle, Result
# from datetime import date
# from werkzeug.security import generate_password_hash


# # def seed():
# #     with app.app_context():
# #         # Pobierz zawodnika i styl
# #         user = User.query.get(1)  # Zakładamy, że zawodnik z id_user=1 istnieje
# #         style = SwimmingStyle.query.filter_by(distance=50, style_name="Dowolny").first()
# #         club_id = user.club_id if user else None

# #         if not user or not style:
# #             print("Brakuje danych zawodnika lub stylu w bazie danych.")
# #             return

# #         # Lista zawodów i wyników do dodania
# #         competitions_results = [
# #             {"competition_name": "Letnie Zawody", "competition_city": "Warszawa", "competition_date": date(2018, 6, 15), "distance_time": 30.12, "reaction_time": 0.85},
# #             {"competition_name": "Zimowe Zawody", "competition_city": "Kraków", "competition_date": date(2019, 12, 10), "distance_time": 29.75, "reaction_time": 0.80},
# #             {"competition_name": "Wiosenne Zawody", "competition_city": "Poznań", "competition_date": date(2020, 4, 20), "distance_time": 29.10, "reaction_time": 0.78},
# #             {"competition_name": "Jesienne Zawody", "competition_city": "Gdańsk", "competition_date": date(2021, 10, 5), "distance_time": 28.95, "reaction_time": 0.76},
# #             {"competition_name": "Międzynarodowe Zawody", "competition_city": "Warszawa", "competition_date": date(2022, 8, 25), "distance_time": 28.70, "reaction_time": 0.75},
# #             {"competition_name": "Mistrzostwa Polski", "competition_city": "Łódź", "competition_date": date(2023, 3, 10), "distance_time": 28.50, "reaction_time": 0.74},
# #         ]

# #         # Dodanie zawodów i wyników
# #         for data in competitions_results:
# #             # Sprawdź, czy zawody istnieją
# #             competition = Competition.query.filter_by(competition_name=data["competition_name"]).first()

# #             if not competition:
# #                 # Dodaj zawody
# #                 competition = Competition(
# #                     competition_name=data["competition_name"],
# #                     competition_city=data["competition_city"],
# #                     competition_date=data["competition_date"]
# #                 )
# #                 db.session.add(competition)
# #                 db.session.commit()

# #             # Dodaj wynik
# #             result = Result(
# #                 id_user=user.id_user,
# #                 id_club=club_id,
# #                 id_competition=competition.id_competition,
# #                 id_style=style.id_style,
# #                 distance_time=data["distance_time"],
# #                 reaction_time=data["reaction_time"]
# #             )
# #             db.session.add(result)

# #         db.session.commit()
# #         print("Wyniki zostały pomyślnie dodane do różnych zawodów.")


# # if __name__ == "__main__":
# #     seed()


# # from app import app, db
# # from app.models import Role, SwimmingStyle

# # def seed():
# #     with app.app_context():
# #         # Usunięcie istniejących danych (opcjonalnie)
# #         db.session.query(Role).delete()
# #         db.session.query(SwimmingStyle).delete()
# #         db.session.commit()

# #         # Dodanie ról
# #         roles = [
# #             Role(id_role=1, role_name="Admin"),
# #             Role(id_role=2, role_name="Trener"),
# #             Role(id_role=3, role_name="Zawodnik"),
# #         ]

# #         db.session.bulk_save_objects(roles)

# #         # Dodanie styli pływackich
# #         swimming_styles = [
# #             SwimmingStyle(style_name="Dowolny", distance=50),
# #             SwimmingStyle(style_name="Dowolny", distance=100),
# #             SwimmingStyle(style_name="Dowolny", distance=200),
# #             SwimmingStyle(style_name="Dowolny", distance=400),
# #             SwimmingStyle(style_name="Dowolny", distance=800),
# #             SwimmingStyle(style_name="Dowolny", distance=1500),
# #             SwimmingStyle(style_name="Grzbietowy", distance=50),
# #             SwimmingStyle(style_name="Grzbietowy", distance=100),
# #             SwimmingStyle(style_name="Grzbietowy", distance=200),
# #             SwimmingStyle(style_name="Klasyczny", distance=50),
# #             SwimmingStyle(style_name="Klasyczny", distance=100),
# #             SwimmingStyle(style_name="Klasyczny", distance=200),
# #             SwimmingStyle(style_name="Motylkowy", distance=50),
# #             SwimmingStyle(style_name="Motylkowy", distance=100),
# #             SwimmingStyle(style_name="Motylkowy", distance=200),
# #             SwimmingStyle(style_name="Zmienny", distance=100),
# #             SwimmingStyle(style_name="Zmienny", distance=200),
# #             SwimmingStyle(style_name="Zmienny", distance=400),
# #         ]

# #         db.session.bulk_save_objects(swimming_styles)

# #         # Zapisanie zmian w bazie
# #         db.session.commit()

# #         print("Role i style pływackie zostały dodane pomyślnie!")

# # if __name__ == "__main__":
# #     seed()


# from app import app, db
# from app.models import Role, SwimmingStyle, Club, Competition, User, Result
# from datetime import date
# from werkzeug.security import generate_password_hash

# def seed():
#     with app.app_context():
#         # # Usunięcie istniejących danych (opcjonalnie, tylko jeśli chcesz wyczyścić bazę)
#         # db.session.query(Result).delete()
#         # db.session.query(User).delete()
#         # db.session.query(Competition).delete()
#         # db.session.query(Club).delete()
#         # # db.session.query(SwimmingStyle).delete()
#         # # db.session.query(Role).delete()
#         db.session.commit()

#         # **1️⃣ Dodanie ról**
#         # roles = [
#         #     Role(id_role=1, role_name="Admin"),
#         #     Role(id_role=2, role_name="Trener"),
#         #     Role(id_role=3, role_name="Zawodnik"),
#         # ]
#         # db.session.bulk_save_objects(roles)

#         # **2️⃣ Dodanie styli pływackich**
#         # swimming_styles = [
#         #     SwimmingStyle(style_name="Dowolny", distance=50),
#         #     SwimmingStyle(style_name="Dowolny", distance=100),
#         #     SwimmingStyle(style_name="Dowolny", distance=200),
#         #     SwimmingStyle(style_name="Dowolny", distance=400),
#         #     SwimmingStyle(style_name="Grzbietowy", distance=50),
#         #     SwimmingStyle(style_name="Grzbietowy", distance=100),
#         #     SwimmingStyle(style_name="Grzbietowy", distance=200),
#         #     SwimmingStyle(style_name="Klasyczny", distance=50),
#         #     SwimmingStyle(style_name="Klasyczny", distance=100),
#         #     SwimmingStyle(style_name="Klasyczny", distance=200),
#         #     SwimmingStyle(style_name="Motylkowy", distance=50),
#         #     SwimmingStyle(style_name="Motylkowy", distance=100),
#         #     SwimmingStyle(style_name="Motylkowy", distance=200),
#         #     SwimmingStyle(style_name="Zmienny", distance=100),
#         #     SwimmingStyle(style_name="Zmienny", distance=200),
#         #     SwimmingStyle(style_name="Zmienny", distance=400),
#         # ]
#         # db.session.bulk_save_objects(swimming_styles)

#         # **3️⃣ Dodanie klubów (Admin ma osobny klub)**
#         # clubs = [
#         #     Club(id_club=1, club_name="Admin Club", club_city="Brak"),
#         #     Club(id_club=2, club_name="AZS Warszawa", club_city="Warszawa"),
#         #     Club(id_club=3, club_name="UKS Delfin Kraków", club_city="Kraków"),
#         #     Club(id_club=4, club_name="MKS Poznań", club_city="Poznań"),
#         #     Club(id_club=5, club_name="GKS Gdańsk", club_city="Gdańsk"),
#         #     Club(id_club=6, club_name="WKS Wrocław", club_city="Wrocław"),
#         # ]
#         # db.session.bulk_save_objects(clubs)

#         # **4️⃣ Dodanie użytkowników (Admin, Trenerzy, Zawodnicy)**

#         def hash_password(password):
#             return generate_password_hash(password)

#         users = [
#             # # **Admin (w osobnym klubie)**
#             # User(
#             #     id_user=1, user_name="Admin", last_name="Systemowy", gender="M",
#             #     date_of_birth=date(1985, 1, 1), email_address="admin@admin.com",
#             #     password_hash=hash_password("admin123"),
#             #     id_role=1, club_id=1  # Klub Admin Club
#             # ),
#             # # **Trenerzy**
#             # User(
#             #     id_user=2, user_name="Jan", last_name="Kowalski", gender="M",
#             #     date_of_birth=date(1978, 3, 14), email_address="j.kowalski1@wp.pl",
#             #     password_hash=hash_password("kowalski123"),
#             #     id_role=2, club_id=2
#             # ),
#             # User(
#             #     id_user=3, user_name="Anna", last_name="Nowak", gender="K",
#             #     date_of_birth=date(1982, 7, 20), email_address="a.nowak@wp.pl",
#             #     password_hash=hash_password("nowak123"),
#             #     id_role=2, club_id=3
#             # ),
#             # # **Zawodnicy**
#             # User(
#             #     id_user=4, user_name="Marek", last_name="Wiśniewski", gender="M",
#             #     date_of_birth=date(2005, 6, 5), email_address="m.wisniewski@wp.pl",
#             #     password_hash=hash_password("marek123"),
#             #     id_role=3, club_id=2
#             # ),
#             # User(
#             #     id_user=5, user_name="Oliwia", last_name="Dąbrowska", gender="K",
#             #     date_of_birth=date(2006, 2, 12), email_address="o.dabrowska@wp.pl",
#             #     password_hash=hash_password("oliwia123"),
#             #     id_role=3, club_id=3
#             # ),
#             User(
#                 id_user=7, user_name="Jakub", last_name="Nowak", gender="M",
#                 date_of_birth=date(2007, 11, 28), email_address="j.nowak@wp.pl",
#                 password_hash=hash_password("jakub123"),
#                 id_role=3, club_id=2
#             ),
#         ]
#         db.session.bulk_save_objects(users)

#         # **5️⃣ Dodanie zawodów**
#         # competitions = [
#         #     Competition(competition_name="Letnie Zawody", competition_city="Warszawa", competition_date=date(2018, 6, 15)),
#         #     Competition(competition_name="Zimowe Zawody", competition_city="Kraków", competition_date=date(2019, 12, 10)),
#         #     Competition(competition_name="Wiosenne Zawody", competition_city="Poznań", competition_date=date(2020, 4, 20)),
#         #     Competition(competition_name="Jesienne Zawody", competition_city="Gdańsk", competition_date=date(2021, 10, 5)),
#         #     Competition(competition_name="Międzynarodowe Zawody", competition_city="Warszawa", competition_date=date(2022, 8, 25)),
#         #     Competition(competition_name="Mistrzostwa Polski", competition_city="Łódź", competition_date=date(2023, 3, 10)),
#         # ]
#         # db.session.bulk_save_objects(competitions)

#         # **6️⃣ Dodanie wyników zawodników**
#         results = []
#         for user_id, competition_id, time, reaction in [
#             (7, 1, 32.12, 0.80),
#             (7, 2, 28.75, 0.70),
#             (7, 3, 27.10, 0.60),
#             (7, 4, 29.95, 0.66),
#             (7, 5, 28.70, 0.62),
#             (7, 6, 26.50, 0.52),
#         ]:
#             user = User.query.get(user_id)
#             club_id = user.club_id if user else None
#             style = SwimmingStyle.query.filter_by(distance=50, style_name="Dowolny").first()
#             competition = Competition.query.get(competition_id)

#             if user and style and competition:
#                 results.append(
#                     Result(
#                         id_user=user_id, id_club=club_id,
#                         id_competition=competition_id, id_style=style.id_style,
#                         distance_time=time, reaction_time=reaction
#                     )
#                 )

#         db.session.bulk_save_objects(results)
#         db.session.commit()

#         print("✅ Dodano role, style, kluby, trenerów, zawodników, zawody i wyniki!")

# if __name__ == "__main__":
#     seed()











# from flask import render_template, request, redirect, url_for, flash, Response
# from flask_login import login_user, logout_user, login_required, current_user
# from app import app, db
# from app.models import User, Role, Club, Competition, Result, SwimmingStyle
# from datetime import date
# import io
# import matplotlib.pyplot as plt
# import openai
# from sqlalchemy import func
# from app.forms import LoginForm
# from analysis.trend import analyze_trend, generate_multi_line_plot, generate_trend_plot
# import base64

# # 🔹 Strona główna – przekierowanie do profilu
# @app.route("/")
# def index():
#     if current_user.is_authenticated:
#         return redirect(url_for('profile', user_id=current_user.id_user))
#     return redirect(url_for('login'))

# # 🔹 Logowanie
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("profile", user_id=current_user.id_user))
    
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         user = User.query.filter_by(email_address=email).first()
        
#         if user and user.check_password(password):
#             login_user(user)
#             flash("Zalogowano pomyślnie!", "success")
#             return redirect(url_for("profile", user_id=user.id_user))
#         else:
#             flash("Nieprawidłowy e-mail lub hasło.", "danger")
    
#     return render_template("login.html", title="Logowanie")

# # 🔹 Wylogowanie
# @app.route("/logout", methods=["GET", "POST"])
# @login_required
# def logout():
#     logout_user()
#     flash("Wylogowano pomyślnie.", "info")
#     return redirect(url_for("login"))

# # 🔹 Rejestracja nowego użytkownika
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         try:
#             user_name = request.form["user_name"]
#             last_name = request.form["last_name"]
#             gender = request.form["gender"]
#             date_of_birth = date.fromisoformat(request.form["date_of_birth"])
#             email = request.form["email"]
#             password = request.form["password"]
#             role_id = int(request.form["role_id"])
#             club_id = int(request.form["club_id"])

#             # Sprawdzenie, czy użytkownik istnieje
#             existing_user = User.query.filter_by(email_address=email).first()
#             if existing_user:
#                 flash("Użytkownik z podanym e-mailem już istnieje.", "danger")
#             else:
#                 new_user = User(
#                     user_name=user_name,
#                     last_name=last_name,
#                     gender=gender,
#                     date_of_birth=date_of_birth,
#                     email_address=email,
#                     id_role=role_id,
#                     club_id=club_id
#                 )
#                 new_user.set_password(password)
#                 db.session.add(new_user)
#                 db.session.commit()
#                 flash("Rejestracja zakończona sukcesem!", "success")
#                 return redirect(url_for("login"))
#         except Exception as e:
#             flash("Wystąpił błąd podczas rejestracji. Spróbuj ponownie.", "danger")

#     roles = Role.query.all()
#     clubs = Club.query.all()
#     return render_template("register.html", roles=roles, clubs=clubs, title="Rejestracja")

# # 🔹 Profil użytkownika
# @app.route("/profile/<int:user_id>")
# @login_required
# def profile(user_id):
#     user = User.query.get_or_404(user_id)
#     return render_template("profile.html", user=user, title="Profil użytkownika")

# # 🔹 Edycja profilu
# @app.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def edit_profile(user_id):
#     user = User.query.get_or_404(user_id)

#     if current_user.id_user != user.id_user:
#         flash("Nie masz uprawnień do edytowania tego profilu.", "danger")
#         return redirect(url_for('profile', user_id=current_user.id_user))

#     if request.method == 'POST':
#         try:
#             user.user_name = request.form.get('user_name', user.user_name)
#             user.last_name = request.form.get('last_name', user.last_name)
#             user.email_address = request.form.get('email_address', user.email_address)

#             new_password = request.form.get('password')
#             if new_password:
#                 user.set_password(new_password)

#             db.session.commit()
#             flash("Profil został zaktualizowany.", "success")
#         except Exception:
#             flash("Błąd podczas aktualizacji profilu.", "danger")

#         return redirect(url_for('profile', user_id=user.id_user))

#     return render_template('edit_profile.html', user=user)

# # 🔹 Lista zawodników w klubie trenera
# @app.route("/profile/<int:user_id>/club_athletes")
# @login_required
# def club_athletes(user_id):
#     user = User.query.get_or_404(user_id)

#     if user.id_role != 2:
#         flash("Brak dostępu do tej sekcji.", "danger")
#         return redirect(url_for("profile", user_id=user_id))

#     club_id = user.club_id
#     athletes = User.query.filter_by(club_id=club_id, id_role=3).all()
    
#     return render_template("club_athletes.html", user=user, athletes=athletes, title="Lista zawodników")

# # 🔹 Lista wyników zawodnika
# @app.route("/profile/<int:user_id>/results")
# @login_required
# def results(user_id):
#     user = User.query.get_or_404(user_id)
#     results = Result.query.filter_by(id_user=user_id).all()
#     return render_template("results.html", user=user, results=results, title="Wyniki")

# # 🔹 Lista zawodów zawodnika
# @app.route("/profile/<int:user_id>/competitions")
# @login_required
# def competitions(user_id):
#     user = User.query.get_or_404(user_id)
#     competitions = (
#         db.session.query(
#             Competition.competition_name,
#             Competition.competition_date,
#             Competition.competition_city
#         )
#         .join(Result, Result.id_competition == Competition.id_competition)
#         .filter(Result.id_user == user_id)
#         .order_by(Competition.competition_date.desc())
#         .distinct()
#         .all()
#     )
#     return render_template("competitions.html", user=user, competitions=competitions, title="Zawody")



from app import app, db
from app.models import Role, SwimmingStyle, Club, Competition, User, Result
from datetime import date
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        def hash_password(password):
            return generate_password_hash(password)

        users = [
            User(
                user_name="Jakub", last_name="Nowak", gender="M",
                date_of_birth=date(2007, 11, 28), email_address="j.nowak@wp.pl",
                password_hash=hash_password("jakub123"),
                id_role=3, club_id=2
            ),
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()

        # Pobieranie nowo dodanego użytkownika
        user = User.query.filter_by(email_address="j.nowak@wp.pl").first()
        if not user:
            print("⚠️ Nie udało się dodać użytkownika!")
            return

        results = []
        for user_id, competition_id, time, reaction in [
            (user.id_user, 1, 32.12, 0.80),
            (user.id_user, 2, 28.75, 0.70),
            (user.id_user, 3, 27.10, 0.60),
            (user.id_user, 4, 29.95, 0.66),
            (user.id_user, 5, 28.70, 0.62),
            (user.id_user, 6, 26.50, 0.52),
        ]:
            competition = Competition.query.get(competition_id)
            if not competition:
                print(f"⚠️ Nie znaleziono zawodów o ID: {competition_id}")
                continue

            style = SwimmingStyle.query.filter_by(distance=50, style_name="Dowolny").first()
            if not style:
                print("⚠️ Nie znaleziono stylu pływackiego: 50m Dowolny")
                return

            results.append(
                Result(
                    id_user=user_id, id_club=user.club_id,
                    id_competition=competition_id, id_style=style.id_style,
                    distance_time=time, reaction_time=reaction
                )
            )

        if results:
            db.session.bulk_save_objects(results)
            db.session.commit()

        print("✅ Dodano użytkownika, zawody i wyniki!")

if __name__ == "__main__":
    seed()

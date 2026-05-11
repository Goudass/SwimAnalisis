from flask import render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Role, Club, Competition, Result, SwimmingStyle
from datetime import date
import io
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import matplotlib.pyplot as plt
import openai
from sqlalchemy import func
from app.forms import LoginForm
from analysis.trend import analyze_trend, generate_multi_line_plot, generate_trend_plot
import base64
from datetime import datetime
from functools import wraps


# Strona główna
@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role.role_name == "Trener":
            # Pobranie ostatnich wyników zawodników klubu
            latest_results = (
                db.session.query(Result)
                .join(User, Result.id_user == User.id_user)
                .filter(User.club_id == current_user.club_id)
                .order_by(Result.id_result.desc())
                .limit(5)
                .all()
            )
            # Pobranie nadchodzących zawodów
            upcoming_competitions = (
                Competition.query
                .order_by(Competition.competition_date.asc())
                .limit(5)
                .all()
            )
            return render_template(
                "home.html",
                latest_results=latest_results,
                upcoming_competitions=upcoming_competitions,
                title="Strona główna",
            )

        elif current_user.role.role_name == "Zawodnik":
            # Pobranie ostatnich wyników użytkownika
            user_results = (
                db.session.query(Result)
                .join(Competition, Result.id_competition == Competition.id_competition)
                .filter(Result.id_user == current_user.id_user)
                .order_by(Result.id_result.desc())
                .limit(5)
                .all()
            )
            return render_template("home.html", user_results=user_results, title="Strona główna")

    # Strona dla niezalogowanych użytkowników
    return render_template("home.html", title="Strona główna")



# @app.after_request
# def add_header(response):
#     response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "-1"
#     return response

# limiter = Limiter(get_remote_address, app=app)

# @limiter.limit("5 per minute")
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     # Jeśli użytkownik jest już zalogowany, przekieruj na profil
#     if current_user.is_authenticated:
#         return redirect(url_for("profile", user_id=current_user.id_user))
    
#     form = LoginForm()  # Używamy klasy LoginForm
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data
#         user = User.query.filter_by(email_address=email).first()
#         if user and user.check_password(password):
#             login_user(user)
#             flash("Zalogowano pomyślnie!", "success")
#             return redirect(url_for("profile", user_id=user.id_user))
#         else:
#             flash("Nieprawidłowy e-mail lub hasło.", "danger")
#     return render_template("login.html", form=form, title="Logowanie")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Jeśli użytkownik jest już zalogowany, przekieruj na profil
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email_address=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Zalogowano pomyślnie!", "success")
            return redirect(url_for("index"))
        else:
            flash("Nieprawidłowy e-mail lub hasło.", "danger")
    
    return render_template("login.html", title="Logowanie")

@app.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    """
    Widok do edycji danych użytkownika.
    """
    user = User.query.get_or_404(user_id)

    # Sprawdzenie uprawnień (użytkownik może edytować tylko swój profil)
    if current_user.id_user != user.id_user:
        flash("Nie masz uprawnień do edytowania tego profilu.", "danger")
        return redirect(url_for('profile', user_id=current_user.id_user))

    if request.method == 'POST':
        # Pobranie danych z formularza
        user_name = request.form.get('user_name')
        last_name = request.form.get('last_name')
        email_address = request.form.get('email_address')
        new_password = request.form.get('password')

        try:
            # Walidacja danych formularza
            if not user_name or not last_name or not email_address:
                flash("Wszystkie pola są wymagane (oprócz hasła).", "warning")
                return redirect(url_for('edit_profile', user_id=user.id_user))

            # Sprawdzenie, czy zmieniono dane
            data_changed = False

            if user.user_name != user_name:
                user.user_name = user_name
                data_changed = True

            if user.last_name != last_name:
                user.last_name = last_name
                data_changed = True

            if user.email_address != email_address:
                user.email_address = email_address
                data_changed = True

            # Obsługa zmiany hasła (opcjonalnie)
            if new_password:
                if len(new_password) < 6:
                    flash("Hasło musi mieć co najmniej 6 znaków.", "warning")
                    return redirect(url_for('edit_profile', user_id=user.id_user))
                user.set_password(new_password)
                data_changed = True

            # Zapis zmian w bazie danych tylko, jeśli dane zostały zmienione
            if data_changed:
                db.session.commit()
                flash("Profil został zaktualizowany.", "success")
            else:
                flash("Nie wprowadzono żadnych zmian.", "info")

        except Exception as e:
            print(f"Błąd podczas aktualizacji profilu: {e}")
            flash("Wystąpił błąd podczas aktualizacji profilu. Spróbuj ponownie.", "danger")

        # Przekierowanie po zapisaniu danych
        return redirect(url_for('profile', user_id=user.id_user))

    # Renderowanie szablonu formularza edycji
    return render_template('edit_profile.html', user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Pobranie danych z formularza
        user_name = request.form["user_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        date_of_birth = date.fromisoformat(request.form["date_of_birth"])
        email = request.form["email"]
        password = request.form["password"]
        role_id = request.form["role_id"]
        club_id = request.form["club_id"]

        # Sprawdzenie, czy użytkownik już istnieje
        existing_user = User.query.filter_by(email_address=email).first()
        if existing_user:
            flash("Użytkownik z podanym e-mailem już istnieje.", "danger")
        else:
            # Dodanie nowego użytkownika
            new_user = User(
                user_name=user_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                email_address=email,
                id_role=role_id,
                club_id=club_id,
            )
            new_user.set_password(password)  # Haszowanie hasła
            db.session.add(new_user)
            db.session.commit()
            flash("Rejestracja zakończona sukcesem!", "success")
            return redirect(url_for("login"))

    # Pobranie ról z bazy, z wykluczeniem roli 'Admin' (id=1)
    roles = Role.query.filter(Role.id_role != 1).all()  # Filtruj rolę 'Admin'
    
    # Pobranie klubów z bazy, z wykluczeniem klubu 'Admin Club' (id=1)
    clubs = Club.query.filter(Club.id_club != 1).all()  # Filtruj klub o id=1

    return render_template("register.html", roles=roles, clubs=clubs, title="Rejestracja")



@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)

    # Pobieranie rekordów życiowych
    personal_bests = []
    for result in user.results:
        formatted_time = result.format_time(result.distance_time)  # Używamy metody do formatowania czasu
        personal_bests.append({
            "distance": result.swimming_style.distance,
            "style_name": result.swimming_style.style_name,
            "formatted_time": formatted_time,  # Dodajemy sformatowany czas
            "competition_date": result.competition.competition_date,
            "competition_name": result.competition.competition_name,
            "competition_city": result.competition.competition_city,
            "id_style": result.id_style
        })

    return render_template("profile.html", user=user, personal_bests=personal_bests, title="Profil użytkownika")

# Wylogowanie
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Wylogowano pomyślnie.", "info")
    return redirect(url_for("login"))

# Dekorator sprawdzający, czy użytkownik jest adminem
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name != 'Admin':
            flash("Nie masz uprawnień do tej akcji.", "danger")
            return redirect(url_for('index'))  # Przekierowanie na stronę główną
        return func(*args, **kwargs)
    return wrapper


# Widoki zarządzania użytkownikami
@app.route("/admin/manage/users", methods=["GET"])
@login_required
@admin_required
def manage_users():
    users = User.query.all()  # Pobieramy wszystkich użytkowników
    return render_template("admin/manage_users.html", users=users)

@app.route("/admin/manage/users/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Użytkownik usunięty pomyślnie!", "success")
    return redirect(url_for("manage_users"))

@app.route("/admin/manage/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.user_name = request.form["user_name"]
        user.last_name = request.form["last_name"]
        db.session.commit()
        flash("Dane użytkownika zaktualizowane!", "success")
        return redirect(url_for("manage_users"))
    return render_template("admin/edit_user.html", user=user)

@app.route("/admin/manage/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    roles = Role.query.all()
    clubs = Club.query.all()
    if request.method == "POST":
        user_name = request.form["user_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        email_address = request.form["email_address"]
        password = request.form["password"]
        role_id = request.form["role_id"]
        club_id = request.form["club_id"]
        
        # Tworzenie nowego użytkownika
        new_user = User(
            user_name=user_name,
            last_name=last_name,
            gender=gender,
            email_address=email_address,
            password_hash=generate_password_hash(password),
            id_role=role_id,
            club_id=club_id
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Użytkownik dodany pomyślnie!", "success")
        return redirect(url_for("manage_users"))
    return render_template("admin/add_user.html", roles=roles, clubs=clubs)


# Widoki zarządzania klubami
@app.route("/admin/manage/clubs", methods=["GET"])
@login_required
@admin_required
def manage_clubs():
    clubs = Club.query.all()  # Pobieramy wszystkie kluby
    return render_template("admin/manage_clubs.html", clubs=clubs)

@app.route("/admin/manage/clubs/delete/<int:club_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    flash("Klub usunięty pomyślnie!", "success")
    return redirect(url_for("manage_clubs"))

@app.route("/admin/manage/clubs/edit/<int:club_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_club(club_id):
    club = Club.query.get_or_404(club_id)
    if request.method == "POST":
        club.club_name = request.form["club_name"]
        club.club_city = request.form["club_city"]
        db.session.commit()
        flash("Dane klubu zaktualizowane!", "success")
        return redirect(url_for("manage_clubs"))
    return render_template("admin/edit_club.html", club=club)

@app.route("/admin/manage/clubs/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_club():
    if request.method == "POST":
        club_name = request.form["club_name"]
        club_city = request.form["club_city"]
        
        # Tworzenie nowego klubu
        new_club = Club(club_name=club_name, club_city=club_city)
        db.session.add(new_club)
        db.session.commit()
        flash("Klub dodany pomyślnie!", "success")
        return redirect(url_for("manage_clubs"))
    return render_template("admin/add_club.html")


# Widoki zarządzania zawodami
@app.route("/admin/manage/competitions", methods=["GET"])
@login_required
@admin_required
def manage_competitions():
    competitions = Competition.query.all()  # Pobieramy wszystkie zawody
    return render_template("admin/manage_competitions.html", competitions=competitions)

@app.route("/admin/manage/competitions/delete/<int:competition_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_competition(competition_id):
    competition = Competition.query.get_or_404(competition_id)
    db.session.delete(competition)
    db.session.commit()
    flash("Zawody usunięte pomyślnie!", "success")
    return redirect(url_for("manage_competitions"))

@app.route("/admin/manage/competitions/edit/<int:competition_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_competition(competition_id):
    competition = Competition.query.get_or_404(competition_id)
    if request.method == "POST":
        competition.competition_name = request.form["competition_name"]
        competition.competition_city = request.form["competition_city"]
        competition.competition_date = request.form["competition_date"]
        db.session.commit()
        flash("Dane zawodów zaktualizowane!", "success")
        return redirect(url_for("manage_competitions"))
    return render_template("admin/edit_competition.html", competition=competition)

@app.route("/admin/manage/competitions/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_competition():
    if request.method == "POST":
        competition_name = request.form["competition_name"]
        competition_city = request.form["competition_city"]
        competition_date = request.form["competition_date"]
        
        # Tworzenie nowego konkursu
        new_competition = Competition(
            competition_name=competition_name,
            competition_city=competition_city,
            competition_date=competition_date
        )
        db.session.add(new_competition)
        db.session.commit()
        flash("Zawody dodane pomyślnie!", "success")
        return redirect(url_for("manage_competitions"))
    return render_template("admin/add_competition.html")


# Widoki zarządzania wynikami
@app.route("/admin/manage/results", methods=["GET"])
@login_required
@admin_required
def manage_results():
    results = Result.query.all()  # Pobieramy wszystkie wyniki
    return render_template("admin/manage_results.html", results=results)

@app.route("/admin/manage/results/delete/<int:result_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_result(result_id):
    result = Result.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash("Wynik usunięty pomyślnie!", "success")
    return redirect(url_for("manage_results"))

@app.route("/admin/manage/results/edit/<int:result_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_result(result_id):
    result = Result.query.get_or_404(result_id)
    if request.method == "POST":
        result.distance_time = request.form["distance_time"]
        result.formatted_time = format_seconds_to_time(result.distance_time)
        db.session.commit()
        flash("Wynik zaktualizowany!", "success")
        return redirect(url_for("manage_results"))
    return render_template("admin/edit_result.html", result=result)

@app.route("/admin/manage/results/add", methods=["GET", "POST"])
@login_required
@admin_required
def admin_add_result():
    users = User.query.all()
    competitions = Competition.query.all()
    if request.method == "POST":
        user_id = request.form["user_id"]
        competition_id = request.form["competition_id"]
        distance_time = request.form["distance_time"]
        reaction_time = request.form["reaction_time"]
        
        # Tworzenie nowego wyniku
        new_result = Result(
            id_user=user_id,
            id_competition=competition_id,
            distance_time=distance_time,
            reaction_time=reaction_time,
            formatted_time=format_seconds_to_time(distance_time)
        )

        db.session.add(new_result)
        db.session.commit()
        flash("Wynik dodany pomyślnie!", "success")
        return redirect(url_for("manage_results"))

    return render_template("admin/add_result.html", users=users, competitions=competitions)



# Wyniki progresji z analizą
@app.route("/profile/<int:user_id>/progression/<int:style_id>")
@login_required
def progression(user_id, style_id):
    user = User.query.get_or_404(user_id)
    results = (
        db.session.query(
            Result.distance_time,
            Competition.competition_date
        )
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == user_id, Result.id_style == style_id)
        .order_by(Competition.competition_date.asc())
        .all()
    )

    if not results:
        flash("Brak wyników do analizy progresji.", "warning")
        return redirect(url_for("results_by_distance", user_id=user_id, style_id=style_id))

    dates = [result.competition_date for result in results]
    times = [result.distance_time for result in results]

    # Generowanie analizy
    analysis = generate_analysis(dates, times)

    # Tworzenie wykresu
    plt.figure(figsize=(10, 6))
    plt.plot(dates, times, marker='o', linestyle='-', color='blue')
    plt.title(f"Progresja wyników dla {user.user_name} {user.last_name}")
    plt.xlabel("Data")
    plt.ylabel("Czas (s)")
    plt.gca().invert_yaxis()  # Czasy lepsze u góry
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return render_template(
        "progression.html",
        user=user,
        analysis=analysis,
        image_url=url_for("progression_image", user_id=user_id, style_id=style_id),
        title="Progresja wyników"
    )

@app.route("/profile/<int:user_id>/progression/<int:style_id>/image")
@login_required
def progression_image(user_id, style_id):
    results = (
        db.session.query(
            Result.distance_time,
            Competition.competition_date
        )
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == user_id, Result.id_style == style_id)
        .order_by(Competition.competition_date.asc())
        .all()
    )

    dates = [result.competition_date for result in results]
    times = [result.distance_time for result in results]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, times, marker='o', linestyle='-', color='blue')
    plt.title("Progresja wyników")
    plt.xlabel("Data")
    plt.ylabel("Czas (s)")
    plt.gca().invert_yaxis()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return Response(img, mimetype="image/png")

# Funkcja generująca analizę
def generate_analysis(dates, times):
    """
    Generuje analizę wyników na podstawie danych.
    """
    # Przygotowanie danych wejściowych do analizy
    formatted_data = "\n".join([f"{date}: {time:.2f}s" for date, time in zip(dates, times)])
    prompt = f"""
    Na podstawie poniższych danych wyników zawodnika wygeneruj analizę:
    - Podaj trend wyników (czy zawodnik poprawia swoje wyniki, czy nie).
    - Uwzględnij, czy były znaczące różnice w czasie między zawodami.
    - Zwróć uwagę na najlepszy i najgorszy wynik.

    Dane:
    {formatted_data}

    Napisz analizę w języku polskim.
    """

    # Wysyłanie zapytania do OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # lub "gpt-4"
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem do analizy wyników sportowych."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()


@app.route("/profile/<int:user_id>/personal_bests")
@login_required
def personal_bests(user_id):
    user = User.query.get_or_404(user_id)
    personal_bests = (
        db.session.query(
            Result.id_style,
            SwimmingStyle.distance,
            SwimmingStyle.style_name,
            db.func.min(Result.distance_time).label("best_time"),
            db.func.min(Result.reaction_time).label("best_reaction_time"),
            Competition.competition_name,
            Competition.competition_date,
            Competition.competition_city
        )
        .join(SwimmingStyle, Result.id_style == SwimmingStyle.id_style)
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == user_id)
        .group_by(Result.id_style)
        .order_by(SwimmingStyle.distance, SwimmingStyle.style_name)
        .all()
    )
    return render_template(
        "personal_bests.html",
        user=user,
        personal_bests=personal_bests,
        title="Rekordy życiowe"
    )

@app.route("/profile/<int:user_id>/competitions")
@login_required
def competitions(user_id):
    user = User.query.get_or_404(user_id)
    competitions = (
        db.session.query(
            Competition.competition_name,
            Competition.competition_date,
            Competition.competition_city
        )
        .join(Result, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == user_id)
        .order_by(Competition.competition_date.desc())
        .distinct()
        .all()
    )
    return render_template("competitions.html", user=user, competitions=competitions, title="Zawody")

@app.route("/profile/<int:user_id>/results_by_distance/<int:style_id>")
@login_required
def results_by_distance(user_id, style_id):
    user = User.query.get_or_404(user_id)

    # Pobierz styl pływacki na podstawie style_id
    swimming_style = SwimmingStyle.query.get_or_404(style_id)
    distance = swimming_style.distance  # Wyciągnięcie dystansu z obiektu stylu

    # Pobierz wszystkie wyniki dla tego stylu i użytkownika
    results = (
        db.session.query(Result)
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == user_id, Result.id_style == style_id)
        .order_by(Result.distance_time.asc())  # Sortowanie od najszybszych do najwolniejszych
        .all()
    )

    return render_template(
        "results_by_distance.html",
        user=user,
        results=results,
        distance=distance,
        title="Wyniki dla dystansu",
    )



@app.route("/club_athletes", methods=["GET"])
@login_required
def club_athletes():
    # Sprawdzenie, czy użytkownik to trener
    if current_user.id_role != 2:  # 2 = Trener
        flash("Brak dostępu do tej sekcji.", "danger")
        return redirect(url_for("index"))

    club_id = current_user.club_id  # Pobranie ID klubu trenera

    # Pobranie lat urodzenia zawodników w klubie
    available_years = (
        db.session.query(db.extract("year", User.date_of_birth).label("year"))
        .filter(User.club_id == club_id, User.id_role == 3)  # 3 = Zawodnik
        .distinct()
        .order_by("year")
        .all()
    )
    available_years = [int(year.year) for year in available_years]  # Przekształcenie do listy

    # Obsługa filtrów
    first_name_query = request.args.get("first_name", "").strip()
    last_name_query = request.args.get("last_name", "").strip()
    selected_year = request.args.get("year", "").strip()

    # Budowanie zapytania
    query = User.query.filter(User.club_id == club_id, User.id_role == 3)

    if first_name_query:
        query = query.filter(User.user_name.ilike(f"%{first_name_query}%"))
    if last_name_query:
        query = query.filter(User.last_name.ilike(f"%{last_name_query}%"))
    if selected_year:
        try:
            year = int(selected_year)
            query = query.filter(db.extract("year", User.date_of_birth) == year)
        except ValueError:
            flash("Podaj poprawny rok.", "warning")

    athletes = query.all()

    return render_template(
        "club_athletes.html", 
        athletes=athletes, 
        available_years=available_years
    )


@app.route("/profile/<int:trainer_id>/athlete/<int:athlete_id>/distance/<int:distance>/descriptive_statistics", methods=["GET", "POST"])
@login_required
def descriptive_statistics_for_distance(trainer_id, athlete_id, distance):
    # Pobranie danych trenera i zawodnika
    user = User.query.get_or_404(trainer_id)
    athlete = User.query.get_or_404(athlete_id)

    # Sprawdzenie uprawnień
    if user.role.id_role != 2 or athlete.club_id != user.club_id:
        flash("Brak dostępu do tej sekcji.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie stylu dla danego dystansu
    style = (
        db.session.query(SwimmingStyle)
        .filter_by(distance=distance)
        .first()
    )
    if not style:
        flash("Nie znaleziono stylu dla podanego dystansu.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie dostępnych lat
    available_years = (
        db.session.query(db.func.extract("year", Competition.competition_date).label("year"))
        .join(Result, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == athlete_id, Result.id_style == style.id_style)
        .distinct()
        .order_by("year")
        .all()
    )
    available_years = [int(y.year) for y in available_years]

    # Pobierz wszystkie wyniki (dla wszystkich lat)
    all_results = (
        db.session.query(Result)
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == athlete_id, Result.id_style == style.id_style)
        .all()
    )

    # Statystyki ogólne
    overall_stats = None
    if all_results:
        all_times = [r.distance_time for r in all_results]
        all_reactions = [r.reaction_time for r in all_results]

        overall_stats = {
            "average_time": sum(all_times) / len(all_times) if all_times else None,
            "best_time": min(all_times) if all_times else None,
            "best_reaction": min(all_reactions) if all_reactions else None,
            "total_starts": len(all_times),
        }

        # Formatowanie czasów
        if overall_stats["average_time"]:
            overall_stats["average_time"] = athlete.results[0].format_time(overall_stats["average_time"])
        if overall_stats["best_time"]:
            overall_stats["best_time"] = athlete.results[0].format_time(overall_stats["best_time"])

    # Domyślne statystyki
    stats = overall_stats
    selected_year = None

    # Obsługa wyboru roku
    if request.method == "POST":
        selected_year = request.form.get("year")
        if selected_year:
            selected_year = int(selected_year)
            year_results = [
                r for r in all_results if r.competition.competition_date.year == selected_year
            ]
            if year_results:
                year_times = [r.distance_time for r in year_results]
                year_reactions = [r.reaction_time for r in year_results]

                # Statystyki dla wybranego roku
                stats.update({
                    "average_year_time": sum(year_times) / len(year_times) if year_times else None,
                    "best_year_time": min(year_times) if year_times else None,
                    "best_year_reaction": min(year_reactions) if year_reactions else None,
                    "year_starts": len(year_times),
                })

                # Formatowanie czasów dla roku
                if stats["average_year_time"]:
                    stats["average_year_time"] = athlete.results[0].format_time(stats["average_year_time"])
                if stats["best_year_time"]:
                    stats["best_year_time"] = athlete.results[0].format_time(stats["best_year_time"])

    # Renderowanie szablonu
    return render_template(
        "descriptive_statistics_distance.html",
        user=user,
        athlete=athlete,
        distance=distance,
        style_name=style.style_name,  # Dodanie nazwy stylu
        stats=stats,
        selected_year=selected_year,
        available_years=available_years,
        title=f"Statystyka opisowa dla {distance} m - {style.style_name}"
    )



@app.route("/profile/<int:trainer_id>/athlete/<int:athlete_id>/distance/<int:distance>/trend_analysis", methods=["GET"])
@login_required
def trend_analysis_for_distance(trainer_id, athlete_id, distance):
    user = User.query.get_or_404(trainer_id)
    athlete = User.query.get_or_404(athlete_id)

    # Sprawdzenie, czy użytkownik jest trenerem lub zawodnikiem
    if user.role.id_role != 2 and user.id_user != athlete.id_user:  # Jeśli użytkownik to nie trener ani zawodnik
        flash("Dostęp do analizy trendu jest zarezerwowany dla trenera lub zawodnika.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Sprawdzenie przynależności zawodnika do klubu trenera
    if athlete.club_id != user.club_id and user.role.id_role == 2:  # Jeśli użytkownik jest trenerem, sprawdzamy klub
        flash("Nie masz uprawnień do analizy trendu dla tego zawodnika.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie wyników dla danego dystansu
    results = (
        db.session.query(Result)
        .join(SwimmingStyle, Result.id_style == SwimmingStyle.id_style)
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == athlete_id, SwimmingStyle.distance == distance)
        .order_by(Competition.competition_date.asc())
        .all()
    )

    if not results:
        flash("Brak wyników do analizy trendu.", "warning")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie szczegółów stylu na podstawie wyników
    style = (
        db.session.query(SwimmingStyle)
        .filter_by(id_style=results[0].id_style, distance=distance)
        .first()
    )
    if not style:
        flash("Nie znaleziono stylu dla podanego dystansu.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Przygotowanie danych do analizy
    dates = [r.competition.competition_date for r in results]
    times = [r.distance_time for r in results]
    formatted_times = [r.format_time(r.distance_time) for r in results]  # Dodanie sformatowanych czasów

    # Generowanie opisu trendu i wykresu
    trend_description = analyze_trend(dates, times)
    trend_plot = generate_trend_plot(dates, times, formatted_times)  # Przekazanie sformatowanych czasów do wykresu

    return render_template(
        "trend_analysis.html",
        user=user,
        athlete=athlete,
        distance=distance,
        style_id=style.id_style,  # Przekazywanie style_id
        style_name=style.style_name,  # Przekazywanie nazwy stylu
        trend_description=trend_description,
        trend_plot=trend_plot,
        formatted_times=formatted_times,  # Przekazywanie sformatowanych czasów do szablonu
        title=f"Analiza trendu dla {distance} m - {style.style_name}"
    )



@app.route("/profile/<int:trainer_id>/athlete/<int:athlete_id>/distance/<int:distance>/compare_seasons", methods=["GET", "POST"])
@login_required
def compare_seasons_for_distance(trainer_id, athlete_id, distance):
    """
    Porównanie wyników zawodnika sezonami na konkretnym dystansie i stylu.
    """
    user = User.query.get_or_404(trainer_id)
    athlete = User.query.get_or_404(athlete_id)

    # Sprawdzenie uprawnień trenera
    if user.role.id_role != 2 or athlete.club_id != user.club_id:
        flash("Brak dostępu do tej sekcji.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie stylu pływackiego
    style = (
        db.session.query(SwimmingStyle)
        .filter_by(distance=distance)
        .first()
    )
    if not style:
        flash("Nie znaleziono stylu dla podanego dystansu.", "danger")
        return redirect(url_for("profile", user_id=trainer_id))

    # Pobranie wyników zawodnika na danym dystansie i stylu
    results = (
        db.session.query(Result)
        .join(SwimmingStyle, Result.id_style == SwimmingStyle.id_style)
        .join(Competition, Result.id_competition == Competition.id_competition)
        .filter(Result.id_user == athlete_id, SwimmingStyle.id_style == style.id_style)
        .order_by(Competition.competition_date.asc())
        .all()
    )

    if not results:
        flash("Brak wyników dla tego dystansu i stylu.", "warning")
        return redirect(url_for("profile", user_id=trainer_id))

    # Grupowanie wyników według roku
    from collections import defaultdict
    seasons = defaultdict(list)
    for result in results:
        year = result.competition.competition_date.year
        seasons[year].append(result)

    # Przygotowanie danych do wyświetlenia
    season_data = []
    for year, year_results in seasons.items():
        times = [r.distance_time for r in year_results]
        season_data.append({
            "year": year,
            "average_time": sum(times) / len(times) if times else None,
            "best_time": min(times) if times else None,
            "total_starts": len(year_results),
        })

    # Generowanie wykresu dla wyników wszystkich sezonów
    all_seasons_plot = generate_multi_line_plot(
        x_labels=[str(data["year"]) for data in season_data],
        avg_times=[data["average_time"] for data in season_data],
        best_times=[data["best_time"] for data in season_data],
        title=f"Wyniki wszystkich sezonów ({distance} m - {style.style_name})"
    )

    # Obsługa porównania dwóch lat
    compare_results = None
    year1 = year2 = None
    compare_plot = None
    if request.method == "POST":
        year1 = request.form.get("year1")
        year2 = request.form.get("year2")

        if year1 and year2:
            year1 = int(year1)
            year2 = int(year2)

            if year1 >= year2:
                flash("Pierwszy sezon musi być wcześniejszy niż drugi.", "warning")
            else:
                year1_results = seasons.get(year1, [])
                year2_results = seasons.get(year2, [])

                compare_results = {
                    "year1": {
                        "year": year1,
                        "average_time": sum(r.distance_time for r in year1_results) / len(year1_results) if year1_results else None,
                        "best_time": min((r.distance_time for r in year1_results), default=None),
                        "total_starts": len(year1_results),
                    },
                    "year2": {
                        "year": year2,
                        "average_time": sum(r.distance_time for r in year2_results) / len(year2_results) if year2_results else None,
                        "best_time": min((r.distance_time for r in year2_results), default=None),
                        "total_starts": len(year2_results),
                    },
                }

                # Generowanie wykresu dla porównania sezonów
                compare_plot = generate_multi_line_plot(
                    x_labels=[str(year1), str(year2)],
                    avg_times=[
                        compare_results["year1"]["average_time"] if compare_results["year1"]["average_time"] else 0,
                        compare_results["year2"]["average_time"] if compare_results["year2"]["average_time"] else 0,
                    ],
                    best_times=[
                        compare_results["year1"]["best_time"] if compare_results["year1"]["best_time"] else 0,
                        compare_results["year2"]["best_time"] if compare_results["year2"]["best_time"] else 0,
                    ],
                    title=f"Porównanie sezonów {year1} i {year2} ({distance} m - {style.style_name})"
                )

    # Formatowanie czasów przed wysłaniem do szablonu
    for season in season_data:
        season['average_time'] = format_seconds_to_time(season['average_time'])
        season['best_time'] = format_seconds_to_time(season['best_time'])

    if compare_results:
        compare_results["year1"]["average_time"] = format_seconds_to_time(compare_results["year1"]["average_time"])
        compare_results["year1"]["best_time"] = format_seconds_to_time(compare_results["year1"]["best_time"])
        compare_results["year2"]["average_time"] = format_seconds_to_time(compare_results["year2"]["average_time"])
        compare_results["year2"]["best_time"] = format_seconds_to_time(compare_results["year2"]["best_time"])

    return render_template(
        "compare_seasons.html",
        user=user,
        athlete=athlete,
        distance=distance,
        style_name=style.style_name,
        season_data=sorted(season_data, key=lambda x: x["year"]),
        compare_results=compare_results,
        year1=year1,
        year2=year2,
        all_seasons_plot=all_seasons_plot,
        compare_plot=compare_plot,
        title=f"Porównanie sezonami ({distance} m - {style.style_name})"
    )

def format_seconds_to_time(seconds):
    """Konwertowanie sekundy na format MM:SS.ss"""
    if seconds is None:
        return "Brak danych"
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:05.2f}"



@app.route("/compare_athletes", methods=["GET", "POST"])
@login_required
def compare_athletes():
    distances = db.session.query(SwimmingStyle.distance).distinct().all()
    styles = db.session.query(SwimmingStyle.style_name).distinct().all()
    genders = db.session.query(User.gender).distinct().all()
    
    athletes = []
    selected_distance = request.form.get("distance")
    selected_style = request.form.get("style")
    selected_gender = request.form.get("gender")

    if selected_distance and selected_style and selected_gender:
        athletes = (
            db.session.query(User)
            .join(Result, User.id_user == Result.id_user)
            .join(SwimmingStyle, Result.id_style == SwimmingStyle.id_style)
            .filter(
                SwimmingStyle.distance == int(selected_distance),
                SwimmingStyle.style_name == selected_style,
                User.gender == selected_gender,
                User.club_id == current_user.club_id  # 🏊‍♂️ Filtracja zawodników z tego samego klubu
            )
            .distinct()
            .all()
        )

    return render_template(
        "compare_athletes.html",
        distances=[str(d[0]) for d in distances],
        styles=[s[0] for s in styles],
        genders=[g[0] for g in genders],
        athletes=athletes,
        selected_distance=selected_distance,
        selected_style=selected_style,
        selected_gender=selected_gender
    )


@app.route("/compare_results", methods=["POST"])
@login_required
def compare_results():
    athlete1_id = request.form.get("athlete1")
    athlete2_id = request.form.get("athlete2")
    selected_distance = request.form.get("distance")
    selected_style = request.form.get("style")

    if not athlete1_id or not athlete2_id:
        flash("Musisz wybrać dwóch zawodników.", "danger")
        return redirect(url_for("compare_athletes"))

    athlete1 = User.query.get_or_404(athlete1_id)
    athlete2 = User.query.get_or_404(athlete2_id)

    # Sprawdzenie czy zawodnicy są w tym samym klubie
    if athlete1.club_id != athlete2.club_id:
        flash("Zawodnicy muszą należeć do tego samego klubu!", "warning")
        return redirect(url_for("compare_athletes"))

    # Pobranie wszystkich wyników pasujących do dystansu i stylu
    results1 = Result.query.join(SwimmingStyle).filter(
        Result.id_user == athlete1_id,
        SwimmingStyle.distance == int(selected_distance),
        SwimmingStyle.style_name == selected_style
    ).order_by(Result.distance_time).all()

    results2 = Result.query.join(SwimmingStyle).filter(
        Result.id_user == athlete2_id,
        SwimmingStyle.distance == int(selected_distance),
        SwimmingStyle.style_name == selected_style
    ).order_by(Result.distance_time).all()

    if not results1 or not results2:
        flash("Nie znaleziono wyników dla wybranych zawodników!", "warning")
        return redirect(url_for("compare_athletes"))

    return render_template(
        "compare_results.html",
        athlete1=athlete1,
        athlete2=athlete2,
        results1=results1,
        results2=results2
    )

@app.route("/compare_final", methods=["POST"])
@login_required
def compare_final():
    athlete1_id = request.form.get("athlete1_id")
    athlete2_id = request.form.get("athlete2_id")
    result1_id = request.form.get("result1_id")
    result2_id = request.form.get("result2_id")

    result1 = Result.query.get_or_404(result1_id)
    result2 = Result.query.get_or_404(result2_id)

    # Obliczanie różnicy czasów
    time_diff = round(abs(result1.distance_time - result2.distance_time), 2)
    reaction_diff = round(abs(result1.reaction_time - result2.reaction_time), 2)

    return render_template(
        "compare_final.html",
        result1=result1,
        result2=result2,
        time_diff=time_diff,
        reaction_diff=reaction_diff
    )

@app.route("/add_result", methods=["GET", "POST"])
@login_required
def add_result():
    if current_user.id_role != 2:  # Tylko trenerzy mogą dodawać wyniki
        flash("Nie masz uprawnień do dodawania wyników!", "danger")
        return redirect(url_for("index"))

    athletes = User.query.filter_by(id_role=3, club_id=current_user.club_id).all()

    competitions = (
        db.session.query(Competition)
        .join(Result, Competition.id_competition == Result.id_competition)
        .join(User, Result.id_user == User.id_user)
        .filter(User.club_id == current_user.club_id)
        .distinct()
        .order_by(Competition.competition_date.desc())
        .all()
    )

    styles = SwimmingStyle.query.distinct().all()

    if request.method == "POST":
        athlete_id = request.form.get("athlete_id")
        competition_id = request.form.get("competition_id")
        new_competition_name = request.form.get("new_competition_name")
        new_competition_city = request.form.get("new_competition_city")
        new_competition_date = request.form.get("new_competition_date")
        style_id = request.form.get("style_id")
        time_input = request.form.get("time")  # Czas w MM:SS.SS lub SS.SS
        reaction_time = request.form.get("reaction_time")  # Czas reakcji w SS.SS

        # Walidacja, czy wszystkie pola są uzupełnione
        if not all([athlete_id, style_id, time_input, reaction_time]):
            flash("Wszystkie pola muszą być uzupełnione!", "danger")
            return redirect(url_for("add_result"))

        # Jeśli trener dodał nowe zawody, zapisujemy je w bazie
        if new_competition_name and new_competition_city and new_competition_date:
            new_competition = Competition(
                competition_name=new_competition_name,
                competition_city=new_competition_city,
                competition_date=datetime.strptime(new_competition_date, "%Y-%m-%d"),
                id_club=current_user.club_id
            )
            db.session.add(new_competition)
            db.session.commit()
            competition_id = new_competition.id_competition

        # **Logowanie do sprawdzenia id_club** 
        print(f"Trener: {current_user.club_id}, Zawody: {competition_id}")

        # Walidacja, czy zawody należą do klubu
        if competition_id:
            valid_competition = Competition.query.filter_by(
                id_competition=competition_id, id_club=current_user.club_id
            ).first()
            
            # **Logowanie wyników zapytania**
            print(f"Sprawdzanie czy zawody {competition_id} należą do klubu {current_user.club_id}: {valid_competition}")

            if not valid_competition:
                flash("Błąd: Nie możesz dodać wyniku do zawodów spoza Twojego klubu!", "danger")
                return redirect(url_for("add_result"))

        # Zapamiętanie oryginalnego formatu czasu
        formatted_time = time_input.strip()

        # Konwersja czasu na sekundy
        try:
            time_parts = time_input.split(":")
            if len(time_parts) == 2:  # Format MM:SS.SS
                minutes = int(time_parts[0])
                seconds = float(time_parts[1])

                if minutes >= 60:
                    flash("Błąd: Minuty nie mogą być większe niż 59!", "danger")
                    return redirect(url_for("add_result"))

                total_seconds = minutes * 60 + seconds
            else:  # Format SS.SS
                total_seconds = float(time_parts[0])

            # Walidacja czasu reakcji
            reaction_time = float(reaction_time)

            if reaction_time < 0 or reaction_time > 2.0:
                flash("Błąd: Czas reakcji musi być w przedziale 0-2 sekundy!", "danger")
                return redirect(url_for("add_result"))

        except ValueError:
            flash("Błąd w formacie czasu lub reakcji! Użyj MM:SS.SS lub SS.SS.", "danger")
            return redirect(url_for("add_result"))

        athlete = User.query.get(athlete_id)
        if not athlete:
            flash("Nie znaleziono zawodnika!", "danger")
            return redirect(url_for("add_result"))

        # Zapisanie wyniku w bazie
        new_result = Result(
            id_user=athlete_id,
            id_club=athlete.club_id,
            id_competition=competition_id,
            id_style=style_id,
            distance_time=total_seconds,  # Przechowywanie w sekundach
            formatted_time=formatted_time,  # Oryginalny format czasu
            reaction_time=reaction_time
        )

        db.session.add(new_result)
        db.session.commit()
        flash("Wynik został dodany pomyślnie!", "success")
        return redirect(url_for("index"))  # Po zapisaniu wyniku przekierowanie na stronę główną

    return render_template(
        "add_result.html",
        athletes=athletes,
        competitions=competitions,
        styles=styles
    )


@app.route("/club_competitions", methods=["GET"])
@login_required
def club_competitions():
    # Sprawdzenie, czy użytkownik jest trenerem
    if current_user.id_role != 2:
        flash("Nie masz uprawnień do przeglądania tej strony!", "danger")
        return redirect(url_for("profile", user_id=current_user.id_user))

    # Pobranie zawodów, w których uczestniczyli zawodnicy z klubu trenera
    competitions = (
        db.session.query(Competition, db.func.count(Result.id_user).label("num_athletes"))
        .join(Result, Competition.id_competition == Result.id_competition)
        .join(User, Result.id_user == User.id_user)
        .filter(User.club_id == current_user.club_id)
        .group_by(Competition.id_competition)
        .order_by(Competition.competition_date.desc())  # Sortowanie od najnowszych
        .all()
    )

    return render_template("club_competitions.html", competitions=competitions)


@app.route("/competition/<int:competition_id>")
@login_required
def competition_details(competition_id):
    # Pobranie zawodów
    competition = Competition.query.get_or_404(competition_id)

    # Sprawdzenie, czy trener ma dostęp do zawodów (czy jego zawodnicy tam startowali)
    results = (
        db.session.query(Result, User, SwimmingStyle)
        .join(User, Result.id_user == User.id_user)
        .join(SwimmingStyle, Result.id_style == SwimmingStyle.id_style)
        .filter(Result.id_competition == competition_id, User.club_id == current_user.club_id)
        .order_by(User.last_name, SwimmingStyle.distance)
        .all()
    )

    if not results:
        flash("Brak wyników dla tych zawodów w Twoim klubie.", "warning")
        return redirect(url_for("club_competitions"))

    return render_template("competition_details.html", competition=competition, results=results)

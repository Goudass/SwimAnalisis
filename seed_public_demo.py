"""
Publiczne dane demonstracyjne — fikcyjne imiona i maile (domena .invalid z RFC 2606).

Użycie (z katalogu głównego projektu, aktywne .venv):
  export FLASK_APP=run.py   # Windows: set FLASK_APP=run.py
  flask db upgrade          # jeśli baza jeszcze bez tabel
  python seed_public_demo.py --force

--force  : usuwa treningi, wyniki, użytkowników, zawody i kluby, potem wstawia zestaw demo.
Bez flagi: jeśli w bazie są już użytkownicy — nic nie robi (bezpieczniejsze na przypadkową pomyłkę).

Hasło dla WSZYSTKICH kont demo (po seedzie uruchom opcjonalnie):
  python reset_dev_passwords.py
(domyslnie to samo hasło co w README: SwimDemo2026!)
"""
from __future__ import annotations

import argparse
from datetime import date, datetime

from werkzeug.security import generate_password_hash

from app import app, db
from app.models import (
    Club,
    Competition,
    Result,
    Role,
    SwimmingStyle,
    TrainingBlock,
    TrainingRep,
    TrainingSession,
    User,
)

DEMO_PASSWORD = "SwimDemo2026!"

# Fikcyjne konta — bezpieczne do publicznego repo (brak prawdziwych osób)
DEMO_USERS = [
    # user_name, last_name, gender, birth, email, id_role, club_index (0=klub admina, 1=klub sportowy)
    ("Admin", "Demo", "M", date(1990, 1, 1), "admin.demo@swimanalisis.invalid", 1, 0),
    ("Tomasz", "Trenerson", "M", date(1985, 5, 10), "trener.demo@swimanalisis.invalid", 2, 1),
    ("Zuzanna", "Zawodniczka", "K", date(2008, 3, 15), "zawodnik.demo@swimanalisis.invalid", 3, 1),
    ("Adam", "Aquatic", "M", date(2009, 7, 22), "zawodnik2.demo@swimanalisis.invalid", 3, 1),
]

DEMO_CLUBS = [
    ("Klub administracyjny (demo)", "—"),
    ("UK Demo Aquatica", "Warszawa"),
]

# (distance, style_name) — minimalny zestaw pod wyniki i filtry w aplikacji
DEMO_STYLES = [
    (50, "Dowolny"),
    (100, "Dowolny"),
    (200, "Dowolny"),
    (50, "Grzbietowy"),
    (100, "Klasyczny"),
    (50, "Motylkowy"),
]


def _fmt_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    sec = seconds % 60
    if minutes > 0:
        s = f"{minutes}:{sec:05.2f}"
    else:
        s = f"{sec:.2f}"
    return s[:10]


def _ensure_roles():
    if Role.query.count() >= 3:
        return
    for rid, name in [(1, "Admin"), (2, "Trener"), (3, "Zawodnik")]:
        if Role.query.filter_by(id_role=rid).first() is None:
            db.session.add(Role(id_role=rid, role_name=name))
    db.session.commit()


def _ensure_styles():
    if SwimmingStyle.query.first():
        return
    for dist, name in DEMO_STYLES:
        db.session.add(SwimmingStyle(distance=dist, style_name=name))
    db.session.commit()


def _wipe_training_and_results():
    TrainingRep.query.delete()
    TrainingBlock.query.delete()
    TrainingSession.query.delete()
    Result.query.delete()
    db.session.commit()


def _wipe_users_competitions_clubs():
    User.query.delete()
    Competition.query.delete()
    Club.query.delete()
    db.session.commit()


def _seed_clubs() -> list[Club]:
    clubs = []
    for name, city in DEMO_CLUBS:
        c = Club(club_name=name, club_city=city)
        db.session.add(c)
        clubs.append(c)
    db.session.flush()
    return clubs


def _seed_users(clubs: list[Club], pwd_hash: str) -> dict[str, User]:
    by_email = {}
    for user_name, last_name, gender, birth, email, id_role, club_idx in DEMO_USERS:
        u = User(
            user_name=user_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=birth,
            email_address=email,
            password_hash=pwd_hash,
            id_role=id_role,
            club_id=clubs[club_idx].id_club,
        )
        db.session.add(u)
        db.session.flush()
        by_email[email] = u
    db.session.commit()
    return by_email


def _seed_competitions(club: Club) -> list[Competition]:
    rows = [
        ("Letnie Zawody Demo", "Warszawa", date(2018, 6, 15)),
        ("Zimowe Zawody Demo", "Kraków", date(2019, 12, 10)),
        ("Wiosenne Zawody Demo", "Poznań", date(2020, 4, 20)),
        ("Jesienne Zawody Demo", "Gdańsk", date(2021, 10, 5)),
        ("Międzynarodowe Demo", "Warszawa", date(2022, 8, 25)),
        ("Mistrzostwa Demo", "Łódź", date(2023, 3, 10)),
    ]
    out = []
    for comp_name, city, d in rows:
        c = Competition(
            competition_name=comp_name,
            competition_city=city,
            competition_date=d,
            id_club=club.id_club,
        )
        db.session.add(c)
        out.append(c)
    db.session.flush()
    db.session.commit()
    return out


def _seed_results(athlete: User, club: Club, competitions: list[Competition], style: SwimmingStyle):
    times_reactions = [
        (32.12, 0.80),
        (28.75, 0.70),
        (27.10, 0.60),
        (29.95, 0.66),
        (28.70, 0.62),
        (26.50, 0.52),
    ]
    for comp, (tsec, react) in zip(competitions, times_reactions):
        db.session.add(
            Result(
                id_user=athlete.id_user,
                id_club=club.id_club,
                id_competition=comp.id_competition,
                id_style=style.id_style,
                distance_time=tsec,
                formatted_time=_fmt_time(tsec),
                reaction_time=react,
            )
        )
    db.session.commit()


def run_force():
    pwd_hash = generate_password_hash(DEMO_PASSWORD)
    with app.app_context():
        _ensure_roles()
        _ensure_styles()

        _wipe_training_and_results()
        _wipe_users_competitions_clubs()

        clubs = _seed_clubs()
        users = _seed_users(clubs, pwd_hash)
        sport_club = clubs[1]
        comps = _seed_competitions(sport_club)

        style = SwimmingStyle.query.filter_by(distance=50, style_name="Dowolny").first()
        if not style:
            raise RuntimeError("Brak stylu 50 m Dowolny — sprawdź migracje / _ensure_styles.")

        athlete = users["zawodnik.demo@swimanalisis.invalid"]
        _seed_results(athlete, sport_club, comps, style)

        print("✅ Baza demo gotowa.")
        print(f"   Wspólne hasło dla wszystkich kont: {DEMO_PASSWORD}")
        print("   Logowanie (e-mail):")
        for _, _, _, _, email, _, _ in DEMO_USERS:
            print(f"     - {email}")
        print("\n   (Opcjonalnie) ujednolicenie haseł na świeżo: python reset_dev_passwords.py")


def main():
    parser = argparse.ArgumentParser(description="Seed publicznych danych demo (fikcyjne maile).")
    parser.add_argument("--force", action="store_true", help="Wyczyść użytkowników/wyniki/zawody/kluby i wstaw demo.")
    args = parser.parse_args()

    if not args.force:
        with app.app_context():
            n = User.query.count()
            if n:
                print(f"W bazie jest już {n} użytkownik(ów). Ponowny seed wymaga: python seed_public_demo.py --force")
            else:
                print("Baza pusta — uruchamiam seed demo (--force).")
                run_force()
        return

    run_force()


if __name__ == "__main__":
    main()

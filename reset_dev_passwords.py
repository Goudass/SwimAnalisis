"""
Jednorazowy reset haseł — ustawia to samo hasło dla wszystkich użytkowników w bazie (lokalny dev).

Uruchom z katalogu projektu:
  source .venv/bin/activate
  python reset_dev_passwords.py

Opcjonalnie własne hasło (min. 6 znaków — wymóg formularza logowania):
  SWIM_DEV_PASSWORD='TwojeHaslo!' python reset_dev_passwords.py

Domyślne hasło zgodne z README / seed_public_demo: SwimDemo2026!
"""
import os

from werkzeug.security import generate_password_hash

from app import app, db
from app.models import User


def main() -> None:
    new_password = os.environ.get("SWIM_DEV_PASSWORD", "SwimDemo2026!")
    if len(new_password) < 6:
        print("Hasło musi mieć co najmniej 6 znaków.")
        raise SystemExit(1)

    with app.app_context():
        users = User.query.order_by(User.id_user).all()
        if not users:
            print("Brak użytkowników w bazie.")
            return

        h = generate_password_hash(new_password)
        for u in users:
            u.password_hash = h
        db.session.commit()

        print(f"Zaktualizowano {len(users)} kont.")
        print(f"Wspólne hasło: {new_password}\n")
        print("E-mail (logowanie):")
        for u in users:
            print(f"  {u.email_address}")


if __name__ == "__main__":
    main()

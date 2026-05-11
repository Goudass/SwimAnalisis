# SwimAnalisis

**EN:** Flask web app for swimming club results: roles (admin, coach, athlete), statistics, charts, and athlete comparisons.  
**PL:** Aplikacja webowa do zbierania i analizy wyników pływackich w klubie — role, statystyki, wykresy, porównania zawodników.

Projekt **portfolio** (własna inicjatywa). Repozytorium: [github.com/Goudass/SwimAnalisis](https://github.com/Goudass/SwimAnalisis).

<!-- Opcjonalnie: screen + link do demo -->
<!-- ![Podgląd aplikacji](docs/screenshot.png) -->
<!-- **Demo:** _brak publicznego hostingu — uruchomienie lokalne poniżej_ -->

---

## Dlaczego warto spojrzeć (rekrutacja)

- **Pełny stack backend + UI:** serwer w Pythonie, relacyjna baza, migracje, formularze, sesje użytkownika.
- **Domena zrozumiała w kodzie:** modele (użytkownik, klub, zawody, styl, wynik), uprawnienia wg roli, CRUD w panelu admina.
- **Analityka w praktyce:** agregacje, wizualizacje (Matplotlib), proste analizy trendu — nie tylko „CRUD na szkoleniu”.

---

## Funkcjonalności (skrót)

| Obszar | Opis |
|--------|------|
| **Konta** | Rejestracja, logowanie, wylogowanie, edycja profilu |
| **Role** | Admin, trener, zawodnik — różne widoki i uprawnienia |
| **Admin** | Zarządzanie użytkownikami, klubami, zawodami, wynikami |
| **Trener** | Lista zawodników klubu, dodawanie wyników, statystyki opisowe i trend dla dystansu, porównanie sezonów |
| **Zawodnik** | Profil, wyniki, rekordy życiowe, progresja z wykresem |
| **Porównania** | Porównanie zawodników i wybranych wyników |
| **Integracja** | API OpenAI (opcjonalnie, klucz w `.env`) — rozszerzenia analityczne |

---

## Stack techniczny

- **Python 3**, **Flask** — routing, szablony Jinja2  
- **SQLAlchemy** + **SQLite** — persystencja  
- **Flask-Migrate (Alembic)** — wersjonowanie schematu bazy  
- **Flask-Login** — sesje; **Werkzeug** — hash haseł  
- **Flask-WTF / WTForms** — formularze  
- **Matplotlib**, **NumPy** — wykresy i proste modele na wynikach  
- **OpenAI** (SDK) — konfigurowalny klucz środowiskowy  

---

## Uruchomienie lokalne

```bash
git clone https://github.com/Goudass/SwimAnalisis.git
cd SwimAnalisis

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Uzupełnij w .env: SECRET_KEY, opcjonalnie OPENAI_API_KEY
```

**Baza:** w repozytorium **nie ma** pliku `app.db` (jest w `.gitignore`). Lokalnie możesz podłożyć własny `app.db` w katalogu głównym albo zbudować schemat migracjami (`flask db upgrade` przy ustawionym `FLASK_APP`) i zasilić dane skryptem `seed.py` — zależnie od tego, jak konfigurujesz środowisko.

```bash
python run.py
```

Aplikacja domyślnie: **http://127.0.0.1:5001** (port 5000 bywa zajęty na macOS przez AirPlay).

---

## Struktura repozytorium (skrót)

```
app/            # aplikacja Flask: modele, trasy, formularze, szablony, statyczne
analysis/       # logika trendu / wykresów
migrations/     # Alembic
run.py          # punkt wejścia serwera deweloperskiego
requirements.txt
```

---

## Licencja

Projekt na licencji **MIT** — szczegóły w pliku [`LICENSE`](LICENSE).

Możesz swobodnie używać, modyfikować i rozpowszechniać kod, pod warunkiem zachowania informacji o prawach autorskich i treści licencji MIT.

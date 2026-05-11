# SwimAnalisis

Aplikacja webowa (**Flask**) dla **klubu pływackiego**: wyniki z **zawodów**, prosta **analiza i wykresy**, oraz **dziennik treningowy** (serie startów z pomiarem **czasu**, **tętna (HR)** i **laktatu** — jeden wiersz = jedno powtórzenie).

Repozytorium: [github.com/Goudass/SwimAnalisis](https://github.com/Goudass/SwimAnalisis) · licencja: [MIT](LICENSE).

---

## Wymagania wstępne

| Element | Wymaganie |
|--------|-----------|
| **Python** | **3.10 lub nowszy** (zalecane **3.11+**). Starsze / „systemowe” buildy mogą nie udostępniać `hashlib.scrypt`, a hasła w bazie są weryfikowane przez **Werkzeug** z użyciem **scrypt** — wtedy logowanie kończy się błędem. **Bezpieczny wybór:** instalacja z [python.org](https://www.python.org/downloads/) albo **Miniconda / Anaconda**. |
| **Git** | Do klonowania repozytorium (opcjonalnie, jeśli masz już kopię ZIP — pomiń `git clone`). |
| **Przeglądarka** | Dowolna aktualna (Chrome, Edge, Firefox, Safari). |

---

## Szybki start (wspólne kroki)

1. **Sklonuj repozytorium** (albo rozpakuj archiwum do folderu `SwimAnalisis`).

   ```bash
   git clone https://github.com/Goudass/SwimAnalisis.git
   cd SwimAnalisis
   ```

2. **Utwórz wirtualne środowisko** w podfolderze `.venv` (nazwa jest w `.gitignore` — nie trafia na GitHub).

3. **Zainstaluj zależności:** `pip install -r requirements.txt`

4. **Skonfiguruj zmienne środowiskowe:** skopiuj `.env.example` → `.env` i uzupełnij (szczegóły w sekcji [Zmienne środowiskowe](#zmienne-środowiskowe)).

5. **Baza danych:** aplikacja domyślnie używa pliku **`app.db` w katalogu głównym projektu** (ścieżka w kodzie: `sqlite:///app.db`). W repozytorium **nie ma** `app.db` (`.gitignore`).  
   - **Opcja A:** skopiuj istniejący plik `app.db` do głównego katalogu projektu.  
   - **Opcja B:** utwórz pustą bazę migracjami (sekcja [Migracje bazy danych](#migracje-bazy-danych-alembic)).

6. **Uruchom serwer:** `python run.py`  
   Domyślny adres: **http://127.0.0.1:5001/** (port można zmienić zmienną `PORT`).

---

## Instalacja — **Windows** (PowerShell lub CMD)

Wszystkie polecenia wykonuj w katalogu projektu, np. `C:\Users\TwojLogin\Desktop\SwimAnalisis`.

### 1. Python i venv

```powershell
cd C:\sciezka\do\SwimAnalisis
py -3.12 -m venv .venv
```

Aktywacja środowiska:

```powershell
.\.venv\Scripts\Activate.ps1
```

*(W CMD zamiast tego: `.\.venv\Scripts\activate.bat`)*

### 2. Zależności

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Plik `.env`

```powershell
copy .env.example .env
```

Otwórz `.env` w edytorze i ustaw przynajmniej `SECRET_KEY` (długi losowy ciąg). `OPENAI_API_KEY` jest opcjonalny.

### 4. Migracje (gdy nie masz gotowego `app.db`)

```powershell
set FLASK_APP=run.py
flask db upgrade
```

### 5. Start aplikacji

```powershell
python run.py
```

W przeglądarce: **http://127.0.0.1:5001/**

Inny port (np. gdy 5001 jest zajęty):

```powershell
set PORT=8080
python run.py
```

→ wtedy adres: **http://127.0.0.1:8080/**

---

## Instalacja — **macOS** (Terminal, zsh)

### 1. Python i venv

Użyj Pythona z **python.org**, **Homebrew** (`brew install python@3.12`) lub **Minicondy** — unikaj samego `/usr/bin/python3` z macOS, jeśli `python3 -c "import hashlib; print(hasattr(hashlib,'scrypt'))"` zwraca `False`.

```bash
cd /Users/twoj_login/Desktop/SwimAnalisis
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Zależności

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Plik `.env`

```bash
cp .env.example .env
```

Uzupełnij `SECRET_KEY` (wymagane do sesji). `OPENAI_API_KEY` — opcjonalnie.

### 4. Migracje (gdy nie masz gotowego `app.db`)

```bash
export FLASK_APP=run.py
flask db upgrade
```

*(W jednej linii: `FLASK_APP=run.py flask db upgrade`)*

### 5. Start aplikacji

```bash
python run.py
```

Adres: **http://127.0.0.1:5001/**

Na macOS port **5000** często zajmuje **AirPlay Receiver** — dlatego w `run.py` domyślnie jest **5001**. Zmiana portu:

```bash
export PORT=8080
python run.py
```

---

## Zmienne środowiskowe

Plik **`.env`** (w katalogu głównym projektu, **nie commituj** go do Gita):

| Zmienna | Obowiązkowa | Opis |
|---------|-------------|------|
| `SECRET_KEY` | **Tak** (produkcja / sensowny dev) | Tajny klucz Flask do podpisania sesji. W pliku `.env.example` jest przykład — **zastąp** własnym długim ciągiem. |
| `OPENAI_API_KEY` | Nie | Klucz API OpenAI — tylko jeśli używasz funkcji korzystających z API w kodzie. |

W kodzie używane jest `python-dotenv` (`load_dotenv()` w `app/__init__.py`).

---

## Migracje bazy danych (Alembic)

Schemat bazy jest wersjonowany w **`migrations/versions/`**. Po sklonowaniu repozytorium **bez** pliku `app.db`:

1. Utwórz `.env` z `SECRET_KEY`.
2. Ustaw `FLASK_APP=run.py` (Windows: `set`, macOS/Linux: `export`).
3. Wykonaj:

   ```bash
   flask db upgrade
   ```

Powstanie plik **`app.db`** w katalogu roboczym (zwykle tam, gdzie uruchamiasz `flask` / `python run.py` — czyli **katalog główny projektu**).

**Kolejność migracji** jest zapisana w plikach migracji (`revision` / `down_revision`). Najnowsza logika obejmuje m.in. tabele **dziennika treningowego** (`training_session`, `training_block`, `training_rep`).

---

## Jak działa aplikacja (logika biznesowa)

### Role

| Rola | Dostęp (skrót) |
|------|----------------|
| **Admin** | Panel CRUD: użytkownicy, kluby, zawody, wyniki; dostęp do **dziennika treningowego** w ramach **swojego klubu** (`club_id` użytkownika). |
| **Trener** | Zawodnicy klubu, dodawanie wyników z zawodów, porównania, statystyki/trendy; **dziennik treningowy** — treningi **wszystkich zawodników** z klubu, możliwość zakładania wpisów w czyimś imieniu. |
| **Zawodnik** | Własny profil, wyniki, rekordy życiowe, progresja; **dziennik** — tylko **własne** treningi, możliwość samodzielnego zakładania wpisów i uzupełniania serii. |

Uwierzytelnianie: **Flask-Login**; hasła — **Werkzeug** (`pbkdf2` / `scrypt` w zależności od wersji — istniejąca baza może używać `scrypt`).

### Moduł „wyniki z zawodów”

- Wynik jest powiązany z: **zawodnikiem**, **klubem**, **zawodami**, **stylem** (dystans + nazwa stylu), **czasem** (sekundy + pole tekstowe formatu), **czasem reakcji**.
- Trener dodaje wyniki w kontekście swojego klubu; admin zarządza globalnie w panelu `/admin/...`.

### Moduł „dziennik treningowy”

Ścieżki URL:

| Metoda / URL | Opis |
|--------------|------|
| `GET /training` | Lista treningów (filtrowana wg roli i klubu). |
| `GET/POST /training/new` | Nowy wpis dziennika: data, tytuł, typ (np. beztlen), notatki; trener wybiera **zawodnika** z listy, zawodnik zapisuje **tylko dla siebie**. |
| `GET /training/<id>` | Szczegóły: serie (**bloki**) i tabela **powtórzeń**. |
| `GET/POST /training/<id>/block/new` | Nowa seria: nazwa (np. `8 × 50 m beztlen`), opcjonalnie dystans w metrach, **liczba powtórzeń** (1–60). System tworzy **N wierszy** `TrainingRep` (puste pola do uzupełnienia). |
| `POST /training/block/<id>/save-reps` | Zapis pól: dla każdego powtórzenia **czas** (format `MM:SS.ss` lub `SS.ss`), **HR**, **laktat** (mmol/L), krótka notatka. |
| `POST .../delete` | Usuwanie serii lub całego treningu (z potwierdzeniem w przeglądarce). |

**Zasada danych:** jedno **powtórzenie** = jeden wiersz w bazie = jeden zestaw: czas + HR + laktat (zgodnie z założeniem projektu).

W menu bocznym pozycja: **„Dziennik treningowy”**.

---

## Punkt wejścia i konfiguracja serwera

- **`run.py`** — importuje `app` z pakietu `app`, uruchamia `app.run(debug=True, port=...)`.
- **Port:** domyślnie **5001**; nadpisanie: zmienna środowiskowa **`PORT`** (np. `8080`).
- **`app/__init__.py`** — fabryka aplikacji: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI` (`sqlite:///app.db`), rozszerzenia (`db`, `migrate`, `login_manager`, …), import tras: `routes`, `training_routes`.

Tryb **`debug=True`** jest przeznaczony **tylko do developmentu** — nie używaj tego bez zmian na publicznym serwerze produkcyjnym.

---

## Przydatne skrypty (lokalnie)

| Plik | Zastosowanie |
|------|----------------|
| `reset_dev_passwords.py` | Jednorazowy reset haseł **wszystkich** użytkowników w `app.db` na wspólne hasło dev (domyślnie zdefiniowane w skrypcie lub przez `SWIM_DEV_PASSWORD`). **Tylko środowisko developerskie.** |
| `seed.py` | Skrypt zasiewania danych — treść zależy od wersji w repozytorium; używaj świadomie, żeby nie nadpisać produkcyjnej bazy. |

---

## Publiczne repo — dane demonstracyjne (fikcyjne maile i jedno hasło)

W repozytorium **nie ma** prawdziwych danych osobowych. Do pokazu rekruterom / szybkiego startu lokalnie:

### Hasło testowe (wszystkie konta demo)

**`SwimDemo2026!`**

Po załadowaniu bazy demo każdy użytkownik ma to samo hasło (algorytm hash w bazie). Możesz je ponownie ustawić dla **wszystkich** kont w `app.db`:

```bash
python reset_dev_passwords.py
```

(opcjonalnie: `SWIM_DEV_PASSWORD='InneHaslo!' python reset_dev_passwords.py`)

### Konta logowania (e-mail → rola)

| E-mail (login) | Rola |
|----------------|------|
| `admin.demo@swimanalisis.invalid` | Admin |
| `trener.demo@swimanalisis.invalid` | Trener |
| `zawodnik.demo@swimanalisis.invalid` | Zawodnik (ma przykładowe wyniki z zawodów) |
| `zawodnik2.demo@swimanalisis.invalid` | Zawodnik |

Domena **`.invalid`** jest zarezerwowana (RFC 2606) — nie wyśle się na nią prawdziwy mail.

### Jak zbudować / nadpisać bazę demo

**Uwaga:** poniższa komenda **usuwa** obecnych użytkowników, wyniki, zawody, kluby oraz wpisy **dziennika treningowego** w `app.db` i wstawia zestaw fikcyjny.

```bash
cd SwimAnalisis   # katalog projektu
source .venv/bin/activate          # Windows: .venv\Scripts\activate
export FLASK_APP=run.py            # Windows: set FLASK_APP=run.py
flask db upgrade                   # jeśli tabele jeszcze nie istnieją
python seed_public_demo.py --force
```

Skrypt: `seed_public_demo.py` (w katalogu głównym). Bez flagi `--force`, jeśli w bazie są już użytkownicy, skrypt **nic nie zmieni** (trzeba świadomie podać `--force`).

---

## Struktura katalogów (ważniejsze elementy)

```
SwimAnalisis/
├── run.py                 # Uruchomienie serwera developerskiego
├── requirements.txt       # Zależności pip
├── .env.example           # Wzorzec zmiennych (bez sekretów)
├── LICENSE                # Licencja MIT
├── seed_public_demo.py    # Pełny zestaw kont i danych demo (fikcyjne maile)
├── reset_dev_passwords.py # Ustawia to samo hasło dla wszystkich użytkowników w app.db
├── app/
│   ├── __init__.py        # Inicjalizacja Flask, db, migracje, import tras
│   ├── models.py          # Modele SQLAlchemy (m.in. User, Result, TrainingSession, …)
│   ├── routes.py          # Trasy główne (zawody, profil, admin, …)
│   ├── training_routes.py # Trasy dziennika treningowego
│   ├── forms.py
│   ├── static/            # CSS, obrazy (m.in. style.css, images/)
│   └── templates/         # Szablony Jinja2 (+ podfolder training/)
├── analysis/              # Analiza trendu / wykresy (np. trend.py)
├── migrations/            # Alembic: env.py, versions/*.py
└── static/uploads/        # Uploady (pusty folder z .gitkeep w repo)
```

---

## Rozwiązywanie problemów

| Problem | Działanie |
|---------|-----------|
| `Address already in use` / port zajęty | Ustaw `PORT` na inny (np. `8080`) i uruchom ponownie `python run.py`. |
| `AttributeError: module 'hashlib' has no attribute 'scrypt'` przy logowaniu | Zainstaluj **nowszego Pythona** (np. z python.org lub Minicondy) i **przebuduj `.venv`**. |
| Pusta baza / brak tabel | `FLASK_APP=run.py` oraz `flask db upgrade`. |
| Brak użytkowników po migracji | Załóż konto przez `/register` albo dodaj użytkownika w panelu admina (jeśli masz już admina w bazie). |

---

## Licencja

Projekt na licencji **MIT** — szczegóły w pliku [`LICENSE`](LICENSE).

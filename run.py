import os

from app import app

if __name__ == "__main__":
    # Na macOS port 5000 często zajmuje AirPlay Receiver — domyślnie 5001.
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=True, port=port)
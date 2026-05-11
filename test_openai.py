import openai
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Pobierz klucz API OpenAI z pliku .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Testowa wiadomość do API OpenAI
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem."},
            {"role": "user", "content": "Cześć, jak się masz?"}
        ]
    )
    print("Odpowiedź z API OpenAI:")
    print(response.choices[0].message.content)
except Exception as e:
    print("Wystąpił błąd:")
    print(e)

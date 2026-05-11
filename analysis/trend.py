import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# Ustawienie backendu Matplotlib dla uniknięcia błędów GUI
plt.switch_backend("Agg")

def analyze_trend(dates, times):
    """
    Analizuje trend wyników zawodnika na podstawie regresji liniowej.
    """
    if len(times) < 2:
        return "Za mało danych, aby przeprowadzić analizę trendu."

    try:
        # Konwersja dat na indeksy liczb całkowitych
        x = np.arange(len(dates))  
        y = np.array(times)  

        # Regresja liniowa
        z = np.polyfit(x, y, 1)
        slope = z[0]

        # Wnioski na podstawie trendu
        if slope < 0:
            return "📉 Wyniki zawodnika poprawiają się w czasie."
        elif slope > 0:
            return "📈 Wyniki zawodnika pogarszają się w czasie."
        else:
            return "⚖️ Wyniki zawodnika nie wykazują wyraźnego trendu."
    except Exception as e:
        return f"❌ Błąd analizy trendu: {str(e)}"

def generate_trend_plot(dates, times, formatted_times):
    """
    Generuje wykres trendu wyników zawodnika z sformatowanymi czasami na osi Y.
    """
    if len(times) < 2:
        return None  # Brak danych do wykresu

    try:
        x = np.arange(len(dates))
        z = np.polyfit(x, times, 1)
        p = np.poly1d(z)

        # Tworzymy wykres
        plt.figure(figsize=(10, 5))
        plt.plot(dates, times, marker="o", color="blue", label="Czasy (s)")
        plt.plot(dates, p(x), linestyle="--", color="red", label="Trend")
        plt.gca().invert_yaxis()  # Czasy krótsze są lepsze

        # Ustawienie formatowania osi Y na czasy
        def format_seconds_to_time(seconds):
            """Konwertowanie sekundy na format MM:SS.ss"""
            minutes = int(seconds // 60)
            seconds = seconds % 60
            return f"{minutes:02}:{seconds:05.2f}"

        # Zamiana wartości osi Y na sformatowane czasy
        yticks = plt.gca().get_yticks()
        plt.gca().set_yticklabels([format_seconds_to_time(tick) for tick in yticks])

        # Konfiguracja wykresu
        plt.xlabel("Data zawodów")
        plt.ylabel("Czas (s)")
        plt.title("Trend wyników")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)

        # Zapisanie wykresu do formatu Base64
        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight")
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return plot_url
    except Exception as e:
        print(f"Błąd generowania wykresu: {e}")
        return None


def generate_multi_line_plot(x_labels, avg_times, best_times, title="Wykres wyników"):
    """
    Generuje wieloliniowy wykres dla wyników: średnie czasy, najlepsze czasy i trend.
    """
    if not avg_times or not best_times:
        return None  # Brak danych do wykresu

    try:
        x = np.arange(len(x_labels))  

        # Regresja liniowa dla średnich czasów (trend)
        avg_trend = np.poly1d(np.polyfit(x, avg_times, 1))(x) if avg_times else [0] * len(x)

        plt.figure(figsize=(12, 6))
        plt.plot(x, avg_times, marker="o", color="blue", label="Średni czas (s)")
        plt.plot(x, best_times, marker="o", color="green", label="Najlepszy czas (s)")
        plt.plot(x, avg_trend, linestyle="--", color="red", label="Trend średnich czasów")
        
        plt.gca().invert_yaxis()  # Czasy krótsze są lepsze

        plt.xticks(x, x_labels, rotation=45)
        plt.xlabel("Sezon")
        plt.ylabel("Czas (s)")
        plt.title(f"{title}")
        plt.legend()
        plt.grid(True)

        # Ustawienie formatu na osi Y jako MM:SS.ss
        def format_seconds_to_time(seconds):
            """Konwertowanie sekundy na format MM:SS.ss"""
            minutes = int(seconds // 60)
            seconds = seconds % 60
            return f"{minutes:02}:{seconds:05.2f}"

        yticks = plt.gca().get_yticks()
        plt.gca().set_yticklabels([format_seconds_to_time(tick) for tick in yticks])

        # Konwersja wykresu na obraz w formacie Base64
        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight")
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        return plot_url
    except Exception as e:
        print(f"Błąd generowania wykresu: {e}")
        return None


def generate_bar_chart(labels, times):
    plt.figure(figsize=(8, 5))
    plt.bar(labels, times, color=["blue", "green"])
    plt.xlabel("Zawodnicy")
    plt.ylabel("Czas (s)")
    plt.title("Porównanie wyników")

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

def generate_comparison_plot(athlete1, athlete2, result1, result2):
    """
    Generuje wykres porównujący wyniki dwóch zawodników.
    """
    labels = ["Czas", "Czas reakcji"]
    values1 = [result1.distance_time, result1.reaction_time]
    values2 = [result2.distance_time, result2.reaction_time]

    x = np.arange(len(labels))

    plt.figure(figsize=(8, 5))
    plt.bar(x - 0.2, values1, 0.4, label=f"{athlete1.user_name} {athlete1.last_name}", color="blue")
    plt.bar(x + 0.2, values2, 0.4, label=f"{athlete2.user_name} {athlete2.last_name}", color="green")

    plt.xticks(x, labels)
    plt.ylabel("Czas (s)")
    plt.title("Porównanie wyników zawodników")
    plt.legend()
    plt.grid(axis="y")

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

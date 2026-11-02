import json
from urllib.request import urlopen

LAT, LON = 50.85, 4.37  # Bruxelles
URL = ("https://api.open-meteo.com/v1/forecast"
       f"?latitude={LAT}&longitude={LON}"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min"
       "&timezone=Europe%2FBrussels&forecast_days=2")


def description(code):
    # Traduit le code météo (WMO) en mots, de façon simplifiée
    if code == 0: return "Soleil"
    if code <= 2: return "Éclaircies"
    if code == 3: return "Couvert"
    if code in (45, 48): return "Brouillard"
    if 51 <= code <= 57: return "Bruine"
    if 61 <= code <= 67: return "Pluie"
    if 71 <= code <= 77: return "Neige"
    if 80 <= code <= 82: return "Averses"
    if 85 <= code <= 86: return "Averses de neige"
    if code >= 95: return "Orage"
    return "?"


def meteo():
    # Renvoie [texte pour aujourd'hui, texte pour demain]
    try:
        with urlopen(URL, timeout=10) as reponse:
            d = json.load(reponse)["daily"]
    except Exception:
        return [None, None]  # pas d'Internet : pas de météo, mais pas de panne
    return [f"{description(d['weather_code'][i])}  "
            f"{round(d['temperature_2m_min'][i])}° / {round(d['temperature_2m_max'][i])}°"
            for i in range(2)]


if __name__ == "__main__":
    print(meteo())

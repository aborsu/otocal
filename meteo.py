import json
import math
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
    if 80 <= code <= 82: return "Pluie"
    if 85 <= code <= 86: return "Neige"
    if code >= 95: return "Orage"
    return "?"


def meteo():
    # Renvoie [(type, températures) pour aujourd'hui, idem pour demain]
    try:
        with urlopen(URL, timeout=10) as reponse:
            d = json.load(reponse)["daily"]
    except Exception:
        return [None, None]  # pas d'Internet : pas de météo, mais pas de panne
    return [(description(d["weather_code"][i]),
             f"{round(d['temperature_2m_min'][i])}° / {round(d['temperature_2m_max'][i])}°")
            for i in range(2)]


# ---------- Les icônes ----------
# dn = image noire, dr = image rouge, (cx, cy) = centre, s = taille

def soleil(dr, cx, cy, s):
    r = 0.18 * s
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    for i in range(8):  # 8 rayons
        a = i * math.pi / 4
        dr.line((cx + math.cos(a) * r * 1.4, cy + math.sin(a) * r * 1.4,
                 cx + math.cos(a) * r * 2.1, cy + math.sin(a) * r * 2.1), fill=0, width=3)


def nuage(dn, dr, cx, cy, s):
    # 3 ronds + 1 rectangle = un nuage. On l'efface du rouge pour qu'il passe devant le soleil.
    for dx, dy, r in [(0, -0.08, 0.24), (-0.22, 0.04, 0.17), (0.22, 0.04, 0.17)]:
        boite = (cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s)
        dn.ellipse(boite, fill=0)
        dr.ellipse(boite, fill=255)
    boite = (cx - 0.22 * s, cy + 0.04 * s, cx + 0.22 * s, cy + 0.21 * s)
    dn.rectangle(boite, fill=0)
    dr.rectangle(boite, fill=255)


def icone(dn, dr, type_meteo, cx, cy, s=44):
    if type_meteo == "Soleil":
        soleil(dr, cx, cy, s)
    elif type_meteo == "Éclaircies":
        soleil(dr, cx + 0.15 * s, cy - 0.15 * s, 0.8 * s)
        nuage(dn, dr, cx - 0.05 * s, cy + 0.08 * s, 0.8 * s)
    elif type_meteo == "Couvert":
        nuage(dn, dr, cx, cy, s)
    elif type_meteo == "Brouillard":
        for i in range(3):
            y = cy - 0.2 * s + i * 0.2 * s
            dn.line((cx - 0.35 * s, y, cx + 0.35 * s, y), fill=0, width=3)
    elif type_meteo in ("Bruine", "Pluie", "Neige", "Orage"):
        nuage(dn, dr, cx, cy - 0.12 * s, s)  # le nuage monte pour laisser la place en dessous
        for dx in (-0.2, 0, 0.2):
            x = cx + dx * s
            if type_meteo == "Bruine":
                r = 0.04 * s
                dn.ellipse((x - r, cy + 0.28 * s - r, x + r, cy + 0.28 * s + r), fill=0)
            elif type_meteo == "Pluie":
                dn.line((x, cy + 0.16 * s, x - 0.08 * s, cy + 0.4 * s), fill=0, width=3)
            elif type_meteo == "Neige":
                for y in (cy + 0.2 * s, cy + 0.36 * s):
                    r = 0.05 * s
                    dn.ellipse((x - r, y - r, x + r, y + r), fill=0)
        if type_meteo == "Orage":  # éclair rouge
            points = [(0.05, 0.12), (-0.08, 0.30), (0.02, 0.30), (-0.05, 0.46),
                      (0.12, 0.24), (0.02, 0.24), (0.10, 0.12)]
            dr.polygon([(cx + px * s, cy + py * s) for px, py in points], fill=0)


def dessiner_meteo(dn, dr, prevision, droite, haut, font):
    # Températures alignées à droite, icône juste à gauche
    type_meteo, temperatures = prevision
    dn.text((droite, haut), temperatures, font=font, fill=0, anchor="ra")
    largeur = dn.textlength(temperatures, font=font)
    icone(dn, dr, type_meteo, droite - largeur - 35, haut + 14)


if __name__ == "__main__":
    print(meteo())

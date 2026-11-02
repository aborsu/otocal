from datetime import date, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from evenements import charger_evenements, JOURS
from phrase import phrase_du_jour
from meteo import meteo, dessiner_meteo
from barre_batterie import dessiner_batterie

L, H = 1304, 984  # taille de l'écran en pixels
POLICE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GRAS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
JOURS_LONGS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def police(taille, gras=False):
    return ImageFont.truetype(GRAS if gras else POLICE, taille)


def police_grille(taille=16):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", taille)


def couper(texte, n):
    # Raccourcit un texte trop long avec "…"
    return texte if len(texte) <= n else texte[:n - 1] + "…"


def dessiner():
    # Deux images blanches : une pour l'encre noire, une pour l'encre rouge
    noir = Image.new("1", (L, H), 255)
    rouge = Image.new("1", (L, H), 255)
    dn, dr = ImageDraw.Draw(noir), ImageDraw.Draw(rouge)

    # Ranger les événements par jour (un congé occupe plusieurs jours)
    par_jour = {}
    for e in charger_evenements():
        for i in range(e["duree"] if e["conge"] else 1):
            par_jour.setdefault(e["jour"] + timedelta(days=i), []).append(e)

    # --- Haut : zoom sur aujourd'hui et demain ---
    auj = date.today()
    HAUT = 360
    previsions = meteo()
    for k, (titre, d) in enumerate([("Aujourd'hui", auj), ("Demain", auj + timedelta(days=1))]):
        x = k * L // 2 + 20
        dn.text((x, 15), titre, font=police(26), fill=0)
        if previsions[k]:
            dessiner_meteo(dn, dr, previsions[k], x + L // 2 - 40, 15, police(26))
        dn.text((x, 50), f"{JOURS_LONGS[d.weekday()]} {d.day} {MOIS[d.month - 1]}",
                font=police(44 if k == 0 else 36, gras=True), fill=0)
        y = 120
        for e in par_jour.get(d, [])[:7]:
            ligne = f"{e['heure']}  {e['texte']}".strip()
            (dr if e["rouge"] else dn).text((x, y), couper(ligne, 34), font=police(26), fill=0)
            y += 34
    dn.line((L // 2, 0, L // 2, HAUT), fill=0, width=2)
    dn.line((0, HAUT, L, HAUT), fill=0, width=4)

    # --- Milieu : grille de 4 semaines ---
    lundi = auj - timedelta(days=auj.weekday())
    col = L / 7
    y0 = HAUT + 40
    lig = (H - 50 - y0) / 4
    for j in range(7):
        dn.text((j * col + col / 2, HAUT + 20), JOURS[j], font=police(22, gras=True), fill=0, anchor="mm")
    for s in range(4):
        for j in range(7):
            d = lundi + timedelta(days=7 * s + j)
            x, y = int(j * col), int(y0 + s * lig)
            dn.rectangle((x, y, int((j + 1) * col), int(y0 + (s + 1) * lig)), outline=0, width=1)
            if d == auj:
                dr.rectangle((x, y, int((j + 1) * col), int(y0 + (s + 1) * lig)), outline=0, width=5)
            dn.text((x + 6, y + 4), str(d.day), font=police(22, gras=True), fill=0)
            ty = y + 32
            for e in par_jour.get(d, [])[:4]:
                if e["conge"]:
                    dn.rectangle((x + 3, ty, int(x + col) - 3, ty + 20), fill=0)
                    dn.text((x + 6, ty), couper(e["texte"], 16), font=police_grille(), fill=255)
                else:
                    (dr if e["rouge"] else dn).text((x + 6, ty), couper(e["texte"], 18), font=police_grille(), fill=0)
                ty += 22

    # --- Bas : place pour la météo et la phrase du jour ---
    dn.line((0, H - 50, L, H - 50), fill=0, width=2)
    dn.text((20, H - 38), couper(phrase_du_jour(), 95), font=police(22), fill=0)
    dessiner_batterie(dn, dr, police(22), L, H)
    return noir, rouge


if __name__ == "__main__":
    noir, rouge = dessiner()
    # Fabriquer un aperçu en couleurs pour le regarder sur le Mac
    apercu = Image.new("RGB", (L, H), "white")
    apercu.paste((0, 0, 0), mask=ImageOps.invert(noir.convert("L")))
    apercu.paste((200, 0, 0), mask=ImageOps.invert(rouge.convert("L")))
    apercu.save(Path.home() / "otocal/apercu.png")
    print("Aperçu enregistré !")

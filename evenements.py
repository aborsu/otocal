from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from dotenv import dotenv_values
import caldav

TZ = ZoneInfo("Europe/Brussels")
INITIALES = {"Anne-Christine": "AC", "Augustin": "AB", "Gabriel": "G", "Alois": "AL"}
IGNORER = {"Personnel"}
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]


def court(titre):
    # Raccourcit les anniversaires pour mieux voir le prénom
    for long in ("Anniversaire de ", "Anniversaire d'", "Anniversaire "):
        if titre.startswith(long):
            return "Anniv. " + titre[len(long):]
    return titre


def charger_evenements(nb_jours=28):
    cfg = dotenv_values(Path("/home/otocal/.config/otocal/nextcloud.env"))
    client = caldav.DAVClient(url=cfg["NC_URL"], username=cfg["NC_USER"], password=cfg["NC_PASS"])
    debut = datetime.combine(date.today(), time(0), TZ)
    fin = debut + timedelta(days=nb_jours)

    evenements = []
    deja_vu = set()  # pour ne pas afficher deux fois le même événement
    for cal in client.principal().calendars():
        if cal.name in IGNORER:
            continue
        for ev in cal.search(start=debut, end=fin, event=True, expand=True):
            c = ev.icalendar_component
            titre = str(c.get("SUMMARY", "(sans titre)"))
            dt = c.decoded("DTSTART")
            toute_journee = not isinstance(dt, datetime)
            if not toute_journee:
                dt = dt.astimezone(TZ)

            # Correction 1 : doublon -> on saute
            if (titre, dt) in deja_vu:
                continue
            deja_vu.add((titre, dt))

            duree = 1
            if toute_journee and "DTEND" in c:
                duree = (c.decoded("DTEND") - dt).days

            # Correction 3 : pas d'heure si toute la journée ou 00:00
            heure = "" if toute_journee else dt.strftime("%H:%M")
            if heure == "00:00":
                heure = ""

            ini = INITIALES.get(cal.name)
            evenements.append({
                "jour": dt.date() if isinstance(dt, datetime) else dt,
                "heure": heure,
                "texte": f"{ini} · {court(titre)}" if ini else court(titre),
                # Correction 2 : tout ce qui commence par "Anniversaire" est rouge
                "rouge": cal.name == "Anniversaires des contacts" or titre.startswith("Anniversaire"),
                "conge": cal.name == "Famille" and duree > 1,
                "duree": duree,
            })

    evenements.sort(key=lambda e: (e["jour"], e["heure"]))
    return evenements


# Ce bloc ne s'exécute que si on lance ce fichier directement
if __name__ == "__main__":
    for e in charger_evenements():
        marque = "[ROUGE] " if e["rouge"] else ("[CONGÉ] " if e["conge"] else "")
        print(JOURS[e["jour"].weekday()], f"{e['jour']:%d/%m}", f"{e['heure']:5}", marque + e["texte"])

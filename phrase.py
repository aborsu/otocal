import json
import random
from pathlib import Path

FICHIER = Path("/home/otocal/otocal/phrases.txt")
PIOCHE = Path("/home/otocal/otocal/.pioche_blagues.json")


def lire_blagues():
    try:
        return [l.strip() for l in FICHIER.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return []


def phrase_du_jour():
    # Paquet de cartes : chaque blague sort une fois avant qu'on remélange
    blagues = lire_blagues()
    if not blagues:
        return ""
    try:
        etat = json.loads(PIOCHE.read_text(encoding="utf-8"))
    except Exception:
        etat = {"pioche": [], "derniere": None}
    # On garde seulement les blagues encore présentes dans phrases.txt
    pioche = [b for b in etat.get("pioche", []) if b in blagues]
    if not pioche:
        pioche = blagues[:]
        random.shuffle(pioche)
        # Pas la même blague deux fois de suite au moment du mélange
        if len(pioche) > 1 and pioche[-1] == etat.get("derniere"):
            pioche[0], pioche[-1] = pioche[-1], pioche[0]
    blague = pioche.pop()
    try:
        PIOCHE.write_text(json.dumps({"pioche": pioche, "derniere": blague}, ensure_ascii=False),
                          encoding="utf-8")
    except OSError:
        pass  # si on ne peut pas écrire, on affiche quand même une blague
    return blague


if __name__ == "__main__":
    print(phrase_du_jour())

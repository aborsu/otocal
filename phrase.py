import random
from pathlib import Path

FICHIER = Path("/home/otocal/otocal/phrases.txt")


def phrase_du_jour():
    try:
        lignes = [l.strip() for l in FICHIER.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return ""
    return random.choice(lignes) if lignes else ""  # tirage au sort !


if __name__ == "__main__":
    print(phrase_du_jour())

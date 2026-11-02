import sys
import time
import subprocess
from pathlib import Path
sys.path.append("/home/otocal/12.48inch-e-paper/RaspberryPi/python/lib")
import epd12in48b
from pisugar import commande
from reveil import regler_reveil
from dessin import dessiner

SORTIE_SECOURS = Path("/home/otocal/otocal/RESTER_ALLUME")


def journal(message):
    print(message, flush=True)


# 1. Remettre l'heure du Pi à jour depuis l'horloge du PiSugar
for essai in range(10):
    try:
        journal(commande("rtc_rtc2pi"))
        break
    except Exception:
        time.sleep(3)  # le PiSugar n'est peut-être pas encore prêt

# 2. Dessiner (il faut Internet : on réessaie pendant 2 minutes)
noir = rouge = None
for essai in range(12):
    try:
        noir, rouge = dessiner()
        break
    except Exception as e:
        journal(f"Essai {essai + 1} raté : {e}")
        time.sleep(10)

# 3. Afficher
if noir is not None:
    journal("Envoi à l'écran...")
    epd = epd12in48b.EPD()
    epd.Init()
    epd.display(noir, rouge)
    epd.EPD_Sleep()

# 4. Régler la prochaine alarme
moment, reponse = regler_reveil()
journal(f"Prochain réveil : {moment} ({reponse})")

# 5. S'éteindre, sauf sortie de secours
en_charge = "true" in commande("get battery_charging")
if SORTIE_SECOURS.exists() or en_charge:
    journal("Sortie de secours : je reste allumé.")
else:
    journal("Bonne nuit !")
    subprocess.run(["systemctl", "poweroff"])

import sys
import time
import subprocess
from pathlib import Path
sys.path.append("/home/otocal/12.48inch-e-paper/RaspberryPi/python/lib")
import epd12in48b
from pisugar import commande, batterie
from reveil import regler_reveil
from dessin import dessiner

SORTIE_SECOURS = Path("/home/otocal/otocal/RESTER_ALLUME")


def journal(message):
    print(message, flush=True)


# 1. Heure depuis le PiSugar (on vérifie la réponse, pas seulement l'absence d'erreur)
pisugar_ok = False
for essai in range(10):
    try:
        reponse = commande("rtc_rtc2pi")
        journal(reponse)
        if "done" in reponse:
            pisugar_ok = True
            break
    except Exception as e:
        journal(f"PiSugar pas prêt : {e}")
    time.sleep(3)

if pisugar_ok:
    try:
        journal(f"Batterie : {batterie():.0f} %")
    except Exception as e:
        journal(f"Batterie illisible : {e}")

# 2-3. Dessiner et afficher (une erreur ici ne doit pas empêcher la suite)
try:
    noir = rouge = None
    for essai in range(12):
        try:
            noir, rouge = dessiner()
            break
        except Exception as e:
            journal(f"Essai {essai + 1} raté : {e}")
            time.sleep(10)
    if noir is not None:
        journal("Envoi à l'écran...")
        epd = epd12in48b.EPD()
        epd.Init()
        epd.display(noir, rouge)
        epd.EPD_Sleep()
except Exception as e:
    journal(f"Affichage raté : {e}")

# 4. Prochaine alarme (on insiste : sans alarme, on ne se réveille jamais)
alarme_ok = False
for tentative in range(30):
    try:
        moment, reponse = regler_reveil()
        journal(f"Prochain réveil : {moment} ({reponse})")
        alarme_ok = "done" in reponse
    except Exception as e:
        journal(f"Réveil non réglé : {e}")
    if alarme_ok:
        break
    time.sleep(60)

# 5. S'éteindre seulement si on est sûr de se réveiller
try:
    en_charge = "true" in commande("get battery_charging")
except Exception:
    en_charge = False

if SORTIE_SECOURS.exists():
    journal("Sortie de secours (fichier RESTER_ALLUME) : je reste allumé.")
elif en_charge:
    journal("Sortie de secours (batterie en charge) : je reste allumé.")
elif not alarme_ok:
    journal("Alarme non réglée : je reste allumé pour ne pas dormir pour toujours.")
else:
    journal("Bonne nuit !")
    subprocess.run(["systemctl", "poweroff"])

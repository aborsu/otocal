import sys
sys.path.append("/home/otocal/12.48inch-e-paper/RaspberryPi/python/lib")
import epd12in48b
from dessin import dessiner

print("Dessin du calendrier...")
noir, rouge = dessiner()

print("Envoi à l'écran (environ 2 minutes)...")
epd = epd12in48b.EPD()
epd.Init()                 # réveiller l'écran
epd.display(noir, rouge)   # envoyer les deux images
epd.EPD_Sleep()            # endormir l'écran pour le protéger
print("Terminé !")

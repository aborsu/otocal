from pathlib import Path
from dotenv import dotenv_values
import caldav

# 1. Lire la clé secrète
cfg = dotenv_values(Path.home() / ".config/otocal/nextcloud.env")

# 2. Se connecter au Nextcloud
client = caldav.DAVClient(url=cfg["NC_URL"], username=cfg["NC_USER"], password=cfg["NC_PASS"])
moi = client.principal()

# 3. Afficher chaque calendrier trouvé
print("Calendriers trouvés :")
for cal in moi.calendars():
    print(" -", cal.name)

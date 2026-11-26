from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from pisugar import commande
import subprocess
import time as chrono

TZ = ZoneInfo("Europe/Brussels")
HEURES_REVEIL = [time(6, 0), time(11, 30), time(18, 0)]


def prochain_reveil():
    maintenant = datetime.now(TZ)
    # On regarde aujourd'hui, puis demain
    for jour in range(2):
        d = maintenant.date() + timedelta(days=jour)
        for h in HEURES_REVEIL:
            moment = datetime.combine(d, h, TZ)
            # Marge de 5 minutes, pour ne pas reprendre l'alarme qui vient de sonner
            if moment > maintenant + timedelta(minutes=5):
                return moment


def horloge_synchronisee():
    r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                       capture_output=True, text=True)
    return r.stdout.strip() == "yes"


def regler_reveil(essais=10):
    moment = prochain_reveil()
    if horloge_synchronisee():
        commande("rtc_pi2rtc")  # seulement si heure du Pi fiable
    reponse = ""
    for essai in range(essais):
        try:
            reponse = commande(f"rtc_alarm_set {moment.isoformat()} 127")
            if "done" in reponse:
                break
        except Exception as e:
            reponse = f"erreur : {e}"
        chrono.sleep(3)
    return moment, reponse


if __name__ == "__main__":
    moment, reponse = regler_reveil()
    print("Prochain réveil :", moment.strftime("%A %d/%m à %H:%M"))
    print(reponse)
    print(commande("get rtc_alarm_time"))

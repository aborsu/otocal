from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from pisugar import commande

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


def regler_reveil():
    moment = prochain_reveil()
    commande("rtc_pi2rtc")  # remettre l'horloge à l'heure, par sécurité
    reponse = commande(f"rtc_alarm_set {moment.isoformat()} 127")
    return moment, reponse


if __name__ == "__main__":
    moment, reponse = regler_reveil()
    print("Prochain réveil :", moment.strftime("%A %d/%m à %H:%M"))
    print(reponse)
    print(commande("get rtc_alarm_time"))

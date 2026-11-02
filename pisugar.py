import socket


def commande(cmd):
    # Envoie une commande au PiSugar et renvoie sa réponse
    with socket.create_connection(("127.0.0.1", 8423), timeout=5) as s:
        s.sendall((cmd + "\n").encode())
        return s.recv(1024).decode().strip()


def batterie():
    # La réponse ressemble à "battery: 87.5" -> on garde le nombre
    return float(commande("get battery").split(":")[1])


if __name__ == "__main__":
    print(commande("get battery"))
    print(commande("get battery_charging"))
    print(commande("get rtc_time"))

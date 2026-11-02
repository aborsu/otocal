from pisugar import batterie


def dessiner_batterie(dn, dr, font, L, H):
    try:
        niveau = batterie()
    except Exception:
        return  # pas de PiSugar : on ne dessine rien
    niveau = max(0, min(100, niveau))
    x, y, larg, haut = L - 140, H - 33, 60, 16
    d = dr if niveau < 20 else dn  # rouge si batterie faible
    d.rectangle((x, y, x + larg, y + haut), outline=0, width=2)        # le corps de la pile
    d.rectangle((x + larg, y + 5, x + larg + 4, y + haut - 5), fill=0) # le petit bout
    d.rectangle((x + 3, y + 3, x + 3 + int((larg - 6) * niveau / 100), y + haut - 3), fill=0)  # le remplissage
    d.text((x + larg + 14, y), f"{niveau:.0f}%", font=font, fill=0)

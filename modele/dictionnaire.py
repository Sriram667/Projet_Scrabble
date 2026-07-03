import random
from pathlib import Path

#Il faudra faire dict = Dictionnaire("modele.Dictionnaire_ODS.txt") pour avoir accès au fichier


def _normaliser_mot(mot):
    """Sert à normaliser le mot, en enlevant les espaces et maj."""
    return mot.strip().upper()


class Dictionnaire:
    """Classe donnant accès à un dictionnaire de mots."""

    def __init__(self, localisation_fichier):
        self.localisation_fichier = str(localisation_fichier)
        self.dict_mots = set() # Nous sert à chercher rapidement si un mot est valide
        self._liste_mots = [] # Nous sert à choisir rapidemnt un mot aléatoire
        self.recharger() # Initialise les deux attributs en utilisant le fichier

    def recharger(self):
        """Recharge le fichier de mots"""
        path = Path(self.localisation_fichier)
        mots = set()  # On crée un ensemble vide pour stocker les mots uniques

        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    mot = _normaliser_mot(line)
                    if mot:
                        mots.add(mot) # Ajoute le mot au set 
        except FileNotFoundError:
            mots = set()

        self.dict_mots = mots
        self._liste_mots = sorted(mots) 

    def mot_valide(self, mot):
        """Retourne True si le mot est bien dans le dictionnaire. False sinon"""
        mot_normalise = _normaliser_mot(mot)
        if not mot_normalise:
            return False
        return mot_normalise in self.dict_mots

    def randomMot_secret(self):
        """Retourne un mot aléatoire du dictionnaire ou une chaîne vide dans le cas où le disctionnaire est vide."""
        if not self._liste_mots:
            return ""
        return random.choice(self._liste_mots)




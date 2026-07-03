import random
from modele.dictionnaire import Dictionnaire
from modele.joueur import Joueur
from modele.calculateur_score import calculateur_score

POINTS_LETTRES = {
    'A': 1, 'E': 1, 'I': 1, 'L': 1, 'N': 1, 'O': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1,
    'D': 2, 'G': 2, 'M': 2,
    'B': 3, 'C': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4,
    'J': 8, 'Q': 8,
    'K': 10, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10,
    '?': 0,
}

BONUS_MOT_IMPOSE = 15 
BONUS_SCRABBLE   = 50  # si 7 lettres posées d'un coup

# cases spéciales du plateau
def _construire_cases():
    cases = [['' for _ in range(15)] for _ in range(15)]
    MT = [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)]
    MD = [(1,1),(2,2),(3,3),(4,4),(1,13),(2,12),(3,11),(4,10),
          (10,4),(11,3),(12,2),(13,1),(10,10),(11,11),(12,12),(13,13),(7,7)]
    LT = [(1,5),(1,9),(5,1),(5,5),(5,9),(5,13),
          (9,1),(9,5),(9,9),(9,13),(13,5),(13,9)]
    LD = [(0,3),(0,11),(2,6),(2,8),(3,0),(3,7),(3,14),
          (6,2),(6,6),(6,8),(6,12),(7,3),(7,11),
          (8,2),(8,6),(8,8),(8,12),(11,0),(11,7),(11,14),
          (12,6),(12,8),(14,3),(14,11)]
    for r, c in MT: cases[r][c] = 'MT'
    for r, c in MD: cases[r][c] = 'MD'
    for r, c in LT: cases[r][c] = 'LT'
    for r, c in LD: cases[r][c] = 'LD'
    return cases

CASES_SPECIALES = _construire_cases()


class Partie:
    def __init__(self, location_dict):
        self.dictionnaire = Dictionnaire(location_dict)
        self.calculateur  = calculateur_score(POINTS_LETTRES, CASES_SPECIALES)
        self.sacLettres   = self._initialiserSacLettres()
        self.plateau      = [[' ' for _ in range(15)] for _ in range(15)]
        self.tour         = 0
        self.joueur1      = self._initialiserJoueur()
        self.joueur2      = self._initialiserJoueur()
        self.terminee     = False
        self.passes_consecutifs = 0

    def _initialiserSacLettres(self):
        nbLettres = {
            'E': 15, 'A': 9, 'I': 8,
            'N': 6, 'O': 6, 'R': 6, 'S': 6, 'T': 6, 'U': 6,
            'L': 5, 'D': 3, 'M': 3,
            'G': 2, 'B': 2, 'C': 2, 'P': 2, 'F': 2, 'H': 2, 'V': 2, '?': 2,
            'J': 1, 'Q': 1, 'K': 1, 'W': 1, 'X': 1, 'Y': 1, 'Z': 1
        }
        sac = []
        for lettre, quantite in nbLettres.items():
            sac.extend([lettre] * quantite)
        random.shuffle(sac)
        return sac

    def _initialiserJoueur(self):
        chevalet = []
        for _ in range(7):
            if self.sacLettres:
                chevalet.append(self.sacLettres.pop())
        mot_secret = self.dictionnaire.randomMot_secret()
        return Joueur(chevalet, 0, mot_secret)

    def _extraire_mot_plateau(self, plateau, r, c, dr, dc):
        """Remonte au début du mot dans la direction (dr,dc) puis retourne le mot complet."""
        while r - dr >= 0 and c - dc >= 0 and plateau[r - dr][c - dc] != ' ':
            r -= dr
            c -= dc
        mot = ''
        while 0 <= r < 15 and 0 <= c < 15 and plateau[r][c] != ' ':
            mot += plateau[r][c]
            r += dr
            c += dc
        return mot

    def poserMot(self, mot, ligne, colonne, direction, num_joueur):
        direction = direction.upper()
        joueur = self.joueur1 if num_joueur == 1 else self.joueur2

        if not self.dictionnaire.mot_valide(mot.upper()):
            return False
        if direction == 'H' and colonne + len(mot) > 15:
            return False
        if direction == 'V' and ligne + len(mot) > 15:
            return False

        # Positions des lettres du mot principal
        positions = []
        for i in range(len(mot)):
            r = ligne + (i if direction == 'V' else 0)
            c = colonne + (i if direction == 'H' else 0)
            positions.append((r, c))

        # Vérification case par case : cohérence avec le plateau
        lettres_a_placer = []
        positions_nouvelles = []
        for i, lettre in enumerate(mot):
            r, c = positions[i]
            case = self.plateau[r][c]
            if case == ' ':
                lettres_a_placer.append(lettre)
                positions_nouvelles.append((r, c))
            elif case != lettre:
                return False

        if not lettres_a_placer:
            return False

        # Vérification du chevalet
        chevalet_temp = joueur.chevalet[:]
        for lettre in lettres_a_placer:
            if lettre in chevalet_temp:
                chevalet_temp.remove(lettre)
            elif '?' in chevalet_temp:
                chevalet_temp.remove('?')
            else:
                return False

        # Connexion au plateau
        plateau_vide = all(self.plateau[r][c] == ' ' for r in range(15) for c in range(15))
        if plateau_vide:
            passe_centre = any(r == 7 and c == 7 for r, c in positions)
            if not passe_centre:
                return False
        else:
            connecte = False
            for r, c in positions:
                if self.plateau[r][c] != ' ':
                    connecte = True
                    break
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 15 and 0 <= nc < 15 and self.plateau[nr][nc] != ' ':
                        connecte = True
                        break
                if connecte:
                    break
            if not connecte:
                return False

        # Simulation du plateau après pose pour valider les mots croisés
        plateau_simule = [row[:] for row in self.plateau]
        for i, lettre in enumerate(mot):
            r, c = positions[i]
            plateau_simule[r][c] = lettre

        # Vérification des mots croisés formés par les nouvelles lettres
        dr_perp, dc_perp = (0, 1) if direction == 'V' else (1, 0)
        for r, c in positions_nouvelles:
            mot_croise = self._extraire_mot_plateau(plateau_simule, r, c, dr_perp, dc_perp)
            if len(mot_croise) > 1 and not self.dictionnaire.mot_valide(mot_croise.upper()):
                return False

        plateau_avant = [row[:] for row in self.plateau]

        # Pose effective des lettres
        for i, lettre in enumerate(mot):
            r, c = positions[i]
            self.plateau[r][c] = lettre
        joueur.chevalet = chevalet_temp

        # score classique
        points = self.calculateur.calculerScore(self.plateau, plateau_avant)

        # bonus si 7 lettres posées d'un coup
        if len(lettres_a_placer) == 7:
            points += BONUS_SCRABBLE

        # bonus mot imposé
        if mot.upper() == joueur.mot_secret:
            points += BONUS_MOT_IMPOSE
            joueur.mot_secret = self.dictionnaire.randomMot_secret()

        joueur.score += points
        self.passes_consecutifs = 0

        # Repiocher
        while len(joueur.chevalet) < 7 and self.sacLettres:
            joueur.chevalet.append(self.sacLettres.pop())

        self.tour += 1
        joueur.dernier_coup = "poser_mot"
        self._verifier_fin_partie()
        return True

    def defausserLettres(self, lettres_a_defausser, num_joueur):
        joueur = self.joueur1 if num_joueur == 1 else self.joueur2
        chevalet_temp = joueur.chevalet[:]
        for lettre in lettres_a_defausser:
            if lettre in chevalet_temp:
                chevalet_temp.remove(lettre)
            else:
                return False
        if len(self.sacLettres) < len(lettres_a_defausser):
            return False
        self.sacLettres.extend(lettres_a_defausser)
        random.shuffle(self.sacLettres)
        joueur.chevalet = chevalet_temp
        for _ in range(len(lettres_a_defausser)):
            joueur.chevalet.append(self.sacLettres.pop())
        joueur.dernier_coup = "defausser"
        self.passes_consecutifs = 0

        self.tour += 1
        return True

    def passertour(self, num_joueur):
        print("Le joueur passe son tour")
        self.tour += 1
        joueur = self.joueur1 if num_joueur == 1 else self.joueur2
        joueur.dernier_coup = "passer"
        self.passes_consecutifs += 1
        if self.passes_consecutifs >= 4:
            self._finaliser()
        return True

    def changermotsecret(self, num_joueur):
        """Change le mot imposé — coûte le tour du joueur (perte de tour)."""
        joueur = self.joueur1 if num_joueur == 1 else self.joueur2
        nouveau_mot = self.dictionnaire.randomMot_secret()
        while nouveau_mot == joueur.mot_secret:
            nouveau_mot = self.dictionnaire.randomMot_secret()
        joueur.mot_secret = nouveau_mot
        joueur.dernier_coup = "changer_mot"
        self.passes_consecutifs = 0
        self.tour += 1
        return True

    def _verifier_fin_partie(self):
        """Déclenche la fin si le sac est vide et qu'un joueur n'a plus de lettres."""
        if self.sacLettres:
            return
        if not self.joueur1.chevalet or not self.joueur2.chevalet:
            self._finaliser()

    def _finaliser(self):
        """Décompte final : pénalités lettres restantes, bonus vider chevalet."""
        self.terminee = True

        for joueur, adversaire in [(self.joueur1, self.joueur2), (self.joueur2, self.joueur1)]:
            if not joueur.chevalet:
                # A vidé son chevalet : récupère les points des lettres adverses
                bonus = sum(POINTS_LETTRES.get(l, 0) for l in adversaire.chevalet)
                joueur.score += bonus
            else:
                # Perd les points de ses lettres restantes
                malus = sum(POINTS_LETTRES.get(l, 0) for l in joueur.chevalet)
                joueur.score = max(0, joueur.score - malus)

    def vainqueur(self):
        """Retourne 1, 2, ou 0 (égalité). À appeler seulement si terminee == True."""
        if self.joueur1.score > self.joueur2.score:
            return 1
        elif self.joueur2.score > self.joueur1.score:
            return 2
        return 0

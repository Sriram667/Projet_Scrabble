import pygame
from pathlib import Path
from modele.partie import Partie
from vue.game_view import Game_view, VueSaisieIP
from vue.bouton import Bouton
from vue.element import Element
from controleur.game_controller import GameController


LARGEUR, HAUTEUR = 1280, 720
CHEMIN_DICT = Path(__file__).parent.parent / "Dictionnaire_ODS.txt"

TAILLE_CASE = 38
PLATEAU_X   = 28
PLATEAU_Y   = 22
PX = PLATEAU_X + 15 * TAILLE_CASE + 20   # = 618

COULEURS_CASES = {
    'MT': (220,  50,  50),
    'MD': (230, 130, 130),
    'LT': ( 70, 130, 200),
    'LD': (140, 190, 230),
    ''  : (240, 230, 210),
}
C_LETTRE_VALIDEE = (255, 248, 180)
C_LETTRE_JOKER   = (200, 180, 255)   
C_LETTRE_PREVIEW = (180, 230, 180)
C_BORD           = (180, 160, 130)
C_BORD_PLATEAU   = (100,  80,  60)


C_TUILE_NORMALE   = (205, 133,  63)
C_TUILE_SELECTEE  = ( 50, 200,  50)
C_TUILE_GRISEE    = ( 90,  90,  90)
C_TUILE_DEFAUSSE  = (220, 100,  30)

LABELS_CASES = {'MT': 'TM', 'MD': 'DM', 'LT': 'TL', 'LD': 'DL'}


def _construire_cases_speciales():
    cases = [['' for _ in range(15)] for _ in range(15)]
    for r, c in [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)]:
        cases[r][c] = 'MT'
    for r, c in [(1,1),(2,2),(3,3),(4,4),(1,13),(2,12),(3,11),(4,10),
                 (10,4),(11,3),(12,2),(13,1),(10,10),(11,11),(12,12),(13,13),(7,7)]:
        cases[r][c] = 'MD'
    for r, c in [(1,5),(1,9),(5,1),(5,5),(5,9),(5,13),
                 (9,1),(9,5),(9,9),(9,13),(13,5),(13,9)]:
        cases[r][c] = 'LT'
    for r, c in [(0,3),(0,11),(2,6),(2,8),(3,0),(3,7),(3,14),
                 (6,2),(6,6),(6,8),(6,12),(7,3),(7,11),
                 (8,2),(8,6),(8,8),(8,12),(11,0),(11,7),(11,14),
                 (12,6),(12,8),(14,3),(14,11)]:
        cases[r][c] = 'LD'
    return cases

CASES_SPECIALES = _construire_cases_speciales()


#  Création des boutons plateau 

def creer_boutons_plateau():
    boutons = []
    for r in range(15):
        for c in range(15):
            x = PLATEAU_X + c * TAILLE_CASE
            y = PLATEAU_Y + r * TAILLE_CASE
            type_case = CASES_SPECIALES[r][c]
            btn = Bouton(x, y, TAILLE_CASE, TAILLE_CASE,
                         texte=LABELS_CASES.get(type_case, ""),
                         couleur=None,
                         id="case_plateau",
                         row=r, col=c, type_case=type_case)
            btn.set_couleur(COULEURS_CASES[type_case])
            boutons.append(btn)
    return boutons


#  Création des pages

def creer_page_depart(partie):
    boutons = [
        Bouton(490, 200, 300, 70, "JOUER",   None, "jouer"),
        Bouton(490, 300, 300, 70, "SERVEUR", None, "serveur"),
        Bouton(490, 400, 300, 70, "OPTIONS", None, "options"),
        Bouton(490, 500, 300, 70, "QUITTER", None, "quitter"),
    ]
    elements = [
        Element(640, 80, "SCRABBLE", 100, (255, 200, 0), centre=True, outline_color=(120, 70, 0), outline_width=3, shadow=True, shadow_offset=5),
    ]
    return Game_view(partie, boutons, elements)


def creer_page_mode(partie):
    boutons = [
        Bouton(400, 280, 480, 60, "Joueur 1 vs Joueur 2", None, "mode_jvj"),
        Bouton(400, 370, 480, 60, "Joueur vs IA",         None, "mode_jvia"),
        Bouton(490, 480, 300, 55, "RETOUR",               None, "retour"),
    ]
    elements = [
        Element(640, 120, "CHOISIR LE MODE", 60, (255, 200, 0), centre=True),
    ]
    return Game_view(partie, boutons, elements)


def creer_page_option(partie):
    boutons = [
        Bouton(490, 230, 300, 60, "RÈGLES DU JEU", None, "regles"),
        Bouton(490, 320, 300, 60, "MENU",           None, "menu"),
        Bouton(490, 410, 300, 60, "RETOUR",         None, "retour"),
        Bouton(490, 500, 300, 60, "QUITTER",        None, "quitter"),
        Bouton(530, 610, 55,  50, "-",              None, "volume_moins"),
        Bouton(695, 610, 55,  50, "+",              None, "volume_plus"),
    ]
    elements = [
        Element(640,  80, "OPTIONS",  60, (255, 200, 0), centre=True),
        Element(640, 580, "VOLUME :", 24, (220, 220, 220), centre=True),
        Element(640, 618, "50%",      28, (255, 255, 255), centre=True, id="volume_label"),
    ]
    return Game_view(partie, boutons, elements, couleur_fond=(30, 30, 50))


def creer_page_regles(partie):
    boutons = [
        Bouton(490, 600, 300, 60, "RETOUR", None, "retour"),
    ]
    elements = [
    ]
    return Game_view(partie, boutons, elements, (30, 30, 50), "assets/image/regles.png")


def creer_page_jeu(partie):
    _W  = LARGEUR - PX - 20
    _W2 = (_W - 8) // 2
    boutons = [
        Bouton(PX + 10,           380, _W2, 55, "VALIDER",            None, "valider"),
        Bouton(PX + 10 + _W2 + 8, 380, _W2, 55, "ANNULER",            None, "annuler"),
        Bouton(PX + 10,           445, _W,  50, "DÉFAUSSER",          None, "defausser"),
        Bouton(PX + 10,           505, _W,  45, "CHANGER MOT IMPOSÉ", None, "changer_mot"),
        Bouton(PX + 10,           560, _W2, 50, "PASSER",             None, "passer"),
        Bouton(PX + 10 + _W2 + 8, 560, _W2, 50, "OPTIONS",            None, "options_jeu"),
    ]
    elements = [
        Element(PX + 10,  55, "Score J1 : 0 pts",   26, (255, 255, 255), id="score_j1"),
        Element(PX + 10,  85, "Score J2 : 0 pts",   26, (255, 255, 255), id="score_j2"),
        Element(PX + 10, 135, "Mot impose :",        26, (255, 255,   0)),
        Element(PX + 10, 165, "",                    36, (255, 230,  50), id="mot_impose"),
        Element(PX + 10, 220, "Lettres restantes :", 26, (240, 205, 110)),
        Element(PX + 10, 243, "100",                 36, (255, 255, 255), id="sac"),
        Element(PX + 10,  25, "",                    26, (100, 220, 100), id="tour_info"),
        Element(PX + 10, 288, "",                    26, (255, 100, 100), id="message"),
    ]
    return Game_view(partie, boutons, elements)


def creer_page_reseau(partie):
    boutons = [
        Bouton(515, 250, 250, 65, "HÉBERGER",  None, "heberger"),
        Bouton(490, 460, 300, 55, "CONNECTER", None, "connecter"),
        Bouton(490, 530, 300, 55, "RETOUR",    None, "retour"),
    ]
    elements = [
        Element(640,  80, "RÉSEAU LOCAL",      60, (255, 200, 0), centre=True),
        Element(470, 170, "Votre IP locale :", 20, (180, 180, 180), id="ip_locale"),
        Element(340, 345, "IP du serveur :",   22, (200, 200, 200)),
        Element(340, 610, "",                  18, (255, 100, 100), id="msg_reseau"),
    ]
    return VueSaisieIP(partie, boutons, elements)


def main():
    pygame.init()
    pygame.mixer.init()

    chemin_musique = Path(__file__).parent.parent / "assets" / "music" / "ScrabbleTheme.mp3"
    pygame.mixer.music.load(str(chemin_musique))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    sfx_party_end = pygame.mixer.Sound(
        str(Path(__file__).parent.parent / "assets" / "sfx" / "party_end.mp3")
    )
    sfx_error = pygame.mixer.Sound(
        str(Path(__file__).parent.parent / "assets" / "sfx" / "error.mp3")
    )

    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Scrabble")
    clock = pygame.time.Clock()

    partie = Partie(CHEMIN_DICT)

    vues = {
        'menu':    creer_page_depart(partie),
        'mode':    creer_page_mode(partie),
        'options': creer_page_option(partie),
        'regles':  creer_page_regles(partie),
        'jeu':     creer_page_jeu(partie),
        'reseau':  creer_page_reseau(partie),
    }
    boutons_plateau = creer_boutons_plateau()

    config = {
        'LARGEUR':          LARGEUR,
        'PLATEAU_X':        PLATEAU_X,
        'PLATEAU_Y':        PLATEAU_Y,
        'TAILLE_CASE':      TAILLE_CASE,
        'PX':               PX,
        'COULEURS_CASES':   COULEURS_CASES,
        'LABELS_CASES':     LABELS_CASES,
        'C_LETTRE_VALIDEE': C_LETTRE_VALIDEE,
        'C_LETTRE_JOKER':   C_LETTRE_JOKER,
        'C_LETTRE_PREVIEW': C_LETTRE_PREVIEW,
        'C_BORD':           C_BORD,
        'C_BORD_PLATEAU':   C_BORD_PLATEAU,
        'C_TUILE_NORMALE':  C_TUILE_NORMALE,
        'C_TUILE_SELECTEE': C_TUILE_SELECTEE,
        'C_TUILE_GRISEE':   C_TUILE_GRISEE,
        'C_TUILE_DEFAUSSE': C_TUILE_DEFAUSSE,
        'sfx_party_end':    sfx_party_end,
        'sfx_error':        sfx_error,
        'sfx_valid':        pygame.mixer.Sound(
            str(Path(__file__).parent.parent / "assets" / "sfx" / "valid.mp3")
        ),
    }

    controleur = GameController(ecran, clock, partie, vues, boutons_plateau, config)
    controleur.lancer()


if __name__ == "__main__":
    main()

import pygame
from vue.element import Element


class Game_view:
    """Vue générique : fond + boutons + éléments texte."""

    def __init__(self, partie, tab_boutons=None, tab_elements=None, couleur_fond=None, image_fond=None):
        self.partie       = partie
        self.afficher     = False
        self.fond         = couleur_fond
        self.tab_boutons  = tab_boutons  or []
        self.tab_elements = tab_elements or []
        self.image_fond = pygame.image.load(image_fond) if image_fond else ""

    def basculer_affichage(self):
        self.afficher = not self.afficher

    def afficher_page(self, ecran):
        if self.afficher:
            if self.image_fond != "":
                ecran.blit(self.image_fond, (0, 0))
            else:
                ecran.fill(self.fond or (28, 52, 28))
            pos_souris = pygame.mouse.get_pos()
            for bouton in self.tab_boutons:
                if bouton.est_selectionne(pos_souris):
                    bouton.afficher_bouton_hover(ecran)
                else:
                    bouton.afficher_bouton(ecran)
            for element in self.tab_elements:
                element.afficher_element(ecran)

    def get_element(self, id):
        for e in self.tab_elements:
            if e.id == id:
                return e
        raise KeyError(f"Element id='{id}' introuvable")


class VueSaisieIP(Game_view):
    """
    Page réseau avec champ de saisie IP pygame.
    Affiche un curseur clignotant et gère les touches clavier.
    """

    def __init__(self, partie, tab_boutons=None, tab_elements=None):
        super().__init__(partie, tab_boutons, tab_elements, couleur_fond=(20, 20, 40))
        self.ip_saisie   = ""
        self.saisie_active = False
        self.timer_curseur = 0
        self.curseur_visible = True
        self._police_ip = None

    def _init_police(self):
        if self._police_ip is None:
            self._police_ip = pygame.font.SysFont("georgia", 32)

    def afficher_page(self, ecran):
        if not self.afficher:
            return
        self._init_police()
        ecran.fill(self.fond)

        # Champ de saisie
        rect_champ = pygame.Rect(340, 375, 600, 50)
        couleur_bord = (100, 200, 100) if self.saisie_active else (150, 150, 150)
        pygame.draw.rect(ecran, (40, 40, 60), rect_champ, border_radius=6)
        pygame.draw.rect(ecran, couleur_bord, rect_champ, 2, border_radius=6)

        # Texte saisi + curseur clignotant
        self.timer_curseur += 1
        if self.timer_curseur > 30:
            self.curseur_visible = not self.curseur_visible
            self.timer_curseur = 0

        texte_affiche = self.ip_saisie
        if self.saisie_active and self.curseur_visible:
            texte_affiche += "|"

        surf = self._police_ip.render(texte_affiche, True, (255, 255, 255))
        ecran.blit(surf, (rect_champ.x + 10, rect_champ.y + 8))

        pos_souris = pygame.mouse.get_pos()
        for bouton in self.tab_boutons:
            if bouton.est_selectionne(pos_souris):
                bouton.afficher_bouton_hover(ecran)
            else:
                bouton.afficher_bouton(ecran)
        for element in self.tab_elements:
            element.afficher_element(ecran)

    def gerer_touche(self, event):
        """Appelé par le contrôleur sur pygame.KEYDOWN."""
        if not self.saisie_active:
            return
        if event.key == pygame.K_BACKSPACE:
            self.ip_saisie = self.ip_saisie[:-1]
        elif event.key == pygame.K_RETURN:
            pass   # le contrôleur gère la validation
        elif len(self.ip_saisie) < 15:
            if event.unicode in "0123456789.":
                self.ip_saisie += event.unicode

    def activer_saisie(self, pos):
        rect_champ = pygame.Rect(340, 375, 600, 50)
        self.saisie_active = rect_champ.collidepoint(pos)
import pygame
from vue.bouton import Bouton


class PopupController:


    def __init__(self, ecran, partie, largeur, sfx_party_end,
                 on_retour_menu, on_quitter):
        self.ecran         = ecran
        self.partie        = partie
        self.largeur       = largeur
        self.sfx_party_end = sfx_party_end

        # Callbacks vers GameController
        self._on_retour_menu = on_retour_menu  # historique.clear + reinit + vue menu
        self._on_quitter     = on_quitter       # pygame.quit + exit

    
        self.popup_actif         = False
        self._action_cible       = None
        self._police             = pygame.font.SysFont("segoeuibald", 28)
        self._btn_oui = Bouton(510, 370, 110, 50, "OUI", None, "popup_oui")
        self._btn_non = Bouton(660, 370, 110, 50, "NON", None, "popup_non")
        self._btn_oui.set_couleur((80, 160, 80))
        self._btn_non.set_couleur((180, 60, 60))

    
        self.popup_victoire     = False
        self._victoire_msg      = ""
        self._police_titre      = pygame.font.SysFont("segoeuibald", 48)
        self._police_msg        = pygame.font.SysFont("segoeuibald", 30)
        self._police_score      = pygame.font.SysFont("segoeuibald", 24)
        self._btn_menu_victoire = Bouton(540, 430, 200, 55, "MENU", None, "popup_victoire_menu")
        self._btn_menu_victoire.set_couleur((80, 130, 200))

    

    def declencher_fin_partie(self):
        v = self.partie.vainqueur()
        self._victoire_msg = "Égalité !" if v == 0 else f"Victoire Joueur {v} !"
        self.popup_victoire = True
        pygame.mixer.music.stop()
        self.sfx_party_end.play()

    

    def gerer_clic(self, pos) -> bool:
        """
        Traite un clic si un popup est actif.
        Retourne True si le clic a été consommé (le reste du clic doit être ignoré).
        """
        if self.popup_victoire:
            if self._btn_menu_victoire.est_selectionne(pos):
                self.popup_victoire = False
                self._on_retour_menu()
            return True

        if self.popup_actif:
            if self._btn_oui.est_selectionne(pos):
                self._confirmer()
            elif self._btn_non.est_selectionne(pos):
                self.popup_actif = False
                self._action_cible = None
            return True

        return False


    def executer_action(self, action_id) -> bool:
        """
        Traite les actions liées aux popups.
        Retourne True si l'action a été prise en charge.
        """
        if action_id == "menu":
            self.popup_actif   = True
            self._action_cible = "menu"
            return True

        if action_id == "quitter":
            self.popup_actif   = True
            self._action_cible = "quitter"
            return True

        if action_id == "popup_oui":
            self.popup_actif = False
            self._confirmer()
            return True

        if action_id == "popup_non":
            self.popup_actif   = False
            self._action_cible = None
            return True

        return False

    
    def dessiner(self):
        if self.popup_actif:
            self._dessiner_confirmation()
        if self.popup_victoire:
            self._dessiner_victoire()

    def _dessiner_confirmation(self):
        overlay = pygame.Surface((self.largeur, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.ecran.blit(overlay, (0, 0))

        boite = pygame.Rect(390, 280, 500, 180)
        pygame.draw.rect(self.ecran, (40, 40, 60), boite, border_radius=10)
        pygame.draw.rect(self.ecran, (180, 160, 130), boite, 2, border_radius=10)

        surf = self._police.render("Êtes-vous sûr de vouloir quitter ?", True, (255, 255, 255))
        self.ecran.blit(surf, surf.get_rect(centerx=640, top=305))

        self._btn_oui.afficher_bouton(self.ecran)
        self._btn_non.afficher_bouton(self.ecran)

    def _dessiner_victoire(self):
        overlay = pygame.Surface((self.largeur, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.ecran.blit(overlay, (0, 0))

        boite = pygame.Rect(290, 200, 700, 290)
        pygame.draw.rect(self.ecran, (30, 30, 60), boite, border_radius=12)
        pygame.draw.rect(self.ecran, (255, 200, 0), boite, 3, border_radius=12)

        titre = self._police_titre.render("PARTIE TERMINÉE", True, (255, 200, 0))
        self.ecran.blit(titre, titre.get_rect(centerx=640, top=220))

        msg = self._police_msg.render(self._victoire_msg, True, (255, 255, 255))
        self.ecran.blit(msg, msg.get_rect(centerx=640, top=290))

        s1 = self._police_score.render(
            f"Joueur 1 : {self.partie.joueur1.score} pts", True, (200, 230, 255))
        s2 = self._police_score.render(
            f"Joueur 2 : {self.partie.joueur2.score} pts", True, (200, 230, 255))
        self.ecran.blit(s1, s1.get_rect(centerx=640, top=345))
        self.ecran.blit(s2, s2.get_rect(centerx=640, top=378))

        self._btn_menu_victoire.afficher_bouton(self.ecran)

    
    def _confirmer(self):
        self.popup_actif   = False
        cible              = self._action_cible
        self._action_cible = None
        if cible == "menu":
            self._on_retour_menu()
        elif cible == "quitter":
            self._on_quitter()

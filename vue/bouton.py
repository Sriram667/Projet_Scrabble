import pygame


class Bouton:
    """Instance de bouton à afficher et détecter au clic."""

    def __init__(self, x, y, largeur, hauteur, texte=None, couleur=None, id=None,
                 row=None, col=None, type_case=None):
        self.rectangle = pygame.Rect(x, y, largeur, hauteur)
        self.id        = id
        self.texte     = texte if texte else ""
        self.couleur   = self._choix_couleur(couleur)
        self.police    = pygame.font.SysFont("georgia", round(hauteur * 0.55))

        # Attributs spécifiques aux cases du plateau
        self.row       = row        # ligne sur le plateau (0-14), None si pas une case
        self.col       = col        # colonne sur le plateau (0-14), None si pas une case
        self.type_case = type_case  # '', 'MT', 'MD', 'LT', 'LD'

    def _choix_couleur(self, couleur):
        if couleur == "blanc":
            return (255, 255, 255)
        elif couleur == "noir":
            return (0, 0, 0)
        elif couleur == "gris_fonce":
            return (128, 128, 128)
        else:
            return (205, 133, 63)

    def set_couleur(self, couleur_rgb):
        self.couleur = couleur_rgb

    def afficher_bouton(self, ecran):
        pygame.draw.rect(ecran, self.couleur, self.rectangle, border_radius=4)
        if self.texte:
            surf = self.police.render(self.texte, True, (0, 0, 0))
            ecran.blit(surf, surf.get_rect(center=self.rectangle.center))

    def afficher_bouton_hover(self, ecran):
        r, g, b = self.couleur
        couleur_hover = (max(0, r - 30), max(0, g - 30), max(0, b - 30))
        pygame.draw.rect(ecran, couleur_hover, self.rectangle, border_radius=4)
        if self.texte:
            surf = self.police.render(self.texte, True, (0, 0, 0))
            ecran.blit(surf, surf.get_rect(center=self.rectangle.center))

    def est_selectionne(self, pos):
        return self.rectangle.collidepoint(pos)

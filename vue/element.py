import pygame


class Element:
    """Instance de textes à afficher"""
    def __init__(self, x, y, texte, taille_police=None, couleur=None, id=None, centre=False, outline_color=None, outline_width=0, shadow=False, shadow_offset=4):
        self.posx = x
        self.posy = y
        self.texte = texte
        self.police = pygame.font.SysFont("segoeuibald", taille_police or 50)
        self.couleur = couleur or (0, 0, 0)
        self.id = id
        self.centre = centre
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.shadow = shadow
        self.shadow_offset = shadow_offset

    def afficher_element(self, ecran):
        if self.shadow:
            shadow_surf = self.police.render(self.texte, True, (0, 0, 0))
            o = self.shadow_offset
            if self.centre:
                rect = shadow_surf.get_rect(centerx=self.posx + o, top=self.posy + o)
            else:
                rect = (self.posx + o, self.posy + o)
            ecran.blit(shadow_surf, rect)

        if self.outline_color and self.outline_width > 0:
            outline_surf = self.police.render(self.texte, True, self.outline_color)
            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    if self.centre:
                        rect = outline_surf.get_rect(centerx=self.posx + dx, top=self.posy + dy)
                    else:
                        rect = (self.posx + dx, self.posy + dy)
                    ecran.blit(outline_surf, rect)

        texte_surface = self.police.render(self.texte, True, self.couleur)
        if self.centre:
            ecran.blit(texte_surface, texte_surface.get_rect(centerx=self.posx, top=self.posy))
        else:
            ecran.blit(texte_surface, (self.posx, self.posy))

    def modifier_texte(self, nouveau_texte):
        self.texte = nouveau_texte

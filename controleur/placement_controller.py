class PlacementController:
    """
    Gère l'état et la logique de la pose de lettres en cours
    (sélection, placement preview, joker, défausse, validation).
    """

    def __init__(self, partie, reseau,
                 get_joueur_courant, get_num_joueur,
                 on_message, on_apres_coup, sfx_valid):
        self.partie  = partie
        self.reseau  = reseau

        self._get_joueur_courant = get_joueur_courant  # () -> Joueur
        self._get_num_joueur     = get_num_joueur       # () -> int
        self._on_message         = on_message           # (texte, erreur=True)
        self._on_apres_coup      = on_apres_coup        # () -> passer au joueur suivant
        self._sfx_valid          = sfx_valid

        # État de la pose en cours
        self.placements         = []
        self.index_selectionne  = None
        self.mode_defausse      = False
        self.defausse_selection = []
        self.joker_en_attente   = None  # (r, c, idx_chevalet)

    
    def clic_tuile(self, index):
        if self.mode_defausse:
            if index in self.defausse_selection:
                self.defausse_selection.remove(index)
            else:
                self.defausse_selection.append(index)
            return

        indices_places = [idx for lettre, r, c, idx in self.placements]
        if index in indices_places:
            return
        if self.index_selectionne == index:
            self.index_selectionne = None
        else:
            self.index_selectionne = index

    

    def clic_case(self, r, c):
        for i in range(len(self.placements)):
            lettre, pr, pc, idx = self.placements[i]
            if pr == r and pc == c:
                self.placements.pop(i)
                self.index_selectionne = idx
                return

        if self.partie.plateau[r][c] != ' ':
            return
        if self.index_selectionne is None:
            return

        joueur = self._get_joueur_courant()
        lettre = joueur.chevalet[self.index_selectionne]

        if lettre == '?':
            self.joker_en_attente = (r, c, self.index_selectionne)
            self.index_selectionne = None
            self._on_message("Joker : appuyez sur une lettre (A-Z)", erreur=False)
            return

        self.placements.append((lettre, r, c, self.index_selectionne))
        self.index_selectionne = None

    def choisir_lettre_joker(self, event):
        if event.unicode and event.unicode.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            lettre_choisie = event.unicode.lower()  # minuscule = joker sur le plateau
            r, c, idx = self.joker_en_attente
            self.placements.append((lettre_choisie, r, c, idx))
            self.joker_en_attente = None
            self._on_message("")

    

    def annuler(self):
        self.placements.clear()
        self.index_selectionne  = None
        self.mode_defausse      = False
        self.defausse_selection = []
        self.joker_en_attente   = None

    

    def valider_mot(self):
        if not self.placements:
            self._on_message("Placez des lettres avant de valider")
            return

        rows = [r for lettre, r, c, idx in self.placements]
        cols = [c for lettre, r, c, idx in self.placements]

        horizontal = len(set(rows)) == 1
        vertical   = len(set(cols)) == 1

        if horizontal and vertical:
            r0, c0  = rows[0], cols[0]
            plateau = self.partie.plateau
            voisin_v = (
                (r0 > 0  and plateau[r0 - 1][c0] != ' ') or
                (r0 < 14 and plateau[r0 + 1][c0] != ' ')
            )
            voisin_h = (
                (c0 > 0  and plateau[r0][c0 - 1] != ' ') or
                (c0 < 14 and plateau[r0][c0 + 1] != ' ')
            )
            horizontal = not (voisin_v and not voisin_h)

        if not horizontal and not vertical:
            self._on_message("Les lettres doivent être alignées")
            return

        plateau = self.partie.plateau

        if horizontal:
            r0    = rows[0]
            c_min = min(cols)
            c_max = max(cols)
            while c_min > 0  and plateau[r0][c_min - 1] != ' ':
                c_min -= 1
            while c_max < 14 and plateau[r0][c_max + 1] != ' ':
                c_max += 1
            preview = {c: lettre for lettre, r, c, idx in self.placements}
            mot = ""
            for c in range(c_min, c_max + 1):
                if plateau[r0][c] != ' ':
                    mot += plateau[r0][c]
                elif c in preview:
                    mot += preview[c]
                else:
                    self._on_message("Il y a un trou dans le mot")
                    return
            if self.reseau.mode_reseau:
                self.reseau.envoyer_poser_mot(mot, r0, c_min, 'H')
                self.annuler()
                return
            ok = self.partie.poserMot(mot, r0, c_min, 'H', self._get_num_joueur())

        else:
            c0    = cols[0]
            r_min = min(rows)
            r_max = max(rows)
            while r_min > 0  and plateau[r_min - 1][c0] != ' ':
                r_min -= 1
            while r_max < 14 and plateau[r_max + 1][c0] != ' ':
                r_max += 1
            preview = {r: lettre for lettre, r, c, idx in self.placements}
            mot = ""
            for r in range(r_min, r_max + 1):
                if plateau[r][c0] != ' ':
                    mot += plateau[r][c0]
                elif r in preview:
                    mot += preview[r]
                else:
                    self._on_message("Il y a un trou dans le mot")
                    return
            if self.reseau.mode_reseau:
                self.reseau.envoyer_poser_mot(mot, r_min, c0, 'V')
                self.annuler()
                return
            ok = self.partie.poserMot(mot, r_min, c0, 'V', self._get_num_joueur())

        if not ok:
            self._on_message(f"'{mot}' refuse : hors dico ou mal connecte")
        else:
            self._sfx_valid.play()
            self.annuler()
            self._on_apres_coup()

    

    def defausser(self):
        if not self.defausse_selection:
            self._on_message("Sélectionnez au moins une lettre à défausser")
            return
        joueur  = self._get_joueur_courant()
        lettres = [joueur.chevalet[i] for i in self.defausse_selection]
        if joueur.dernier_coup == "defausser":
            self._on_message("Vous ne pouvez pas défausser 2 tours d'affilée")
            return
        if self.reseau.mode_reseau:
            self.reseau.envoyer_defausser(lettres)
            self.annuler()
            return
        ok = self.partie.defausserLettres(lettres, self._get_num_joueur())
        if not ok:
            self._on_message("Défausse impossible : sac trop vide")
        else:
            self.annuler()
            self._on_apres_coup()

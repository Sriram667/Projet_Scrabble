import pygame
from vue.game_view import VueSaisieIP
from vue.bouton import Bouton
from controleur.network_controller import NetworkController
from controleur.ia_controller import IAController
from controleur.placement_controller import PlacementController
from controleur.popup_controller import PopupController


class GameController:

    def __init__(self, ecran, clock, partie, vues, boutons_plateau, config):
        self.ecran  = ecran
        self.clock  = clock
        self.partie = partie

        for key, val in config.items():
            setattr(self, key, val)

        self.num_joueur_courant = 1
        self._police_labels = pygame.font.SysFont("georgia", 13)

        self.boutons_plateau  = boutons_plateau
        self.boutons_chevalet = []

        self.vue_menu    = vues['menu']
        self.vue_mode    = vues['mode']
        self.vue_options = vues['options']
        self.vue_regles  = vues['regles']
        self.vue_jeu     = vues['jeu']
        self.vue_reseau  = vues['reseau']

        self.vue_active     = self.vue_menu
        self.vue_active.afficher = True
        self._historique = []

        # ---- Volume ----
        self.volume = 0.5

        # ---- Réseau ----
        self.reseau = NetworkController(
            partie             = self.partie,
            vue_reseau         = self.vue_reseau,
            vue_jeu            = self.vue_jeu,
            on_maj_chevalet    = self._maj_boutons_chevalet,
            on_maj_affichage   = self._maj_affichage_jeu,
            on_changer_vue_jeu = self._activer_vue_jeu_si_besoin,
            on_fin_partie      = lambda: self.popup.declencher_fin_partie(),
            on_set_message     = self._set_message,
            on_joueur_actif    = self._set_joueur_actif,
        )

        self.placement = PlacementController(
            partie             = self.partie,
            reseau             = self.reseau,
            get_joueur_courant = self._joueur_courant,
            get_num_joueur     = lambda: self.num_joueur_courant,
            on_message         = self._set_message,
            on_apres_coup      = self._passer_au_joueur_suivant,
            sfx_valid          = self.sfx_valid,
        )

        # ---- IA ----
        self.ia_ctrl = None

        # ---- Popups ----
        self.popup = PopupController(
            ecran         = self.ecran,
            partie        = self.partie,
            largeur       = self.LARGEUR,
            sfx_party_end = self.sfx_party_end,
            on_retour_menu = self._retour_menu,
            on_quitter     = self._quitter,
        )

        self._maj_boutons_chevalet()

    #  Plateau:

    def _maj_couleurs_plateau(self):
        preview = {}
        for lettre, r, c, idx in self.placement.placements:
            preview[(r, c)] = lettre

        for btn in self.boutons_plateau:
            r, c = btn.row, btn.col
            lettre_plateau = self.partie.plateau[r][c]

            if (r, c) in preview:
                btn.set_couleur(self.C_LETTRE_PREVIEW)
                btn.texte = preview[(r, c)]
                btn.rectangle.inflate_ip(0, 0)
            elif lettre_plateau != ' ':
                if lettre_plateau.islower():
                    btn.set_couleur(self.C_LETTRE_JOKER)
                    btn.texte = lettre_plateau.upper()
                else:
                    btn.set_couleur(self.C_LETTRE_VALIDEE)
                    btn.texte = lettre_plateau
            else:
                btn.set_couleur(self.COULEURS_CASES[btn.type_case])
                btn.texte = self.LABELS_CASES.get(btn.type_case, "")

    #  Chevalet 

    def _maj_boutons_chevalet(self):
        joueur   = self._joueur_courant()
        chevalet = joueur.chevalet
        nb = len(chevalet)

        TAILLE_TUILE = 52
        ESPACEMENT   = 6
        plateau_largeur = 15 * self.TAILLE_CASE
        start_x = self.PLATEAU_X + (plateau_largeur - nb * (TAILLE_TUILE + ESPACEMENT)) // 2
        y = self.PLATEAU_Y + 15 * self.TAILLE_CASE + self.PLATEAU_Y + 8

        self.boutons_chevalet = []
        for i, lettre in enumerate(chevalet):
            x = start_x + i * (TAILLE_TUILE + ESPACEMENT)
            btn = Bouton(x, y, TAILLE_TUILE, TAILLE_TUILE,
                         texte=lettre, couleur=None, id="tuile_chevalet")
            btn.set_couleur(self.C_TUILE_NORMALE)
            btn.index_chevalet = i
            self.boutons_chevalet.append(btn)

    def _maj_couleurs_chevalet(self):
        p = self.placement
        indices_places = [idx for lettre, r, c, idx in p.placements]
        for btn in self.boutons_chevalet:
            i = btn.index_chevalet
            if p.mode_defausse:
                if i in p.defausse_selection:
                    btn.set_couleur(self.C_TUILE_DEFAUSSE)
                else:
                    btn.set_couleur(self.C_TUILE_NORMALE)
            elif i in indices_places:
                btn.set_couleur(self.C_TUILE_GRISEE)
            elif i == p.index_selectionne:
                btn.set_couleur(self.C_TUILE_SELECTEE)
            else:
                btn.set_couleur(self.C_TUILE_NORMALE)


    #  Boucle principale 
    def lancer(self):
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._gerer_clic(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if self.placement.joker_en_attente is not None:
                        self.placement.choisir_lettre_joker(event)
                    elif isinstance(self.vue_active, VueSaisieIP):
                        if event.key == pygame.K_RETURN:
                            self._executer_action("connecter")
                        else:
                            self.vue_active.gerer_touche(event)

            if self.vue_active is self.vue_jeu:
                self._maj_couleurs_plateau()
                self._maj_couleurs_chevalet()

            self.ecran.fill((30, 30, 30))
            self.vue_active.afficher_page(self.ecran)

            if self.vue_active is self.vue_jeu:
                # Lignes de séparation panneau droit
                pygame.draw.line(self.ecran, (100, 80, 60),
                                 (self.PX + 10, 120), (self.LARGEUR - 10, 120), 3)
                pygame.draw.line(self.ecran, (100, 80, 60),
                                 (self.PX + 10, 212), (self.LARGEUR - 10, 212), 3)
                # Cases du plateau
                for btn in self.boutons_plateau:
                    pygame.draw.rect(self.ecran, btn.couleur, btn.rectangle)
                    pygame.draw.rect(self.ecran, self.C_BORD, btn.rectangle, 1)
                    if btn.texte:
                        surf = btn.police.render(btn.texte, True, (0, 0, 0))
                        self.ecran.blit(surf, surf.get_rect(center=btn.rectangle.center))
                # Bordure extérieure plateau
                pygame.draw.rect(self.ecran, self.C_BORD_PLATEAU,
                                 pygame.Rect(self.PLATEAU_X, self.PLATEAU_Y,
                                             15 * self.TAILLE_CASE, 15 * self.TAILLE_CASE), 2)
                # Labels colonnes : 1-15
                for c in range(15):
                    txt = str(c + 1)
                    cx = self.PLATEAU_X + c * self.TAILLE_CASE + self.TAILLE_CASE // 2
                    for cy in [self.PLATEAU_Y // 2,
                                self.PLATEAU_Y + 15 * self.TAILLE_CASE + self.PLATEAU_Y // 2]:
                        s = self._police_labels.render(txt, True, (200, 200, 200))
                        self.ecran.blit(s, s.get_rect(center=(cx, cy)))
                # Labels lignes : A-O
                for r in range(15):
                    txt = chr(ord('A') + r)
                    cy = self.PLATEAU_Y + r * self.TAILLE_CASE + self.TAILLE_CASE // 2
                    for cx in [self.PLATEAU_X // 2,
                                self.PLATEAU_X + 15 * self.TAILLE_CASE + self.PLATEAU_X // 2]:
                        s = self._police_labels.render(txt, True, (200, 200, 200))
                        self.ecran.blit(s, s.get_rect(center=(cx, cy)))
                # Chevalet
                for btn in self.boutons_chevalet:
                    btn.afficher_bouton(ecran=self.ecran)

                # Overlay "pas votre tour" en mode réseau
                if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                    self._dessiner_overlay_attente()

            self.popup.dessiner()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _dessiner_overlay_attente(self):
        """Voile semi-transparent sur le plateau quand ce n'est pas notre tour."""
        surf = pygame.Surface((15 * self.TAILLE_CASE, 15 * self.TAILLE_CASE), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 110))
        self.ecran.blit(surf, (self.PLATEAU_X, self.PLATEAU_Y))

    #  Gestion des clics 

    def _gerer_clic(self, pos):
        if self.popup.gerer_clic(pos):
            return

        if isinstance(self.vue_active, VueSaisieIP):
            self.vue_active.activer_saisie(pos)

        for bouton in self.vue_active.tab_boutons:
            if bouton.est_selectionne(pos):
                self._executer_action(bouton.id)
                return

        if self.vue_active is self.vue_jeu:
            # En mode réseau, bloquer toute interaction si ce n'est pas notre tour
            if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                return
            for btn in self.boutons_chevalet:
                if btn.est_selectionne(pos):
                    self.placement.clic_tuile(btn.index_chevalet)
                    return
            for btn in self.boutons_plateau:
                if btn.est_selectionne(pos):
                    self.placement.clic_case(btn.row, btn.col)
                    return

    #  Actions

    def _executer_action(self, action_id):
        if self.popup.executer_action(action_id):
            return

        if action_id == "jouer":
            self._historique.append(self.vue_active)
            self._changer_vue(self.vue_mode)

        elif action_id == "mode_jvj":
            self._historique.clear()
            self._changer_vue(self.vue_jeu)
            self._maj_affichage_jeu()

        elif action_id == "mode_jvia":
            self._historique.clear()
            self._demarrer_jeu_ia()

        elif action_id == "regles":
            self._historique.append(self.vue_active)
            self._changer_vue(self.vue_regles)

        elif action_id == "options":
            self._historique.append(self.vue_active)
            self._changer_vue(self.vue_options)

        elif action_id == "options_jeu":
            self._historique.append(self.vue_active)
            self._changer_vue(self.vue_options)

        elif action_id == "volume_plus":
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self._maj_label_volume()

        elif action_id == "volume_moins":
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self._maj_label_volume()

        elif action_id == "retour":
            if self._historique:
                self._changer_vue(self._historique.pop())
            else:
                self._changer_vue(self.vue_menu)

        elif action_id == "serveur":
            self.reseau.afficher_ip_locale()
            self._changer_vue(self.vue_reseau)

        elif action_id == "heberger":
            self.reseau.heberger()

        elif action_id == "connecter":
            self.reseau.connecter_client(self.vue_reseau.ip_saisie)

        elif action_id == "valider":
            if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                return
            self.placement.valider_mot()

        elif action_id == "annuler":
            self.placement.annuler()
            self._set_message("")

        elif action_id == "passer":
            if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                return
            if self.reseau.mode_reseau:
                self.reseau.envoyer_passer()
            else:
                self.partie.passertour(self.num_joueur_courant)
                self.placement.annuler()
                self._passer_au_joueur_suivant()

        elif action_id == "defausser":
            if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                return
            if not self.placement.mode_defausse:
                self.placement.mode_defausse = True
                self._set_message("Sélectionnez les lettres puis re-cliquez DÉFAUSSER", erreur=False)
            else:
                self.placement.defausser()

        elif action_id == "changer_mot":
            if self.reseau.mode_reseau and not self.reseau.est_mon_tour():
                return
            if self.reseau.mode_reseau:
                self.reseau.envoyer_changer_mot()
                self.placement.annuler()
            else:
                self.partie.changermotsecret(self.num_joueur_courant)
                self.placement.annuler()
                self._passer_au_joueur_suivant()
                self._set_message("Mot imposé changé — tour passé", erreur=False)

    #  Helpers
    
    def _maj_label_volume(self):
        try:
            label = self.vue_options.get_element("volume_label")
            label.modifier_texte(f"{round(self.volume * 100)}%")
        except KeyError:
            pass

    def _reinitialiser_partie(self):
        """Remet à zéro l'état du jeu pour commencer une nouvelle partie propre."""
        self.reseau.reinitialiser()

        self.num_joueur_courant = 1
        self.placement.annuler()

        self.ia_ctrl = None
        self.popup.popup_victoire = False
        pygame.mixer.music.play(-1)

        self.partie.sacLettres = self.partie._initialiserSacLettres()
        self.partie.plateau = [[' ' for _ in range(15)] for _ in range(15)]
        self.partie.tour = 0
        self.partie.joueur1 = self.partie._initialiserJoueur()
        self.partie.joueur2 = self.partie._initialiserJoueur()
        self.partie.terminee = False
        self.partie.passes_consecutifs = 0
        
        self._set_message("")
        self._maj_boutons_chevalet()

    def _maj_affichage_jeu(self):
        # Mot imposé : toujours le NÔTRE (mon_num en réseau, joueur actif en local)
        if self.reseau.mode_reseau and self.reseau.mon_num is not None:
            mon_joueur = self.partie.joueur1 if self.reseau.mon_num == 1 else self.partie.joueur2
        else:
            mon_joueur = self._joueur_courant()

        self.vue_jeu.get_element("score_j1").modifier_texte(
            f"Score J1 : {self.partie.joueur1.score} pts")
        self.vue_jeu.get_element("score_j2").modifier_texte(
            f"Score J2 : {self.partie.joueur2.score} pts")
        self.vue_jeu.get_element("mot_impose").modifier_texte(mon_joueur.mot_secret)

        if self.reseau.mode_reseau:
            self.vue_jeu.get_element("sac").modifier_texte(
                str(self.reseau.lettres_restantes))
        else:
            self.vue_jeu.get_element("sac").modifier_texte(
                str(len(self.partie.sacLettres)))

        if self.reseau.mode_reseau:
            if self.reseau.est_mon_tour():
                info = f"Votre tour (Joueur {self.reseau.mon_num})"
            else:
                adv = 2 if self.reseau.mon_num == 1 else 1
                info = f"Tour du Joueur {adv} — attendez..."
        else:
            info = f"Tour du Joueur {self.num_joueur_courant}"
        self.vue_jeu.get_element("tour_info").modifier_texte(info)

    def _set_message(self, texte, erreur=True):
        el = self.vue_jeu.get_element("message")
        el.modifier_texte(texte)
        el.couleur = (255, 100, 100) if erreur else (100, 220, 100)
        if texte and erreur:
            self.sfx_error.play()

    def _retour_menu(self):
        """Callback popup : réinitialise et revient au menu."""
        self._historique.clear()
        self._reinitialiser_partie()
        self._changer_vue(self.vue_menu)

    def _quitter(self):
        """Callback popup : quitte le jeu."""
        pygame.quit()
        exit()

    def _set_joueur_actif(self, num):
        """Callback réseau : met à jour le joueur courant."""
        self.num_joueur_courant = num

    def _activer_vue_jeu_si_besoin(self):
        """Callback réseau : bascule vers la vue jeu si on n'y est pas encore."""
        if self.vue_active is not self.vue_jeu:
            self._changer_vue(self.vue_jeu)

    def _changer_vue(self, nouvelle_vue):
        self.vue_active.afficher = False
        self.vue_active = nouvelle_vue
        self.vue_active.afficher = True

    def _joueur_courant(self):
        """
        Mode réseau : retourne NOTRE joueur (mon_num), pour afficher notre chevalet.
        Mode local  : retourne le joueur dont c'est le tour.
        """
        if self.reseau.mode_reseau and self.reseau.mon_num is not None:
            return self.partie.joueur1 if self.reseau.mon_num == 1 else self.partie.joueur2
        return self.partie.joueur1 if self.num_joueur_courant == 1 else self.partie.joueur2

    def _demarrer_jeu_ia(self):
        self.ia_ctrl = IAController(
            partie       = self.partie,
            num_joueur   = 2,
            on_fin_tour  = self._apres_tour_ia,
            on_message   = self._set_message,
            on_fin_partie= self.popup.declencher_fin_partie,
        )
        self.ia_ctrl.demarrer(self.partie)
        self._changer_vue(self.vue_jeu)
        self._maj_affichage_jeu()

    def _apres_tour_ia(self):
        """Repasse la main au joueur humain après le tour de l'IA."""
        self.num_joueur_courant = 1
        self._maj_boutons_chevalet()
        self._maj_affichage_jeu()

    def _passer_au_joueur_suivant(self):
        self.num_joueur_courant = 2 if self.num_joueur_courant == 1 else 1
        self._maj_boutons_chevalet()
        self._maj_affichage_jeu()
        self._set_message("")
        if self.partie.terminee:
            self.popup.declencher_fin_partie()
            return
        if self.ia_ctrl and self.num_joueur_courant == 2:
            self.ia_ctrl.jouer_tour()
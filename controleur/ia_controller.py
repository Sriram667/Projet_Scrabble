from modele.joueur import JoueurIA


class IAController:
    """
    Gère le démarrage et le déroulement du tour de l'IA.
    """

    def __init__(self, partie, num_joueur=2,
                 on_fin_tour=None, on_message=None, on_fin_partie=None):
        self.partie       = partie
        self.num_joueur   = num_joueur
        self.on_fin_tour  = on_fin_tour  or (lambda: None)
        self.on_message   = on_message   or (lambda texte, erreur=False: None)
        self.on_fin_partie = on_fin_partie or (lambda: None)

        self.ia: JoueurIA = (
            partie.joueur1 if num_joueur == 1 else partie.joueur2
        )

    def demarrer(self, partie):
        """
        Initialise le joueur IA dans la partie.
        """
        j = partie.joueur1 if self.num_joueur == 1 else partie.joueur2
        self.ia = JoueurIA(
            dictionnaire_obj=partie.dictionnaire,
            chevalet=j.chevalet[:],
            score=j.score,
            mot_secret=j.mot_secret,
        )
        if self.num_joueur == 1:
            partie.joueur1 = self.ia
        else:
            partie.joueur2 = self.ia

    def jouer_tour(self):
        """
        Fait jouer l'IA pour un tour complet.
        Équivaut à l'ancien _tour_ia() dans GameController.
        """
        action = self.ia.choisir_action(self.partie)
        type_action = action[0]
        msg = ""

        if type_action == "poser_mot":
            _, mot, r0, c0, direction = action
            ok = self.partie.poserMot(mot, r0, c0, direction, self.num_joueur)
            if ok:
                msg = f"IA a joué : {mot}"
            else:
                self.partie.passertour(self.num_joueur)
                msg = "IA a passé (coup invalide)"

        elif type_action == "defausser":
            lettres = action[1]
            ok = self.partie.defausserLettres(lettres, self.num_joueur)
            msg = f"IA a défaussé {len(lettres)} lettre(s)" if ok else "IA a passé"
            if not ok:
                self.partie.passertour(self.num_joueur)

        else:
            self.partie.passertour(self.num_joueur)
            msg = "L'IA a passé son tour"

        if self.partie.terminee:
            self.on_fin_partie()
        else:
            self.on_fin_tour()
            self.on_message(msg, erreur=False)
import random


tab_facile    = {'passer': 4, 'defausser': 2, 'poser_mot': 4}
tab_normale   = {'passer': 3, 'defausser': 1, 'poser_mot': 6}
tab_difficile = {'passer': 1, 'defausser': 1, 'poser_mot': 8}


class Joueur:
    def __init__(self, chevalet=None, score=0, mot_secret=""):
        self.chevalet = chevalet or []
        self.score = score
        self.mot_secret = mot_secret
        self.dernier_coup = None


class JoueurIA(Joueur):
    def __init__(self, dictionnaire_obj, chevalet=None, score=0, mot_secret="", diff=None):
        super().__init__(chevalet, score, mot_secret)
        self.dictionnaire = dictionnaire_obj._liste_mots
        self.dict_obj     = dictionnaire_obj

        if diff == "facile":
            self.diff = tab_facile
        elif diff == "difficile":
            self.diff = tab_difficile
        else:
            self.diff = tab_normale

    def choisir_action(self, partie):
        """
        Choisit une action selon les probabilités définies par le niveau de difficulté.
        Les poids du tableau orientent le tirage, mais l'action n'est exécutée que si
        elle est réellement possible (sinon on tombe en cascade sur la suivante).
        """

        if self.mot_secret:
            coup = self._peut_poser_mot(self.mot_secret, partie.plateau, self.chevalet)
            if coup:
                mot_complet, (r0, c0), direction = coup
                return ("poser_mot", mot_complet, r0, c0,
                        "H" if direction == "horizontal" else "V")


        total = self.diff['passer'] + self.diff['defausser'] + self.diff['poser_mot']
        n = random.randint(1, total)
        if n <= self.diff['passer']:
            action_tiree = 'passer'
        elif n <= self.diff['passer'] + self.diff['defausser']:
            action_tiree = 'defausser'
        else:
            action_tiree = 'poser_mot'

        if action_tiree == "poser_mot":
            coup = self.chercher_coup_simple(partie)
            if coup:
                mot_complet, (r0, c0), direction = coup
                return ("poser_mot", mot_complet, r0, c0,
                        "H" if direction == "horizontal" else "V")
            # Pas de coup possible -> défausser
            action_tiree = "defausser"

        if action_tiree == "defausser":
            if len(partie.sacLettres) >= 1 and self.chevalet:
                nb = random.randint(1, min(3, len(self.chevalet)))
                return ("defausser", random.sample(self.chevalet, nb))
            # Sac vide → passer
            action_tiree = "passer"

        # "passer" ou fallback final
        return ("passer", None)

    def chercher_coup_simple(self, partie):
        plateau      = partie.plateau
        lettres_main = list(self.chevalet)

        board_letters = {cell for row in plateau for cell in row if cell != ' '}
        available     = set(lettres_main) | board_letters | {'?'}

        candidats = [
            mot for mot in self.dictionnaire
            if 2 <= len(mot) <= 15 and all(l in available for l in mot)
        ]
        random.shuffle(candidats)

        for mot in candidats[:500]:
            coup = self._peut_poser_mot(mot, plateau, lettres_main)
            if coup:
                return coup

        return None

    def _peut_poser_mot(self, mot, plateau, lettres_main):
        lettres_main = list(lettres_main)
        plateau_vide = all(plateau[r][c] == ' ' for r in range(15) for c in range(15))

        if plateau_vide:
            return self._placer_premier_mot(mot, lettres_main)

        return self._placer_mot_normal(mot, plateau, lettres_main)

    def _placer_premier_mot(self, mot, lettres_main):
        for direction in ["horizontal", "vertical"]:
            dr = 0 if direction == "horizontal" else 1
            dc = 1 if direction == "horizontal" else 0
            for index_mot in range(len(mot)):
                r0 = 7 - dr * index_mot
                c0 = 7 - dc * index_mot
                if r0 < 0 or c0 < 0:
                    continue
                if r0 + dr * (len(mot) - 1) > 14 or c0 + dc * (len(mot) - 1) > 14:
                    continue
                tmp = list(lettres_main)
                valide = True
                for lettre in mot:
                    if lettre in tmp:
                        tmp.remove(lettre)
                    elif '?' in tmp:
                        tmp.remove('?')
                    else:
                        valide = False
                        break
                if valide:
                    return (mot, (r0, c0), direction)
        return None

    def _placer_mot_normal(self, mot, plateau, lettres_main):
        for r in range(15):
            for c in range(15):
                lettre_plateau = plateau[r][c]
                if lettre_plateau == ' ' or lettre_plateau not in mot:
                    continue

                for index_mot in [i for i, L in enumerate(mot) if L == lettre_plateau]:
                    for direction in ["horizontal", "vertical"]:
                        dr = 0 if direction == "horizontal" else 1
                        dc = 1 if direction == "horizontal" else 0

                        r0 = r - dr * index_mot
                        c0 = c - dc * index_mot
                        if r0 < 0 or c0 < 0:
                            continue
                        if r0 + dr * (len(mot) - 1) > 14 or c0 + dc * (len(mot) - 1) > 14:
                            continue

                        lettres_restantes = list(lettres_main)
                        valide = True
                        preview = {}
                        for i, lettre in enumerate(mot):
                            rr = r0 + dr * i
                            cc = c0 + dc * i
                            case = plateau[rr][cc]
                            if case == ' ':
                                if lettre in lettres_restantes:
                                    lettres_restantes.remove(lettre)
                                elif '?' in lettres_restantes:
                                    lettres_restantes.remove('?')
                                else:
                                    valide = False
                                    break
                                preview[(rr, cc)] = lettre
                            elif case != lettre:
                                valide = False
                                break

                        if not valide:
                            continue

                        r_end = r0 + dr * (len(mot) - 1)
                        c_end = c0 + dc * (len(mot) - 1)

                        rs, cs = r0, c0
                        while rs - dr >= 0 and cs - dc >= 0 \
                                and plateau[rs - dr][cs - dc] != ' ':
                            rs -= dr
                            cs -= dc

                        re, ce = r_end, c_end
                        while re + dr <= 14 and ce + dc <= 14 \
                                and plateau[re + dr][ce + dc] != ' ':
                            re += dr
                            ce += dc

                        mot_complet = ""
                        rr, cc = rs, cs
                        ok_reconstruction = True
                        while True:
                            if plateau[rr][cc] != ' ':
                                mot_complet += plateau[rr][cc]
                            elif (rr, cc) in preview:
                                mot_complet += preview[(rr, cc)]
                            else:
                                ok_reconstruction = False
                                break
                            if rr == re and cc == ce:
                                break
                            rr += dr
                            cc += dc

                        if ok_reconstruction and self.dict_obj.mot_valide(mot_complet):
                            return (mot_complet, (rs, cs), direction)

        return None
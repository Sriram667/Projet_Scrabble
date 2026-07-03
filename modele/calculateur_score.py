class calculateur_score:
    def __init__(self, tab_lettres, tab_cases):
        self.lettresPoints = tab_lettres
        self.casePoints = tab_cases

    def _trouverNouvellesLettres(self, tab_actuelle, tab_precedente):
        nouvelles = []
        for r in range(15):
            for c in range(15):
                if (tab_precedente[r][c] == " " or tab_precedente[r][c] == "") and tab_actuelle[r][c] != " ":
                    nouvelles.append((r, c))
        return nouvelles

    def _extraireMot(self, grid, r, c, dr, dc):
        # Remonter au début du mot
        start_r, start_c = r, c
        while start_r - dr >= 0 and start_c - dc >= 0 and grid[start_r - dr][start_c - dc].strip():
            start_r -= dr
            start_c -= dc

        mot = ""
        cases = []
        curr_r, curr_c = start_r, start_c
        while curr_r < 15 and curr_c < 15 and grid[curr_r][curr_c].strip():
            mot += grid[curr_r][curr_c]
            cases.append((curr_r, curr_c))
            curr_r += dr
            curr_c += dc

        return mot, cases

    def _scoreMot(self, mot, cases, nouvelles_lettres):
        total_lettres = 0
        multiplicateur_mot = 1

        for i, (r, c) in enumerate(cases):
            lettre = mot[i]
            valeur = self.lettresPoints.get(lettre, 0)

            # Le bonus ne s'applique que si la case vient d'être recouverte
            if (r, c) in nouvelles_lettres:
                bonus = self.casePoints[r][c]
                if bonus == "LD": valeur *= 2
                elif bonus == "LT": valeur *= 3
                elif bonus == "MD": multiplicateur_mot *= 2
                elif bonus == "MT": multiplicateur_mot *= 3
            
            total_lettres += valeur

        return total_lettres * multiplicateur_mot

    def calculerScore(self, tab_actuelle, tab_precedente):
        nouvelles_lettres = self._trouverNouvellesLettres(tab_actuelle, tab_precedente)
        if not nouvelles_lettres:
            return 0

        total_tour = 0
        mots_identifies = set() 

        for (r, c) in nouvelles_lettres:
            # On vérifie les deux directions pour chaque nouvelle lettre
            for dr, dc in [(0, 1), (1, 0)]:
                mot, cases = self._extraireMot(tab_actuelle, r, c, dr, dc)
                
                identifiant_mot = tuple(cases)
                if len(mot) > 1 and identifiant_mot not in mots_identifies:
                    total_tour += self._scoreMot(mot, cases, nouvelles_lettres)
                    mots_identifies.add(identifiant_mot)

        return total_tour
"""
serveur.py  —  Lance la partie côté serveur.
Lancer : python reseau/serveur.py   (depuis la racine du projet)
"""
import socket, threading, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modele.partie import Partie

HOST = "0.0.0.0"
PORT = 55000
CHEMIN_DICT = Path(__file__).parent.parent / "Dictionnaire_ODS.txt"


class Serveur:
    def __init__(self):
        self.partie  = Partie(CHEMIN_DICT)
        self.clients = {}        # {1: conn, 2: conn}
        self.lock    = threading.Lock()

    def demarrer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((HOST, PORT))
            srv.listen(2)
            print(f"[SERVEUR] En attente sur le port {PORT}...")

            for num in [1, 2]:
                conn, addr = srv.accept()
                self.clients[num] = conn
                print(f"[SERVEUR] Joueur {num} connecté depuis {addr}")
                self._envoyer(conn, {"type": "bienvenue", "num_joueur": num})

            print("[SERVEUR] Partie lancée !")
            self._diffuser_etat()

            threads = [
                threading.Thread(target=self._ecouter, args=(n, c), daemon=True)
                for n, c in self.clients.items()
            ]
            for t in threads: t.start()
            for t in threads: t.join()


    def _ecouter(self, num_joueur, conn):
        with conn:
            while True:
                msg = self._recevoir(conn)
                if msg is None:
                    print(f"[SERVEUR] Joueur {num_joueur} déconnecté.")
                    break
                self._traiter(num_joueur, msg)

    def _traiter(self, num_joueur, msg):
        if self.partie.terminee:
            return

        joueur_attendu = 1 if self.partie.tour % 2 == 0 else 2
        if num_joueur != joueur_attendu:
            self._envoyer(self.clients[num_joueur], {
                "type": "erreur", "message": "Ce n'est pas votre tour."
            })
            return

        action = msg.get("action")
        ok = False
        erreur = ""

        with self.lock:
            if action == "poser_mot":
                ok = self.partie.poserMot(
                    msg["mot"], msg["ligne"], msg["colonne"],
                    msg["direction"], num_joueur
                )
                if not ok: erreur = "Mot invalide ou placement impossible."

            elif action == "passer":
                ok = self.partie.passertour(num_joueur)

            elif action == "defausser":
                ok = self.partie.defausserLettres(msg["lettres"], num_joueur)
                if not ok: erreur = "Défausse impossible."

            elif action == "changer_mot":
                ok = self.partie.changermotsecret(num_joueur)

        if not ok:
            self._envoyer(self.clients[num_joueur], {"type": "erreur", "message": erreur})
        else:
            self._diffuser_etat()

    def _diffuser_etat(self):
        for num, conn in self.clients.items():
            self._envoyer(conn, self._etat_pour(num))

    def _etat_pour(self, num):
        j1, j2 = self.partie.joueur1, self.partie.joueur2
        moi    = j1 if num == 1 else j2
        etat = {
            "type"           : "etat",
            "tour"           : self.partie.tour,
            "joueur_actif"   : 1 if self.partie.tour % 2 == 0 else 2,
            "mon_num"        : num,
            "scores"         : {"1": j1.score, "2": j2.score},
            "mon_chevalet"   : moi.chevalet,
            "mon_mot_secret" : moi.mot_secret,
            "plateau"        : self.partie.plateau,
            "lettres_restantes": len(self.partie.sacLettres),
            "terminee"       : self.partie.terminee,
        }
        if self.partie.terminee:
            etat["vainqueur"] = self.partie.vainqueur()
        return etat

    def _envoyer(self, conn, data):
        try:
            conn.sendall((json.dumps(data) + "\n").encode())
        except OSError:
            pass

    def _recevoir(self, conn):
        buf = b""
        try:
            while b"\n" not in buf:
                chunk = conn.recv(4096)
                if not chunk: return None
                buf += chunk
            return json.loads(buf.split(b"\n")[0].decode())
        except (OSError, json.JSONDecodeError):
            return None


if __name__ == "__main__":
    Serveur().demarrer()

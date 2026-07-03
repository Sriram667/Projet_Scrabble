"""
client.py
---------
Client réseau du Scrabble.
- Se connecte au serveur
- Reçoit l'état de la partie et l'affiche via GameController
- Envoie les actions du joueur au serveur

"""

import socket
import threading
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

HOST_PAR_DEFAUT = "127.0.0.1"
PORT = 55000


class Client:
    def __init__(self, host=HOST_PAR_DEFAUT):
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.num_joueur = None
        self.etat = None                  # dernier état reçu du serveur
        self.on_etat_recu = None          # callback appelé quand l'état change
        self._buffer = b""

    def connecter(self):
        """Bloquant : attend la connexion au serveur."""
        print(f"[CLIENT] Connexion à {self.host}:{PORT}...")
        self.sock.connect((self.host, PORT))
        print("[CLIENT] Connecté !")

        # Le premier message est toujours le numéro de joueur
        msg = self._recevoir()
        if msg and msg.get("type") == "bienvenue":
            self.num_joueur = msg["num_joueur"]
            print(f"[CLIENT] Vous êtes le Joueur {self.num_joueur}")

        # Lance l'écoute des messages serveur en arrière-plan
        t = threading.Thread(target=self._boucle_reception, daemon=True)
        t.start()

    def envoyer_poser_mot(self, mot, ligne, colonne, direction):
        self._envoyer({
            "action": "poser_mot",
            "mot": mot,
            "ligne": ligne,
            "colonne": colonne,
            "direction": direction
        })

    def envoyer_passer(self):
        self._envoyer({"action": "passer"})

    def envoyer_defausser(self, lettres):
        self._envoyer({"action": "defausser", "lettres": lettres})

    def envoyer_changer_mot(self):
        self._envoyer({"action": "changer_mot"})

    def _boucle_reception(self):
        while True:
            msg = self._recevoir()
            if msg is None:
                print("[CLIENT] Déconnecté du serveur.")
                break

            if msg["type"] == "etat":
                self.etat = msg
                if self.on_etat_recu:
                    self.on_etat_recu(msg)  # notifie l'interface

            elif msg["type"] == "erreur":
                print(f"[SERVEUR] Erreur : {msg['message']}")
                if self.on_etat_recu:
                    # On notifie quand même pour que l'UI puisse afficher l'erreur
                    self.on_etat_recu({"type": "erreur", "message": msg["message"]})


    def _envoyer(self, data):
        try:
            msg = json.dumps(data) + "\n"
            self.sock.sendall(msg.encode("utf-8"))
        except OSError as e:
            print(f"[CLIENT] Erreur envoi : {e}")

    def _recevoir(self):
        try:
            while b"\n" not in self._buffer:
                chunk = self.sock.recv(4096)
                if not chunk:
                    return None
                self._buffer += chunk
            ligne, self._buffer = self._buffer.split(b"\n", 1)
            return json.loads(ligne.decode("utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def fermer(self):
        self.sock.close()



if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else HOST_PAR_DEFAUT
    client = Client(host)
    client.connecter()

    print("Commandes : poser / passer / defausser / changer / quitter")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "quitter":
            break
        elif cmd == "passer":
            client.envoyer_passer()
        elif cmd == "changer":
            client.envoyer_changer_mot()
        elif cmd == "poser":
            mot = input("Mot : ").strip()
            ligne = int(input("Ligne (0-14) : "))
            col = int(input("Colonne (0-14) : "))
            dir = input("Direction (H/V) : ").strip()
            client.envoyer_poser_mot(mot, ligne, col, dir)
        elif cmd == "defausser":
            lettres = input("Lettres à défausser (ex: A B C) : ").upper().split()
            client.envoyer_defausser(lettres)

    client.fermer()

import socket
import threading
import time

from reseau.serveur import Serveur
from reseau.client import Client


class NetworkController:

    def __init__(self, partie, vue_reseau, vue_jeu,
                 on_maj_chevalet, on_maj_affichage,
                 on_changer_vue_jeu, on_fin_partie,
                 on_set_message, on_joueur_actif):
        self.partie     = partie
        self.vue_reseau = vue_reseau
        self.vue_jeu    = vue_jeu

        self._on_maj_chevalet    = on_maj_chevalet    # ()
        self._on_maj_affichage   = on_maj_affichage   # ()
        self._on_changer_vue_jeu = on_changer_vue_jeu # () — bascule vers vue_jeu si besoin
        self._on_fin_partie      = on_fin_partie      # ()
        self._on_set_message     = on_set_message     # (texte)
        self._on_joueur_actif    = on_joueur_actif    # (num) — met à jour num_joueur_courant

        self.client            = None
        self.mon_num           = None
        self.mode_reseau       = False
        self.lettres_restantes = 100
        self._joueur_actif     = 1

   
    def est_mon_tour(self):
        """En mode réseau : est-ce le tour de CE client ?"""
        if not self.mode_reseau:
            return True
        return self.mon_num == self._joueur_actif

   
    def reinitialiser(self):
        if self.client:
            self.client.fermer()
        self.client            = None
        self.mon_num           = None
        self.mode_reseau       = False
        self.lettres_restantes = 100

    
    def afficher_ip_locale(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                ip = "inconnue"
        self.vue_reseau.get_element("ip_locale").modifier_texte(f"Votre IP locale : {ip}")

    def heberger(self):
        """Lance le serveur en arrière-plan puis connecte automatiquement ce client."""
        self.vue_reseau.get_element("msg_reseau").modifier_texte(
            "Serveur lance — en attente du 2e joueur...")

        threading.Thread(target=lambda: Serveur().demarrer(), daemon=True).start()

        def auto_connect():
            time.sleep(0.5)
            self.connecter_a("127.0.0.1")

        threading.Thread(target=auto_connect, daemon=True).start()

    def connecter_client(self, ip_saisie):
        ip = ip_saisie.strip()
        if not ip:
            self.vue_reseau.get_element("msg_reseau").modifier_texte("Entrez une IP valide")
            return
        self.connecter_a(ip)

    def connecter_a(self, ip):
        try:
            self.client = Client(ip)
            self.client.on_etat_recu = self._on_etat_reseau
            self.client.connecter()
            self.mode_reseau = True
            self.vue_reseau.get_element("msg_reseau").modifier_texte(
                "Connecte ! En attente du 2e joueur...")
        except Exception as e:
            self.mode_reseau = False
            self.vue_reseau.get_element("msg_reseau").modifier_texte(f"Erreur : {e}")

    

    def envoyer_poser_mot(self, mot, ligne, colonne, direction):
        self.client.envoyer_poser_mot(mot, ligne, colonne, direction)

    def envoyer_passer(self):
        self.client.envoyer_passer()

    def envoyer_defausser(self, lettres):
        self.client.envoyer_defausser(lettres)

    def envoyer_changer_mot(self):
        self.client.envoyer_changer_mot()



    def _on_etat_reseau(self, etat):
        """
        Appelé depuis le thread réseau à chaque message du serveur.
        Règle d'or : on ne touche JAMAIS à mon_num après l'initialisation.
        """
        if etat.get("type") == "erreur":
            self._on_set_message(etat["message"])
            return

        # mon_num est assigné une seule fois au début de la partie
        if self.mon_num is None:
            self.mon_num = etat["mon_num"]

        # Joueur actif (change à chaque coup)
        self._joueur_actif = etat["joueur_actif"]
        self._on_joueur_actif(etat["joueur_actif"])

        # Scores
        self.partie.joueur1.score = etat["scores"]["1"]
        self.partie.joueur2.score = etat["scores"]["2"]

        # Plateau
        self.partie.plateau = etat["plateau"]

        # Chevalet et mot secret : toujours ceux de MON joueur
        mon_joueur = self.partie.joueur1 if self.mon_num == 1 else self.partie.joueur2
        mon_joueur.chevalet   = etat["mon_chevalet"]
        mon_joueur.mot_secret = etat["mon_mot_secret"]

        # Lettres restantes dans le sac
        self.lettres_restantes = etat["lettres_restantes"]

        # Fin de partie
        if etat.get("terminee"):
            self.partie.terminee = True
            self._on_fin_partie()

        # Rafraîchir l'interface
        self._on_maj_chevalet()
        self._on_maj_affichage()

        # Passer à la vue jeu dès le premier état reçu
        self._on_changer_vue_jeu()

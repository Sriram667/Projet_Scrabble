# Projet Scrabble

## 1. Description du projet
Ce projet vise à recréer le jeu de **Scrabble** pour être joué sur sa propre machine.

**Le Scrabble** (Produit de Hasbro, Inc) est un jeu de société et un jeu de lettres où l'objectif est de **cumuler des points**,
sur la base de tirages aléatoires de lettres, en créant des mots sur une grille carrée, dont certaines cases sont primées.
(Source : Wikipédia)

## 2. Déroulement de la partie
La partie se déroule sur **un plateau de 15 sur 15** avec des cases doublant ou triplant des lettres ou des mots. Les mots placés doivent 
être dans **le dictionnaire français** et placés **correctement** sur le plateau en les connectant à des mots existants.

Chaque joueur a **un chevalet de 7 lettres**, avec des lettres choisies aléatoirement au début de la partie et après avoir joué un coup, d'un
sac de lettre, avec un nombre défini de lettre dans un ordre aléatoire. 
Un joueur a le choix soit de **jouer un coup** en plaçant ses lettres sur le plateau, soit de **défausser** un certain nombre de ses lettres
et terminer son tour, soit de simplement **passer** son tour.

Le score est calculé en fonction des lettres jouées, des mots formés avec les mots existant et les cases bonus. Chaque joueur à aussi un
**mot bonus** qui lui rapporte **15 points bonus** s'il arrive à le jouer. Les joueurs ont la possibilité de changer le mot en contrepartie
de terminer leur tour. Jouer les 7 lettres du chevalet d'un coup récompense le joueur avec **50 points bonus**.

La partie se termine quand le sac de lettre est **vide**, et le joueur ayant **le plus de point** gagne la partie.

## 3. Modes de jeu 
Notre projet implémente **3 modes de jeu** : 
### -Deux joueurs en local :
Deux joueurs jouent tour à tour sur la même machine locale.

### -Joueur en ligne local :
Un joueur peut rejoindre le serveur d'un autre joueur dans le même réseau grâce à son adresse IP pour jouer ensemble.

### -Joueur IA :
Une IA avec une difficulté fixe simule un deuxième joueur pour pouvoir jouer seul.

## 4. Installation et lancement
Python3 **nécessaire**.  
Bibliothèque pygame_ce **nécessaire**. Pour l'installer :
```bash 
pip install pygame-ce
```
Les fichiers doivent rester dans leur dossier.  
Pour jouer, se positionner sur le dossier principal et lancer le fichier main.py :

```bash 
python main.py   
```

EL HARRAK Ahmed
BENGHEMINA Malek
SOUMEILLAN Mattéo

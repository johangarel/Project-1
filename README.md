# **PROJECT 1**

***---------------------------------------------------------------------------------------------------------------------------***

### ***ENGLISH :***

***---------------------------------------------------------------------------------------------------------------------------***

###### My first "official" python project. A maze game with pygame.

###### This is an alpha version of the game that has a pretty limited basic setup.



##### **How to play:**

* Install Pygame using the command: `py -3.6 -m pip install pygame` OR `python -m pip install pygame`
* Run main.py

\---------------------------------------------------------------------------------------------------------------------------

##### **Features:**

* 5 different mazes
* Teleporters
* Traps
* Keyed doors
* Fog of war and light system
* Sub map system
* Timer and record time
* Star system progression
* A tutorial menu to help with the controls

\---------------------------------------------------------------------------------------------------------------------------

##### **How to create a new level :**

* First, create on levels/ a new .txt file where you will have to make a grid of the level.



&#x09;Legend :

&#x09;W = Wall

&#x09;P = Player Spawn

&#x09;T = Trap

&#x09;S = Special teleporter (to load another map)

&#x09;lower case letter = Key

&#x09;Other upper case letter = Door (ex. Key "a" opens Door "A")

&#x09;Number = Teleporter

&#x09;Space = Nothing



* Then, go into scripts/ and open the python file settings.py, and modify the variable LEVEL\_CONFIGS. Do like previous levels added, put the number id, the level text file, a teleporter list, and if you want to activate the "fog of war" option. To make a teleporter list, add the index of the destination portal in the index of the entry portal in the list. For example, if I want tp 0 to go to tp 1, then I add 1 to index 0 in the tp list.



***---------------------------------------------------------------------------------------------------------------------------***

### ***FRANCAIS :***

***---------------------------------------------------------------------------------------------------------------------------***

###### Mon premier projet Python « officiel ». Un jeu de labyrinthe avec Pygame.

###### Il s'agit d'une version alpha du jeu avec une configuration de base assez limitée.



##### **Comment jouer :**

* Installer pygame via la commande : `py -3.6 -m pip install pygame` OU `python -m pip install pygame`
* Exécutez main.py

\---------------------------------------------------------------------------------------------------------------------------

##### **Fonctionnalités :**

* 5 labyrinthes différents
* Téléporteurs
* Pièges
* Portes à clés
* Un système de sous-cartes
* Un système fog of war et de lumière
* Chronomètre et temps record
* Progression par système d'étoiles
* Un menu tutoriel pour aider sur les touches

\---------------------------------------------------------------------------------------------------------------------------

##### **Comment créer un nouveau niveau :**

* Créez d'abord un fichier .txt dans le répertoire levels/ où vous définirez la grille du niveau.

&#x09;

&#x09;Légende :

&#x09;W = Mur

&#x09;P = Point d'apparition du joueur

&#x09;T = Piège

&#x09;S = Téléporteur spécial (charger une autre carte)

&#x09;Lettre minuscule = Clé

&#x09;Autre lettre majuscule = Porte (ex. : la clé "a" ouvre la porte "A")

&#x09;Chiffre = Téléporteur

&#x09;Espace = Rien



* Ensuite, allez dans scripts/ et ouvrez le fichier python settings.py, puis modifiez la variable LEVEL\_CONFIGS. Procédez comme pour les niveaux précédents : indiquez le numéro du niveau, le fichier texte du niveau , une liste de téléporteurs et si vous voulez activer l'option "fog of war". Pour créer une liste de téléporteurs, ajoutez l'index du portail de destination à l'index du portail d'entrée dans la liste. Par exemple, si vous souhaitez que le téléporteur 0 mène au téléporteur 1, mettez 1 à l'index 0 dans la liste des téléporteurs.

&#x20;


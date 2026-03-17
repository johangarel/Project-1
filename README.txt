ENGLISH :

My first "official" python project. A maze game with pygame.
This is an alpha version of the game that has a pretty limited basic setup.

To launch the game, download the requirements from requirements.txt and then run the Project 1.py code. I'll let you see the different features for yourself. (Tap the book icon with the British flag if you need help!)


If you want to participate into developing the project, here is how to create a new level :
First, create on levels/ a new .txt file where you will have to make a grid of the level.
W = Wall
P = Player Spawn
T = Trap
lower case letter = Key
Other upper case letter = Door (ex. Key a opens Door A)
Number = Teleporter
Space = Nothing

Then, go into the main script Project 1, and modify in the maze building section (line 500+) the variable level_configs. Do like previous levels added, put the number id, the level text file, and a teleporter list.
To make a teleporter list, add the index of the destination portal in the index of the entry portal in the list. For example, if I want tp 0 to go to tp 1, then I add 1 to index 0 in the tp list.


FRANCAIS :

Mon premier projet Python « officiel ». Un jeu de labyrinthe avec Pygame.
Il s'agit d'une version alpha du jeu avec une configuration de base assez limitée.

Pour lancez le jeu, télécharger les exigences depuis requirements.txt puis exécuter le code Project 1.py . Je vous laisse voir par vous même les différentes fonctionnalités. (Appuyez sur l'icone du livre avec le drapeau français si vous avez besoin d'aide !)


Si vous souhaitez participer au développement du projet, voici comment créer un nouveau niveau :
Créez d'abord un fichier .txt dans le répertoire levels/ où vous définirez la grille du niveau.
W = Mur
P = Point d'apparition du joueur
T = Piège
Lettre minuscule = Clé
Autre lettre majuscule = Porte (ex. : la clé "a" ouvre la porte "A")
Chiffre = Téléporteur
Espace = Rien

Ensuite, accédez au script principal du Projet 1 et modifiez la variable level_configs dans la section de création du labyrinthe (à partir de la ligne 500). Procédez comme pour les niveaux précédents : indiquez le numéro du niveau, le fichier texte du niveau et une liste de téléporteurs.
Pour créer une liste de téléporteurs, ajoutez l'index du portail de destination à l'index du portail d'entrée dans la liste. Par exemple, si vous souhaitez que le téléporteur 0 mène au téléporteur 1, mettez 1 à l'index 0 dans la liste des téléporteurs.
 
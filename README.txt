ENGLISH :

My first "official" python project. A maze game with pygame.
This is an alpha version of the game that has a pretty limited basic setup.

To launch the game, download the requirements from requirements.txt and then run the Project 1.py code. I'll let you see the different features for yourself.


If you want to participate into developing the project, here is how to create a new level :
First, create on levels/ a new .txt file where you will have to make a grid of the level.
W = Wall
P = Player Spawn
T = Trap
lower case letter = Key
Other upper case letter = Door (ex. Key a opens Door A)
Number = Teleporter
Space = Nothing

Then, go into the main script Project 1, and add to the maze building section a variable LEVEL_[N]_MAP where you use the function load_map to import the text file that you just have written.

After that's done, add also a LEVEL_[N]_TP list variable where you indicate which teleporter leads to. For exemple, if I want to have a tp 0 that leads to tp 1, then I put the number 1 on index 0.

Finally, add a variable LEVEL_[N] that uses build_level and add to wall_list index 0 of LEVEL_[N], add to special_objects_list index 1 of LEVEL_[N], index 2 of LEVEL_[N] to spawn_point_list and LEVEL_[N]_MAP to LEVEL_MAP_LIST.

FRANCAIS :

Mon premier projet Python « officiel ». Un jeu de labyrinthe avec Pygame.
Il s'agit d'une version alpha du jeu avec une configuration de base assez limitée.

Pour lancez le jeu, télécharger les exigences depuis requirements.txt puis exécuter le code Project 1.py . Je vous laisse voir par vous même les différentes fonctionnalités.


Si vous souhaitez participer au développement du projet, voici comment créer un nouveau niveau :
Créez d'abord un fichier .txt dans le répertoire levels/ où vous définirez la grille du niveau.
W = Mur
P = Point d'apparition du joueur
T = Piège
Lettre minuscule = Clé
Autre lettre majuscule = Porte (ex. : la clé "a" ouvre la porte "A")
Chiffre = Téléporteur
Espace = Rien

Ensuite, dans le script principal du Projet 1, ajoutez à la section de création du labyrinthe une variable LEVEL_[N]_MAP et utilisez la fonction `load_map` pour importer le fichier texte que vous venez de créer.

Ajoutez ensuite une variable de liste `LEVEL_[N]_TP` indiquant la destination de chaque téléporteur. Par exemple, si je veux qu'un point de téléportation 0 mène au point de téléportation 1, j'attribue la valeur 1 à l'index 0 dans la liste.

Enfin, ajoutez une variable LEVEL_[N] qui utilise build_level et ajoutez son index 0 à wall_list, son index 1 à special_objects_list, son index 2 à spawn_point_list et LEVEL_[N]_MAP à LEVEL_MAP_LIST.
 
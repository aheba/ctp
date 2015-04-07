/*
Maël Valais, 2015
J'ai repris le fichier tsp.mod donné en exemple avec la doc GLPK,
et j'ai ajouté mes données : dix noeuds que j'ai repris d'un exemple
qu'on avait utilisé en TIA.

Il suffit donc d'utiliser ce fichier avec glpsol:
	glpsol -m tsp.mod

Notes: 
	set, param -> pour les données en entrée
	var -> pour les données de décision

	Pour aider au débuggage, j'utilise `display E;`
	avec n'importe quel objet.

	Pour le format `param: E : c` voir "Tabbing data format"
	Pour différence `param A:=`/`param A,...` voir "elemental set"
	Pour `{A:x<>0}` voir "Indexing expressions & predicate"
		ATTENTION: on écrit {A:x>0 and y>0} et pas {A:x>0,y>0}
	Pour `param A := (1,2) (3,4)` Vs. `param A{1,2}` pour page 33

	Pour "0-ary slice not allowed" 
	
*/

# Le nombre de noeuds (à définir)
param n, integer, >= 3;
# Le nombre de camions (à définir)
param r, integer, >= 1;
# La quantité transportable par un camion (à définir)
param Q, integer, >= 1;

# Une constante arbitraire grande pour la contrainte
# temps_voyage_entre_noeuds (à définir)
param M, integer, >=0;

# L'ensemble des noeuds sans le dépôt
set Vprim := 1..n;

# Un ensemble "pour rentrer les données" (à définir)
set DemandesNoeuds, within Vprim;

# L'ensemble des noeuds "dépot" (c'est un seul noeud en fait)
set Depart, := {0};
set Arrivee, := {n+1};
set Depot, := Depart union Arrivee;
set Interdit, := {(0,n+1), (n+1,0)};

# L'ensemble des noeuds (= clients)
set V := Vprim union Depot;

# L'ensemble des camions
set R := 1..r;

# L'ensemble des arcs (= chemins possibles) (à définir)
set E, within {i in V diff Arrivee, j in V diff Depart:i<>j};
# NOTE: `{i in V, j in V}` équivaut à `V cross V`
# NOTE: `{i in V, j in V}` équivaut à `{(i,j):i in V, j in V}`

# La durée de parcours d'un arc (donné)
# L'unité est arbitraire
param c{(i,j) in E};

# La quantité demandée par un client (donné)
# L'unité est arbitraire
param q{i in Vprim};

# Variable de décision entière donnant le tps
# d'arrivée du camion k au noeud i
# Contient la contrainte (7)
var t{k in R, i in V}, >= 0;

# Variable de décision binaire: si x(i,j,k) vrai, 
# alors le camion k passe par l'arc i,j
# Contient la contrainte (8)
var x{k in R, (i,j) in E : i<>j}, binary;
# NOTE: `i<>j` retire tous les (0,0)...
# NOTE: `(i,j) not in Interdit` retire (0,n+1) et (n+1,0)

# Pour comprendre les contraintes :<
# "An adaptive large neighborhood search heuristic for the CCVRP"

# Fonction objectif (minimisation) (contrainte (1))
minimize temps_arriv_chez_client:
	sum{k in R, i in Vprim} t[k,i];

# Contraintes (2)
s.t. conservation_flot{j in Vprim, k in R}:
	sum{i in V diff Arrivee: i<>j} x[k,i,j]
	= sum{l in V diff Depart: l<>j} x[k,j,l];

# Contraintes (3)
s.t. une_route_part_de_chaque_noeud{i in Vprim}:
	sum{k in R, j in V diff Depart: i<>j} x[k,i,j] = 1;


# Contraintes (4)
s.t. capacite_max_vehicule{k in R}:
	sum{i in Vprim, j in V diff Depart: i<>j} q[i]*x[k,i,j] <= Q;

# Contraintes (5)
s.t. route_commence_depot{k in R}:
	sum{i in Depart, j in V : i<>j} x[k,i,j] = 1;
	
# Contraintes (6)
s.t. route_termine_depot{k in R}:
	sum{i in V, j in Arrivee : i<>j} x[k,i,j] = 1;


# Contraintes (7)
# NOTE: pour cette contrainte, j'ai pris celle de l'article
# "Effective memetic algorithm for CCVRP"
s.t. temps_voyage_entre_noeuds{j in V diff Depart, k in R, i in (V diff Arrivee): i<>j}:
	t[k,i] + c[i,j] - (1-x[k,i,j])*M <= t[k,j];

# Contraintes (8) et (9) sont représentées par
# les "param t" et "param q" définis plus haut

solve;
#display conservation_flot;
#display une_route_part_de_chaque_noeud;
#display capacite_max_vehicule;
#display route_commence_depot;
#display route_termine_depot;
display temps_voyage_entre_noeuds;

printf "La somme des temps d'arrivée de %d\n", 
	sum{k in R, i in Vprim} t[k,i];
printf "%d camions parmi %d ont été pris \n", 
	sum{k in R} max{(i,j) in E: i<>j} x[k,i,j],
	r;

# NOTE pour le ":x[k,i,j]"
# Ici, cela représente un booléen <=> x[k,i,j]>0
printf 	"Camion  Sommet1   Sommet2   Duree\n";
printf{k in R, (i,j) in E: x[k,i,j]>0}
		"   %3d      %3d       %3d     %8g\n",
		k, i, j, c[i,j];



data;

# Nombre de camions disponibles
param r := 5;

param n := 4; # Le dépôt n'est pas compté dans n
# Le dépôt est situé en 0 et en n+1

param M := 1000;
param Q := 50;

# Les noeuds 0 et n+1 sont factices (dépot)

# Définition des 'edges' définis par les 4 noeuds
# ne sont pas comptés dans les noeuds "normaux"
# c = le cout de voyage de cet edge
param : E : c :=
0 1 1.414214
0 2 8.062258
0 3 10.816654
0 4 5.099020
0 5 0.000000
1 2 6.708204
1 3 9.433981
1 4 4.472136
1 5 1.414214
2 1 6.708204
2 3 5.099020
2 4 8.062258
2 5 8.062258
3 1 9.433981
3 2 5.099020
3 4 8.062258
3 5 10.816654
4 1 4.472136
4 2 8.062258
4 3 8.062258
4 5 5.099020


;
# Définition des demandes de chaque noeud
# q = quantité demandée par le noeud
param : DemandesNoeuds : q :=
1 10.000000
2 20.000000
3 30.000000
4 10.000000
;
end;

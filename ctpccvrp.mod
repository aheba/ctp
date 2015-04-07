######### Sets ###########

# Nombre de véhicules disponibles
param l, >= 1;
# Nombre de sommets à couvrir
param n, integer;
# Nombre de sommets atteignables
param m, integer;
# Ensemble des sommets qui doit etre visité ( à Ajouté)
#set T;
# Ensemble des sommets à couvrir
set I;
# Ensemble des sommets atteignables
set J;

set Depot, := {0};

set V, := Depot union I union J;
# Ensemble des arcs entre les sommets atteignables (J)
set E, within {i in V, j in V: i<>j} /*union {i in V diff Depot,0}*/;

# Ensemble des véhicules disponibles
set L, := 1..l;

########### Constantes ##########
# Distance entre deux sommets atteignables (J)
param c{i in V,j in V}, >= 0;

# Distance entre un sommet à couvrir i de I et
# un sommet atteignable j de J
#param dist{i in I, j in J}, >= 0;

# Rayon de couverture d'un sommet de V
param cmax, >= 0;

# Capacité de chaque véhicule
param Q, integer;

# Variable binaire vraie si j couvre le sommet i
param delta{i in I, j in J}, := if c[i,j] <= cmax then 1 else 0;
# Quantité demandée pour chaque client i
param d{i in I}, >= 0;

####### Variables de décision #######
var D{i in I, j in J, k in L},>=0;
var x{i in J union Depot, j in J union Depot, k in L}, binary;
var y{j in J union Depot, k in L}, binary;
var u{i in J union Depot, k in L}, >= 0;

######## Fonction objectif #########
minimize somme_couts_deplacement:
	sum{j in J, k in L: j not in Depot} u[j,k];
############ Contraintes ##############

# Contrainte(2) et (3)
# Si un véhicule k utilise le sommet j, il doit vérifier la loi de 1-kirchoff
# et doit etre le seul à utiliser ce sommet ( REMARQUE: PAS SUR Qu'il l'utilise SEULE)
s.t. sommet_atteignable_a_un_arc_entrant{j in J, k in L}:
	sum{i in J union Depot} x[i,j,k] = y[j,k];
s.t. sommet_atteignable_a_un_arc_sortant{j in J, k in L}:
	sum{i in J union Depot} x[j,i,k] = y[j,k];
#s.t. DepotC1{k in L}:
#		sum{i in J union Depot} (x[i,0,k] + x[0,i,k]) =y[0,k];
#tous les Ydepot=1
#s.t. DepotC{k in L}:
#		y[0,k]=1;
#s.t. DepotC2{k in L}:
#		sum{i in J} x[0,i,k] =y[0,k];
# Contrainte (4) et (5)
# Chaque tournée commence du dépôt
s.t. tournee_commence_depot{k in L}:
	sum{j in J union Depot} x[0,j,k] = 1;
# Chaque tournée termine par le dépôt
s.t. tournee_termine_depot{k in L}:
	sum{j in J union Depot} x[j,0,k] = 1;

# Contrainte (6)
# Cette contrainte vérifie le fait qu'une demande de quantité d'un 
# noeud couvert par plusieurs sommets J (sommets qu'on peut visiter)
# peuvent partager l'approvisionnement de la quantité demandée
s.t. demande_satisfaite{i in I}:
	sum{j in J, k in L} delta[i,j] * D[i,j,k] >= d[i];

# Contrainte (7)
s.t. distribution_sommet_atteignable{k in L, j in J}:
	sum{i in I} D[i,j,k] <= Q * y[j,k];

# Contrainte (8)
s.t. capacite_vehicule{k in L}:
	sum{i in I, j in J} D[i,j,k]<= Q;

#s.t. un_camion_par_noeud_atteignable{j in J}:
#	sum{k in L} y[j,k] <= 1;

# Contrainte (9)
s.t. sub_tour{i in J union Depot, j in J union Depot, k in L}:
#	u[i,k] - u[j,k] + (1000+1)*x[i,j,k] <= 1000;
	u[i,k] + c[i,j] - (1-x[i,j,k])*1000 <= u[j,k];
# On doit empêcher i = dépot arrivée && j 
#	u[i,k] - (1-x[i,j,k])*m<=u[j,k];
#s.t. temps_voyage_entre_noeuds{j in V diff Depart, k in R, i in (V diff Arrivee): i<>j}:
#	t[k,i] + c[i,j] - (1-x[k,i,j])*M <= t[k,j];	
solve;
display sub_tour;

#printf{i in I,j in J} "%d %d les delta %d\n",i,j,delta[i,j];
#printf{i in V,j in V : i<>j} "%d %d la distance %d\n",i,j,c[i,j];
#printf{(i,j) in E} "%d %d, l'arcs\n",i,j; 
printf "# La somme des distances/coûts des tournées est de %d\n", 
	#sum{i in J, k in L,j in J: i<>j} c[i,j]*y[i,k]*x[i,j,k];
	sum{i in J, k in L,j in J} u[i,k];
#printf "%d camions parmi %d ont été pris \n", 
#	sum{k in L} max{i in J,j in J} x[i,j,k],l;

printf 	"# Camion  SommetA   SommetB   Distance\n";
printf{k in L, i in J union Depot,j in J union Depot: x[i,j,k]>0 and i<>j}
		"    %3d      %3d       %3d     %6g\n",
		k, i, j, c[i,j];



data;

param n:=4;
param m:=4;

param cmax:=1;

param Q:=50;

param l:=5;


param d:=
6 10.0
7 20.0
8 30.0
9 10.0
;

set I:=
6
7
8
9
;

set J:=
1
2
3
4
;

param : E : c :=
0 1 1.414214
0 2 8.062258
0 3 10.816654
0 4 5.099020
0 0 0.0
1 2 6.708204
1 3 9.433981
1 4 4.472136
1 6 1.0
6 1 1.0
1 1 0.0

2 1 6.708204
2 3 5.099020
2 4 8.062258
2 7 1.0
7 2 1.0
2 2 0.0

3 1 9.433981
3 2 5.099020
3 4 8.062258
3 8 1.0
8 3 1.0
3 3 0.0

4 1 4.472136
4 2 8.062258
4 3 8.062258
4 9 1.0
9 4 1.0
4 4 0.0

1 0 1.414214
2 0 8.062258
3 0 10.816654
4 0 5.099020


0 6 8.0
6 0 8.0
0 7 8.0
7 0 8.0
0 8 8.0
8 0 8.0
0 9 8.0
9 0 8.0

6 2 8.0
6 3 8.0
6 4 8.0
2 6 8.0
3 6 8.0
4 6 8.0

7 1 8.0
7 3 8.0
7 4 8.0
1 7 8.0
3 7 8.0
4 7 8.0

8 2 8.0
8 1 8.0
8 4 8.0
2 8 8.0
1 8 8.0
4 8 8.0

9 2 8.0
9 1 8.0
9 3 8.0
2 9 8.0
1 9 8.0
3 9 8.0
;


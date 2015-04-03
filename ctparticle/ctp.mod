######### Sets ###########

# Nombre de véhicules disponibles
param l, >= 1;
# Nombre de sommets à couvrir
param n, integer;
# Nombre de sommets atteignables
param m, integer;

# Ensemble des sommets à couvrir
set I, := 1..n;
# Ensemble des sommets atteignables
set J, := 1..m;

set Depot, := {0};

# Ensemble des arcs entre les sommets atteignables (J)
set E, within {i in J union Depot, j in J union Depot: i<>j};

# Ensemble des véhicules disponibles
set L, := 1..l;

########### Constantes ##########
# Distance entre un sommet i et un sommet j
param c{(i,j) in E}, >= 0;

# Rayon de couverture d'un sommet de V
param cmax, integer;

# Capacité de chaque véhicule
param Q, integer;

# Variable binaire vraie si j couvre le sommet i
param delta{i in I, j in J}, := if c[i,j] <= cmax then 1 else 0;

# Quantité demandée pour chaque client i
param d{i in I}, >= 0;

####### Variables de décision #######
var D{i in I, j in J, k in L},>=0;
var x{i in J, j in J, k in L: i<>j /*&& i<j*/}, binary;
var y{j in J, k in L}, binary;
var u{i in I, k in L}, >= 0;

######## Fonction objectif #########
minimize somme_couts_deplacement:
	sum{i in I, j in J, k in L: i<>j} c[i,j] * x[i,j,k];

############ Contraintes ##############

# Contrainte(2) et (3)
# Si un véhicule k utilise le sommet j, il doit vérifier la loi de 1-kirchoff et doit etre le seul à utiliser ce sommet
s.t. sommet_atteignable_a_un_arc_entrant{j in J,k in L}:
	sum{i in J} x[i,j,k] = y[j,k];
s.t. sommet_atteignable_a_un_arc_sortant{j in J, k in L}:
	sum{i in J} x[j,i,k] = y[j,k];

# Contrainte (4) et (5)
# Chaque tournée commence du dépôt
s.t. tournee_commence_depot{k in L}:
	sum{j in J} x[0,j,k] = 1;
# Chaque tournée termine par le dépôt
s.t. tournee_termine_depot{k in L}:
	sum{j in J} x[j,0,k] = 1;

# Contrainte (6)
# Cette contrainte vérifie le fait qu'une demande de quantité d'un noeud couvert par plusieurs sommets J (sommets qu'on peut visiter) peuvent partager l'approvisionnement de la quantité demandée
s.t. demande_satisfaite{i in I}:
	sum{j in J,k in L} delta[i,j] * D[i,j,k] >= d[i];

# Contrainte (7)
s.t. distribution_sommet_atteignable{k in L,j in J}:
	sum{i in I} D[i,j,k] <= Q * y[j,k];

# Contrainte (8)
s.t. capacite_vehicule{k in L}:
	sum{i in I,j in J} D[i,j,k]<= Q;

# Contrainte (9)
s.t. sub_tour{i in J, j in J, k in L}:
	u[i,k] - u[j,k] + (m + 1)*x[i,j,k] <= m;

solve;


data;

# Nombre de sommets atteignables (I)
param n := 3;
# Nombre de sommets à couvrir (J)
param m := 3;
# Nombre de véhicules (L)
param l := 3;

# Capacité d'un véhicule
param cmax := 600;

param : d :=
1 10
2 10
3 10
;


param : E : c :=
0 1 5.0
0 2 5.0
0 3 5.0
1 0 5.0
1 2 5.0
1 3 5.0
2 0 5.0
2 1 5.0
2 3 5.0
3 0 5.0
3 1 5.0
3 2 5.0
;

end;

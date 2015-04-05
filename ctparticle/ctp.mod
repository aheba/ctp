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
param c{i in V,j in V: i<>j}, >= 0;

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
var u{i in J, k in L}, >= 0;

######## Fonction objectif #########
minimize somme_couts_deplacement:
	sum{i in J union Depot, j in J union Depot, k in L: i<>j} c[i,j] * x[i,j,k];

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

s.t. un_camion_par_noeud_atteignable{j in J}:
	sum{k in L} y[j,k] <= 1;

# Contrainte (9)
s.t. sub_tour{i in J, j in J, k in L}:
	u[i,k] - u[j,k] + (m+1)*x[i,j,k] <= m;
solve;

#printf{i in I,j in J} "%d %d les delta %d\n",i,j,delta[i,j];
#printf{i in V,j in V : i<>j} "%d %d la distance %d\n",i,j,c[i,j];
#printf{(i,j) in E} "%d %d, l'arcs\n",i,j; 
#printf "La somme des distances/coûts des tournées est de %d\n", 
#	sum{i in J union Depot, j in J union Depot, k in L: i<>j} c[i,j] * x[i,j,k];
#printf "%d camions parmi %d ont été pris \n", 
#	sum{k in L} max{i in J,j in J: i<>j} x[i,j,k],l;

#printf 	"Camion  SommetA   SommetB   Distance\n";
printf{k in L, i in J union Depot,j in J union Depot: x[i,j,k]>0 and i<>j}
		"   %3d      %3d       %3d     %6g\n",
		k, i, j, c[i,j];

end;

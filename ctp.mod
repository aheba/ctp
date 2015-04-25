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

# Vérification de l'ordre des indices de I et de J, qui ne
# doivent pas se chevaucher
check max{i in I} i < min{j in J} j;
check 0 not in I;

# L'ensemble des noeuds "dépot" : 0 et max(J)+1
# Le dépôt est dupliqué pour bien séparer le départ
# de l'arrivée et aider à l'écriture de la contrainte
# de sub-tour
set Depart, := {0};
set Arrivee, := {max{j in J} j + 1};
set Depot, := Depart union Arrivee;

# Ensemble global des sommets
set V, := Depot union I union J;
# Ensemble des arcs entre les sommets atteignables (J)
set E, within {i in V, j in V: i<>j} /*union {i in V diff Depot,0}*/;

# Ensemble des véhicules disponibles
set L, := 1..l;

########### Constantes ##########
# Distance entre deux sommets atteignables (J)
param c{i in V,j in V: i<>j}, >= 0;

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
var x{i in J union Depot, j in J union Depot, k in L: i<>j}, binary;
var y{j in J union Depot, k in L}, binary;
var u{j in J union Depot, k in L}, >= 0;

######## Fonction objectif #########
minimize somme_temps_arrivee:
	sum{i in J union Depart, j in J union Arrivee, k in L: i<>j} c[i,j] * x[i,j,k];

############ Contraintes ##############

# Contrainte(2) et (3)
# Si un véhicule k utilise le sommet j, il doit vérifier la loi de 1-kirchoff
# et doit etre le seul à utiliser ce sommet ( REMARQUE: PAS SUR Qu'il l'utilise SEULE)
s.t. sommet_atteignable_a_un_arc_entrant{j in J, k in L}:
	sum{i in J union Depart: i<>j} x[i,j,k] = y[j,k];
s.t. sommet_atteignable_a_un_arc_sortant{j in J, k in L}:
	sum{i in J union Arrivee: i<>j} x[j,i,k] = y[j,k];

# Contrainte (4) et (5)
# Chaque tournée commence du dépôt
s.t. tournee_commence_depot{k in L}:
	sum{i in Depart, j in J union Arrivee} x[i,j,k] = 1;
# Chaque tournée termine par le dépôt
s.t. tournee_termine_depot{k in L}:
	sum{i in J union Depart, j in Arrivee} x[i,j,k] = 1;

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

# Contrainte ajoutée
# Empêche la mutualisation de distribution depuis un noeud j
# c'est à dire que deux camions ne pourront pas livrer un i
# depuis le même noeud j (mais la multi-distribution est possible).
# NOTE: la multi-distribution marche toujours, c'est à dire
# qu'il est possible qu'un i soit livré depuis deux j différents
# et que ces deux j amène une partie de la quantité chacun
#s.t. un_camion_par_noeud_atteignable{j in J}:
#	sum{k in L} y[j,k] <= 1;

# Contrainte (9) pour l=2
s.t. sub_tour{i in J union Depart, j in J union Depot, k in L: i<>j}:
	u[i,k] + c[i,j] - (1-x[i,j,k])*10000 <= u[j,k];
#	u[i,k] + c[i,j]  - u[j,k] + (m+1)*x[i,j,k] <= 1000;
#pour l=4
#s.t. sub_tour{i in J union Arrivee, j in J union Depart, k in L: i<>j}:
#	u[i,k] + c[i,j] - (1-x[i,j,k])*10000 <= u[j,k];

# Contrainte pour empêcher les temps u[j,k] arbitrairement trop grands
s.t. garder_temps_valides{i in J union Depart, k in L}:
	u[i,k] <= 10000 * sum{j in J union Depot: i<>j} x[i,j,k];
	
solve;
display sub_tour;
display u;

printf 	"# Quantités livrées à i depuis le noeud j par un camion k\n";
printf 	"#    i    j  Camion  Qté  Arrivée \n";
printf{i in I, j in J, k in L: y[j,k] and D[i,j,k]>0} 	
		"#  %3d  %3d     %3d  %3d      %3d \n", 
	i,j,k,D[i,j,k],u[j,k];

printf 	"# Routes empruntées\n";
printf 	"# Camion  SommetA   SommetB\n";
printf{k in L, i in J union Depart,j in J union Arrivee: i<>j and x[i,j,k]>0}
		"     %3d      %3d      %3d\n",
		k, i, j;
printf "# La somme des distances/coûts des tournées est de %.2f\n", 
	sum{i in J union Depart, j in J union Arrivee, k in L: i<>j} c[i,j] * x[i,j,k];
printf "# La somme des temps d'arrivée chez les noeuds à couvrir est de %.2f\n",
	sum{j in J, k in L} u[j,k];
printf "# Au max, le client le plus loin attendra %.2f\n", 
	max{j in J, k in L} u[j,k];
printf "# %d camions parmi %d ont été pris \n",
	sum{k in L} max{i in J,j in J union Arrivee: i<>j} x[i,j,k], l;

end;

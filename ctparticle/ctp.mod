#########Sets###########

#param Sets
param nbl,>=1;
#nombre de sommets W couvert
param n,integer;
#nombre de sommets peuvant etre visité.
param m,integer;

#nombre de type d'aide
param t,integer;

#depot centrale
set Depot;
#c'est l'ensemble W des sommets couvert
set I: 1..n;
#c'est l'ensemble V des sommets qui peuvent etre visité.
set J: 1..m; 
# c'est l'ensemble contenant tous les sommets
set V,within Depot union I union J;
# c'est l'ensemble des combinaisons entre arcs
set Edge,within {i in V,j in V: i<>j /*&& i<j*/};

#Ensemble de voiture
set L:1..nbl;

#Ensemble de type d'aide fournis "Sucre,eau....", dans notre cas l'ensemble =1
#si on voudrai implemeter pour plusieurs type de d'aide, il faudra mettre un array de quantité pour chaque type d'aide pour les véhicules et ajouter une contraint pour qu'il ne dépasse pas la quantité du véhicule.
set TofA:1..t;
#########Constant#######
#Distance Matrix
param C{(i,j) in E},>=0;

#distance max de couverture
param cmax,integer;

#quantité véhicule
param Q,integer;

#covering distance validated
param delta{i in I,j in J}:= if c[i,j]<=cmax then 1 else 0;
#quantité demandé de l'ensemble I(ens W couvert) pour chaque type d'aide
param d{i in I,s in TofA}
########Variable########
var D{i in I,s in TofA,j in J,k in L},>=0;
var X{i in J,j in J,k in L: i<>j /*&& i<j*/},binary;
var Y{j in J,k in L},binary;

#######Contrainte########
###Contrainte(2et3)#######
#si un véhicule k utilise le sommet j, il doit vérifier la loi de 1-kirchoff et doit etre le seul à utiliser ce sommet.
s.t. UsingArc1{j in J,k in L} :
		sum{i in J} X[i,j,k] - Y[j,k]=1;
s.t. UsingArc2{j in J, k in L} :
		sum{i in J} X[j,i,k] - Y[j,k]=1;
###Contrainte(4et5)#######
s.t.
##pour chaque véhicule, on s'assure qu'il a un arc Départ du dépot
s.t. ConnectDepotD{k in L}:
	sum{j in J} X[0,j,k]=1;
##et un arc de Retour au depot
s.t. ConnectDepotR{k in L}:
	sum{j in J} X[j,0,k]=1;
###Contrainte(6)########
s.t. 
########Objectif#########
Minimise totale:
	sum{i in I, j in J, k in L} c[i,j]*x[i,j,k];

end;

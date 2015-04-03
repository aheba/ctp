#########Sets###########

#param Sets
param nbl,>=1;
#nombre de sommets W couvert
param n,integer;
#nombre de sommets peuvant etre visité.
param m,integer;

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
param d{i in I}, >= 0;
#à définir...
param W


####################Variable####################
var D{i in I,s in TofA,j in J,k in L},>=0;
var X{i in J,j in J,k in L: i<>j /*&& i<j*/},binary;
var Y{j in J,k in L},binary;
##a voir
var U{}, >= 0;

###################Contrainte############################
###Contrainte(2et3)#######
#si un véhicule k utilise le sommet j, il doit vérifier la loi de 1-kirchoff et doit etre le seul à utiliser ce sommet.
s.t. UsingArc1{j in J,k in L} :
		sum{i in J} X[i,j,k] = Y[j,k];
s.t. UsingArc2{j in J, k in L} :
		sum{i in J} X[j,i,k] = Y[j,k];
###Contrainte(4et5)#######
##pour chaque véhicule, on s'assure qu'il a un arc Départ du dépot
s.t. ConnectDepotD{k in L}:
	sum{j in J} X[0,j,k]=1;
##et un arc de Retour au depot
s.t. ConnectDepotR{k in L}:
	sum{j in J} X[j,0,k]=1;
###Contrainte(6)########
#Cette contraint vérifie le fait qu'une demande de quantité d'un noeud couvert par plusieur sommets J (sommet qu'on peut visiter) peuvent partager l'approvisionnement de la quantité demandée. 
s.t. DemandSatisfaction{i in I,s in TofA}:
	sum{j in J,k in L} delta[i,j]*D[i,j,k] >= d[i,s]
###Contrainte(7)#######
s.t. linkdelevery{k in L,j in J}:
	sum{i in I} W[s]*D[i,j,k] - Q*Y[j,k]<=0;
###Contrainte(8)#######
s.t. thresholdCap{k in L}:
	sum{i in I,j in J} W[s]*D[i,j,k]<= Q;
###Contrainte(9)#######
##A voir
s.t. sub-tour{i in J,j in J,k in L}:
	U[i,k]-U[j,k]+(m+1)*X[i,j,k]<=m;
########Objectif#########
Minimise totale:
	sum{i in I, j in J, k in L} c[i,j]*x[i,j,k];

end;

Logistique de crise et aide humanitaire
===========================

Lors du [TER](https://sites.google.com/site/term1info/) du M1 informatique de l'université Toulouse 3 - Paul Sabatier, nous avons effectué un état de l'art des méthodes utilisées en *recherche opérationnelle* pour optimiser le routage de véhicules.

Ce dépôt permet de mettre à disposition nos travaux sur les formulations en programmation linéaire des problèmes du *CTP* et du *CCVRP*.

# Le CTP-VRP
Le fichier `ctp.mod` contient le modèle en programmation linéaire du CTP modifié que nous avons utilisé comme référence. Nous l'avons appelé *CTP-VRP*, qui se différencie du CTP classique par les points suivants :

Différences entre le CTP et notre CTP-VRP :

- le CTP-VRP utilise un VRP à la place du TSP ; 
- le CTP-VRP utilise le *split-delivery*, c'est à dire qu'un point à couvrir peut être distribué par deux points atteignables différents

Ainsi :

- plusieurs véhicules peuvent être utilisés,
- seul le coût de livraison est minimisé.


# Le CTP-CCVRP
Le fichier `ctpccvrp.mod` contient le modèle LP du CTP une nouvelle fois modifié en remplaçant le VRP utilisé dans le modèle précédent par un CCVRP. Le VRP minimise le coût de livraison aux points atteignables ; le CCVRP, lui, minimise la somme des temps d'arrivée chez les points atteignables.

Ainsi :
- le coût de livraison n'est pas pris en compte ici, seul le temps de livraison compte

Exemple :
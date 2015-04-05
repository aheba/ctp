#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Mael Valais <mael.valais@univ-tlse3.fr>
#
# Distributed under terms of the MIT license.

#
# txt_vers_gmpl.py
#
# Permet de transcrire un fichier avec des noeuds et coordonnées
# en un fichier avec des (noeud1, noeud2, distance)
# EXEMPLE. Entrée: (je l'ai appelé "exemple.txt" dans le dossier sur le drive)
# 1      3      5
# 2      10      9
# 3      9      14
# etc...
# NOTE: seules les 4 premières données nous importent
# Ça transforme ça en:
# graph City
# {
# layout = neato;
# node [shape = circle];
# edge [dir=forward]
# rankdir = LR;
# 1 [pos="0.0,100.0!"];
# 2 [pos="100.0,200.0!"];
# 3 [pos="100.0,0.0!"];
# 4 [pos="200.0,100.0!"];
#
# 1 -- 2 [label="s2 - 3", color=red];
# 1 -- 3 [label="w - 7", color=blue];
# 1 -- 4 [label="w - 6", color=green];
# }


#
# Note avec exemple.txt:
# Les données sont de la forme
#   id x y quantity tmin tmax duration
# Avec quantity -> quantité demandée par le client
# tmin, tmax, duration -> pas besoin
#


import re # pour re.split()
import sys # pour args
import math # pour sqrt

# Pour parser une chaine de la forme suivante :
#       `id_point x_coord y_coord qty_demand...`
# Ex:   `1    8    9    90`
# NOTE: ne prend que les nombre_infos premiers éléments entiers
# NOTE: si aucun élément, renvoit None
def parser_ligne(ligne):
    element_string = [i for i in re.split("\\D", ligne) if i]
    # \D -> le délimiteur est "tout" sauf les entiers
    if len(element_string) >= 1:
        return [int(element) for element in element_string]
    else:
        return None

# Fonction de parsing du fichier de définition des noeuds au format CTP/CTP+CCVRP
#       - ligne 1: le dépôt (3 entiers)
#       forme:    `num_sommet   x   y`
#       exemple:  `0   4   5`
#       - ligne 2: ensemble des noeuds atteignables et non atteignables
#       forme: `num_sommet_début_atteignable`
#       exemple:  `5` pour 1->4 à couvrir, 5->fin atteignables
#       - lignes >2: la définition de tous les noeuds
#       forme:    `num_sommet  x   y  qté`
#       exemple:  `45  5   9   40`
def definir_noeuds_depuis_fichier_noeuds(nom_fichier):
    fichier = open(nom_fichier, 'r')
    numero_ligne = 1    
    ligne = fichier.readline()
    
    noeuds = []
    noeud_depot = []
    noeuds_atteignables = []
    noeuds_a_couvrir = []
    rayon_couverture = 0
    
    while ligne != "":
        ligne_entiers = parser_ligne(ligne)     
        if numero_ligne == 1 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print "Cette ligne définit le rayon de couverture des noeuds atteignables"
                print "Forme: `valeur_rayon`"
                sys.exit(1)
            rayon_couverture = ligne_entiers[0]
        elif numero_ligne == 2 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne   
                print "Cette ligne correspond au num_sommet du premier sommet 'non-atteignable'"
                print "Tous les num_sommet < ce numéro seront des sommets à couvrir,"
                print "tous les num_sommet >= ce numéro seront des sommets atteignables"
                print "Forme: `numero_sommet`"
                print "Exemple: `5` pour 1->4 à couvrir, 5->fin atteignables"
                sys.exit(1)
            debut_noeuds_atteignables = ligne_entiers[0]
        elif numero_ligne == 3 and ligne_entiers != None:
            if len(ligne_entiers) != 3:
                print "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print "Cette ligne définit la position du dépôt"
                print "Forme: `0   x   y`"
                sys.exit(1)
            noeud_depot = ligne_entiers
        elif numero_ligne > 3 and ligne_entiers != None:
            if len(ligne_entiers) > 0 and ligne_entiers[0] < debut_noeuds_atteignables:
                if len(ligne_entiers) != 4:
                    print "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print "Cette ligne correspond à une définition de noeud à couvrir (non atteignable)"
                    print "car vous avez défini debut_noeuds_atteignables=%d",debut_noeuds_atteignables
                    print "Forme: `num_sommet  x   y  qté`"
                    sys.exit(1)
                noeuds_a_couvrir += [ligne_entiers]
            else:
                if len(ligne_entiers) != 3:
                    print "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print "Cette ligne correspond à une définition de noeud atteignable (couvrants)"
                    print "car vous avez défini debut_noeuds_atteignables=%d",debut_noeuds_atteignables
                    print "Forme: `num_sommet  x   y`"
                    sys.exit(1)
                noeuds_atteignables += [ligne_entiers]
                
        numero_ligne += 1
        ligne = fichier.readline()        
    return [rayon_couverture, noeud_depot, noeuds_a_couvrir, noeuds_atteignables]

#   Depuis les résultats du ctp :
#       `id_route id1  id2 [...]`
def definir_chemins_depuis_resultat_glpsol(nom_fichier):
    fichier = open(nom_fichier, 'r')
    ligne = fichier.readline()
    numero_ligne = 1
    
    routes = [] # [num_camion, sommet1, sommet2]

    while ligne != "":
        ligne_entiers = parser_ligne(ligne)
        if ligne_entiers != None:
            if len(ligne_entiers) < 3:
                print "definir_chemins_depuis_resultat_glpsol(): erreur ligne %d" % numero_ligne
                sys.exit(1)
            routes = routes + [ligne_entiers[:3]]
            numero_ligne += 1
            ligne = fichier.readline()
    return routes

# Vérification des paramètres
if len(sys.argv) != 3:
    print("Usage: %s nom_fichier_noeuds_format_ctp nom_fichier_resultat" % sys.argv[0])
    sys.exit(1)

[rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables] =  definir_noeuds_depuis_fichier_noeuds(sys.argv[1])
routes =  definir_chemins_depuis_resultat_glpsol(sys.argv[2])

print(
"graph RoutesCTP \n"\
"{ \n"\
"\t layout=neato; \n"\
"\t node [shape=point]; \n"\
"\t edge [dir=none splines=line] \n"\
"\t rankdir = LR;")
    

scaling = 50 # Pour que les sommets soient suffisemment écartés dans graphviz
sommets_vus = []
noeuds_atteignables_et_depot = [noeud_depot] + noeuds_atteignables
couleurs_aretes = ['red','blue','black','brown','darkorchid','forestgreen','cyan4','orange','cadetblue']

# Traitement du sommet dépôt
print("\t%d [xlabel=\"D\" shape=point pos=\"%f,%f!\"]; " % (noeud_depot[0],noeud_depot[1]*scaling,noeud_depot[2]*scaling))
sommets_vus = sommets_vus + [noeud_depot[0]]

# Traitement de chaque arc déterminé par le solveur
for chemin in routes:
    sommets = chemin[1:2+1]
    num_route = chemin[0]
    # Traitement des deux sommets
    for num_sommet in sommets:
        if num_sommet not in sommets_vus:
            [x,y] = next(n[1:2+1] for n in noeuds_atteignables_et_depot if n[0]==num_sommet)
            sommets_vus = sommets_vus + [num_sommet]
            print("\t%d [pos=\"%f,%f!\"]; " % (num_sommet,x*scaling,y*scaling))
    # Traitement de l'arête
    if sommets[0] != sommets[1] and sommets[1] != noeud_depot[0]:
        print("\t%d -- %d [color=%s]; " \
                % (sommets[0],sommets[1],couleurs_aretes[(num_route-1)%len(couleurs_aretes)]))


# Traitement des sommets à couvrir
for [num_sommet,x,y,qte] in noeuds_a_couvrir:
    print('\t%d [pos=\"%f,%f!\" color="blue"]; ' % (num_sommet,x*scaling,y*scaling))

    
print("}")



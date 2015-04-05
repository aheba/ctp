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

def float_or_int(value):
  try:
    int(value)
    return int(value)
  except ValueError:
    return float(value)

# Pour parser une chaine de la forme suivante :
#       `id_point x_coord y_coord qty_demand...`
# Ex:   `1    8    9    90`
# NOTE: ne prend que les nombre_infos premiers éléments entiers
# NOTE: si aucun élément, renvoit None
def parser_ligne(ligne):
    element_string = [i for i in re.findall("\d+[.\d+]*", ligne) if i]
    # \D -> le délimiteur est "tout" sauf les entiers
    if len(element_string) >= 1:
        return [float_or_int(element) for element in element_string]
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
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print >> sys.stderr, "Cette ligne définit le rayon de couverture des noeuds atteignables"
                print >> sys.stderr, "Forme: `valeur_rayon`"
                sys.exit(1)
            rayon_couverture = ligne_entiers[0]
        elif numero_ligne == 2 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne   
                print >> sys.stderr, "Cette ligne correspond au num_sommet du premier sommet 'non-atteignable'"
                print >> sys.stderr, "Tous les num_sommet < ce numéro seront des sommets à couvrir,"
                print >> sys.stderr, "tous les num_sommet >= ce numéro seront des sommets atteignables"
                print >> sys.stderr, "Forme: `numero_sommet`"
                print >> sys.stderr, "Exemple: `5` pour 1->4 à couvrir, 5->fin atteignables"
                sys.exit(1)
            debut_noeuds_atteignables = ligne_entiers[0]
        elif numero_ligne == 3 and ligne_entiers != None:
            if len(ligne_entiers) != 3:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print >> sys.stderr, "Cette ligne définit la position du dépôt"
                print >> sys.stderr, "Forme: `0   x   y`"
                sys.exit(1)
            noeud_depot = ligne_entiers
        elif numero_ligne > 3 and ligne_entiers != None:
            if len(ligne_entiers) > 0 and ligne_entiers[0] < debut_noeuds_atteignables:
                if len(ligne_entiers) != 4:
                    print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print >> sys.stderr, "Cette ligne correspond à une définition de noeud à couvrir (non atteignable)"
                    print >> sys.stderr, "car vous avez défini debut_noeuds_atteignables=%d",debut_noeuds_atteignables
                    print >> sys.stderr, "Forme: `num_sommet  x   y  qté`"
                    sys.exit(1)
                noeuds_a_couvrir += [ligne_entiers]
            else:
                if len(ligne_entiers) != 3:
                    print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print >> sys.stderr, "Cette ligne correspond à une définition de noeud atteignable (couvrants)"
                    print >> sys.stderr, "car vous avez défini debut_noeuds_atteignables=%d",debut_noeuds_atteignables
                    print >> sys.stderr, "Forme: `num_sommet  x   y`"
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
                print >> sys.stderr, "definir_chemins_depuis_resultat_glpsol(): erreur ligne %d" % numero_ligne
                sys.exit(1)
            routes = routes + [ligne_entiers[:3]]
            numero_ligne += 1
            ligne = fichier.readline()
    return routes
    
def tracer_dot(rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables,routes):
    print(
    "graph RoutesCTP \n"\
    "{ \n"\
    "\t layout=neato; \n"\
    "\t node [shape=point]; \n"\
    "\t edge [dir=none splines=line] \n"\
    "\t rankdir = LR;")

    scaling = 72 # Pour que les sommets soient suffisemment écartés dans graphviz
    # 72 correspond au nombre de points (x,y...) pour un 'inch'. En effet, `pos=`
    # est en unité de points alors que `width=` a pour unité l'inch.
    sommets_vus = []
    noeuds_atteignables_et_depot = [noeud_depot] + noeuds_atteignables
    couleurs_aretes = ['red','blue','black','darkorchid','forestgreen','cyan4','orange','cadetblue']

    # Traitement du sommet dépôt
    print('\t%d [xlabel=\"D\" shape=point pos=\"%f,%f!\"]; ' % (noeud_depot[0],noeud_depot[1]*scaling,noeud_depot[2]*scaling))
    sommets_vus = sommets_vus + [noeud_depot[0]]

    # Traitement de chaque arc déterminé par le solveur
    for chemin in routes:
        sommets = chemin[1:2+1]
        num_route = chemin[0]
        # Traitement de l'arête
        if sommets[0] != sommets[1] and sommets[1] != noeud_depot[0]:
            print('\t%d -- %d [color=%s]; ' \
                    % (sommets[0],sommets[1],couleurs_aretes[(num_route-1)%len(couleurs_aretes)]))
    # Traitement des sommets atteignables
    for [sommet,x,y] in noeuds_atteignables:
        print('\t%d [pos="%f,%f!"]; ' % (sommet,x*scaling,y*scaling))
        print('\trayon_%d [pos="%f,%f!" shape=circle fixedsize=true width=%d label=""]; '\
                        % (sommet,x*scaling,y*scaling,rayon*2))               

            
        
    # Traitement des sommets à couvrir
    for [num_sommet,x,y,qte] in noeuds_a_couvrir:
        print('\t%d [pos="%f,%f!" color="blue"]; ' % (num_sommet,x*scaling,y*scaling))
    print("}")

# Ajoutons artificiellement un n+1ième point qui sera
# une copie de ce qui a été fait avec 0, le dépôt.
# C'est pour que le paramètre de durée, c[k,i,j] (dans le CCVRP)
# ait toutes les valeurs de i et j entre 0 et n+1
def produire_data_solveur(rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables):
    print "data;"

    print "# Nombre de sommets à couvrir (I)"
    print "param n := %d;"% len(noeuds_a_couvrir)
    print "# Nombre de sommets atteignables (J)"
    print "param m := %d;"% len(noeuds_atteignables)
    print "# Nombre de véhicules (L)"
    print "param l := 10;" # XXX

    print "# Capacité d\'un véhicule"
    print "param Q := 20;" # XXX

    print "set I :="
    for [num,x,y,_] in noeuds_a_couvrir:
        print "%d" % num
    print ";"
    
    print "set J :="
    for [num,x,y] in noeuds_atteignables:
        print "%d" % num
    print ";"

    print "# Rayon de couverture d\'un point atteignable (J)"
    print "param cmax := %.2f;" % rayon

    print "param : d :="
    for [num,x,y,qte] in noeuds_a_couvrir:
        print("%d %d" % (num,qte))
    print(";")

    print("param : E : c := ")
    for p1 in  noeuds_a_couvrir + noeuds_atteignables + [noeud_depot]:
        for p2 in  noeuds_a_couvrir + noeuds_atteignables + [noeud_depot]:
            if p1 != p2:
                dist = math.sqrt(pow(p1[1]-p2[1],2)+pow(p1[2]-p2[2],2))
                print("%d %d %.2f" % (p1[0],p2[0],dist))
    print(";")

    print 'end;'



import argparse

    
parser = argparse.ArgumentParser(description='Parser pour .dat et .dot')

parser.add_argument('--dot', nargs=2, \
        required=False,\
        help='Commande permettant de produire un .dot',\
        metavar=('fichier_noeuds', 'fichier_resultat_solveur')\
        )
parser.add_argument('--dat', nargs=1, \
        required=False,\
        help='Commande permettant de produire un .dat',\
        metavar='fichier_noeuds'\
        )

args = parser.parse_args()

if args.dot != None:
    [rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables] =  definir_noeuds_depuis_fichier_noeuds(args.dot[0])
    routes =  definir_chemins_depuis_resultat_glpsol(args.dot[1])
    tracer_dot(rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables,routes)
    
if args.dat != None:
    [rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables] =  definir_noeuds_depuis_fichier_noeuds(args.dat[0])
    produire_data_solveur(rayon,noeud_depot,noeuds_a_couvrir,noeuds_atteignables)


#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Mael Valais <mael.valais@univ-tlse3.fr>
#
# Distributed under terms of the MIT license.


#
# Pour lancer glpsol et générer en même temps le .dot :
#
# python parseur_noeuds.py --dat noeuds.txt > data.dat && \
# glpsol -m ctp.mod -d data.dat -y resultats_solveur.txt && \
# python parseur_noeuds.py --numeros --dot noeuds.txt resultats_solveur.txt > graphe.dot
# 
# 
#
# Ensuite, ouvrir le .dot avec graphviz
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
#       Format:    `num_sommet   x   y`
#       exemple:  `0   4   5`
#       - ligne 2: ensemble des noeuds atteignables et non atteignables
#       Format: `num_sommet_début_atteignable`
#       exemple:  `5` pour 1->4 à couvrir, 5->fin atteignables
#       - lignes >2: la définition de tous les noeuds
#       Format:    `num_sommet  x   y  qté`
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
    nb_vehicules = 0
    capacite = 0

    
    while ligne != "":
        ligne_entiers = parser_ligne(ligne)     

        if numero_ligne == 1 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print >> sys.stderr, "Cette ligne définit la capacité des camions"
                print >> sys.stderr, "Format: `capacité`"
                sys.exit(1)
            capacite = ligne_entiers[0]
        elif numero_ligne == 2 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne   
                print >> sys.stderr, "Cette ligne correspond au nombre de véhicules/camions"
                print >> sys.stderr, "Format: `nombre_vehicules`"
                sys.exit(1)
            nb_vehicules = ligne_entiers[0]
        elif numero_ligne == 3 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print >> sys.stderr, "Cette ligne définit le rayon de couverture des noeuds atteignables"
                print >> sys.stderr, "Format: `valeur_rayon`"
                sys.exit(1)
            rayon_couverture = ligne_entiers[0]
        elif numero_ligne == 4 and ligne_entiers != None:
            if len(ligne_entiers) != 1:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne   
                print >> sys.stderr, "Cette ligne correspond au num_sommet du premier sommet 'non-atteignable'"
                print >> sys.stderr, "Tous les num_sommet < ce numéro seront des sommets à couvrir,"
                print >> sys.stderr, "tous les num_sommet >= ce numéro seront des sommets atteignables"
                print >> sys.stderr, "Format: `numero_sommet`"
                print >> sys.stderr, "Exemple: `5` pour 1->4 à couvrir, 5->fin atteignables"
                sys.exit(1)
            debut_noeuds_atteignables = ligne_entiers[0]
        elif numero_ligne == 5 and ligne_entiers != None:
            if len(ligne_entiers) != 3:
                print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne
                print >> sys.stderr, "Cette ligne définit la position du dépôt"
                print >> sys.stderr, "Format: `0   x   y`"
                sys.exit(1)
            noeud_depot = ligne_entiers
        elif numero_ligne > 5 and ligne_entiers != None:
            if len(ligne_entiers) > 0 and ligne_entiers[0] < debut_noeuds_atteignables:
                if len(ligne_entiers) != 4:
                    print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print >> sys.stderr, "Cette ligne correspond à une définition de noeud à couvrir (non atteignable)"
                    print >> sys.stderr, "car vous avez défini debut_noeuds_atteignables=%d"%debut_noeuds_atteignables
                    print >> sys.stderr, "Format: `num_sommet  x   y  qté`"
                    sys.exit(1)
                noeuds_a_couvrir += [ligne_entiers]
            else:
                if len(ligne_entiers) != 3:
                    print >> sys.stderr, "definir_noeuds_depuis_fichier_noeuds(): erreur ligne %d" % numero_ligne           
                    print >> sys.stderr, "Cette ligne correspond à une définition de noeud atteignable (couvrants)"
                    print >> sys.stderr, "car vous avez défini debut_noeuds_atteignables=%d"%debut_noeuds_atteignables
                    print >> sys.stderr, "Format: `num_sommet  x   y`"
                    sys.exit(1)
                noeuds_atteignables += [ligne_entiers]
                
        numero_ligne += 1
        ligne = fichier.readline()        
    return [rayon_couverture, nb_vehicules, capacite, noeud_depot, noeuds_a_couvrir, noeuds_atteignables]

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
    
def tracer_dot(rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,noeuds_atteignables,routes,\
        avec_numeros,avec_demande):
    print(
    'graph RoutesCTP \n'\
    '{ \n'\
    '\t layout=neato; \n'\
    '\t node [shape=point label=""]; \n'\
    '\t edge [dir=none splines=line] \n'\
    '\t rankdir = LR;')

    scaling = 72 # Pour que les sommets soient suffisemment écartés dans graphviz
    # 72 correspond au nombre de points (x,y...) pour un 'inch'. En effet, `pos=`
    # est en unité de points alors que `width=` a pour unité l'inch.
    sommets_vus = []
    noeuds_atteignables_et_depot = [noeud_depot] + noeuds_atteignables
    couleurs_aretes = ['red','darkorchid','forestgreen','cyan4','orange','cadetblue']

    # Traitement du sommet dépôt
    print('\t%d [label="" xlabel="Dépôt" shape=square fixedsize=true\
            style=filled width=0.1 color=black pos="%f,%f!"]; ' \
            % (noeud_depot[0],noeud_depot[1]*scaling,noeud_depot[2]*scaling))
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
        print('\t%d [xlabel="%s" pos="%f,%f!" label="" shape=point]; ' \
                % (sommet,str(sommet) if avec_numeros else "", x*scaling,y*scaling))
        print('\trayon_%d [pos="%f,%f!" shape=circle fixedsize=true width=%d label=""]; '\
                % (sommet,x*scaling,y*scaling,rayon*2))

    # Traitement des sommets à couvrir
    for [sommet,x,y,qte] in noeuds_a_couvrir:
        xlabel=""
        xlabel+=("<font color=\'blue\'>"+"("+str(qte)+")" +"</font>") if avec_demande else ""
        xlabel+=("<font color=\'black\'>"+str(sommet)+"</font>") if avec_numeros else ""
        print '\t%d [label="" xlabel=<%s> pos="%f,%f!" color="blue" style=filled shape=triangle fixedsize=true width=0.1 height=0.2]; ' \
               % (sommet, xlabel, x*scaling,y*scaling)
    print("}")

# Ajoutons artificiellement un n+1ième point qui sera
# une copie de ce qui a été fait avec 0, le dépôt.
# C'est pour que le paramètre de durée, c[k,i,j] (dans le CCVRP)
# ait toutes les valeurs de i et j entre 0 et n+1
def produire_data_solveur(rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,noeuds_atteignables):
    print "data;"

    print "# Nombre de sommets à couvrir (I)"
    print "param n := %d;"% len(noeuds_a_couvrir)
    print "# Nombre de sommets atteignables (J)"
    print "param m := %d;"% len(noeuds_atteignables)
    print "# Nombre de véhicules (L)"
    print "param l := %d;"% nb_vehicules

    print "# Capacité d\'un véhicule"
    print "param Q := %d;"% capacite

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
exclusive = parser.add_mutually_exclusive_group(required=True)
exclusive.add_argument('--dot', nargs=2, \
        required=False,\
        help='Commande permettant de produire un .dot',\
        metavar=('fichier_noeuds', 'fichier_resultat_solveur')\
        )
exclusive.add_argument('--dat', nargs=1, \
        required=False,\
        help='Commande permettant de produire un .dat',\
        metavar='fichier_noeuds'\
        )
parser.add_argument('--numeros',action='store_true',\
        help="Pour la commande --dot, afficher les numéros des noeuds")
parser.add_argument('--demandes',action='store_true',\
        help="Pour la commande --dot, afficher les demandes des noeuds à couvrir")

args = parser.parse_args()

if args.dot != None:
    [rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,noeuds_atteignables] =\
            definir_noeuds_depuis_fichier_noeuds(args.dot[0])
    routes =  definir_chemins_depuis_resultat_glpsol(args.dot[1])
    tracer_dot(rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,\
            noeuds_atteignables,routes,args.numeros,args.demandes)
    
if args.dat != None:
    [rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,noeuds_atteignables] = \
            definir_noeuds_depuis_fichier_noeuds(args.dat[0])
    produire_data_solveur(rayon,nb_vehicules,capacite,noeud_depot,noeuds_a_couvrir,\
            noeuds_atteignables)


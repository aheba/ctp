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
# 0      3      6 <- c'est le dépot
# 1      3      5
# 2      10      9
# 3      9      14
# etc...
# NOTE: seules les 4 premières données nous importent
# NOTE: Ici par exemple, on a n=3 (trois noeuds), le dépôt
# ne compte pas dans le nombre de noeuds

# Ça transforme ça en:
# 0 1 2.2OI32

# 1 2 8.062258
# 1 3 10.816654
# 1 4 5.099020
# 1 5 8.062258
# 1 6 11.000000
# 1 7 7.211103
# 1 8 2.000000
# 1 9 3.605551
# etc...
#
# Pour l'utiliser :
#   python txt_vers_gmpl.py exemple.txt
#

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

# Pour parser une chaine de la forme:
#   `id_point x_coord y_coord qty_demand azdazd azdazda...`
# Note: ne prend que les 4 premiers éléments
# Note: si moins de 4 élements, renvoit None
def recuperer_informations_ligne(ligne):
    res = [i for i in re.split("\\s", ligne) if i]
    if len(res) >= 3:
        return [res[0],int(res[1]),int(res[2]),int(res[3])]
    else:
        return None

# Vérification des paramètres
if len(sys.argv) != 2:
    print("Usage: %s nom_fichier_txt")
    sys.exit(1)

# On ouvre le fichier
nom_fichier = sys.argv[1]
fichier = open(nom_fichier, 'r')
points = []
ligne = fichier.readline()
while ligne != "":
    # On parse cette ligne
    parsed = recuperer_informations_ligne(ligne)
    # Si le parsing a bien marché, on concatène
    if parsed != None:
        points.append(recuperer_informations_ligne(ligne))
    ligne = fichier.readline()

# Ajoutons artificiellement un n+1ième point qui sera
# une copie de ce qui a été fait avec 0, le dépôt.
# C'est pour que le paramètre de durée, c[k,i,j] (dans le CCVRP)
# ait toutes les valeurs de i et j entre 0 et n+1
depot_depart = points[0] # Attention, ça n'est pas une vraie copie
depot_arrivee = [len(points),depot_depart[1],depot_depart[2],0]
points_avec_arrivee = points + [depot_arrivee]
points_sans_depots = points[1:]

nb_pts_sans_depot = len(points_avec_arrivee) - 2
print("# Définition des 'edges' définis par les %d noeuds" % nb_pts_sans_depot)
print("# Les deux noeuds \"fictifs\" de dépot_arrivee/depart")
print("# ne sont pas comptés dans les noeuds \"normaux\"")
print("# c = le cout de voyage de cet edge")
print("param : E : c := ")
for p1 in points_avec_arrivee:
    for p2 in points_avec_arrivee:
        if p1 != p2:
            dist = math.sqrt(pow(p1[1]-p2[1],2)+pow(p1[2]-p2[2],2))
            print("%s %s %f" % (p1[0],p2[0],dist))
print(";")

print("# Définition des demandes de chaque noeud")
print("# q = quantité demandée par le noeud")
print("param : Vprim : q :=")
for p in points_sans_depots:
    print("%s %f" % (p[0],p[3]))
print(";")

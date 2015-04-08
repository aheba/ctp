#! /bin/sh
#
# lancer_ctp_et_ctpccvrp.sh
# Copyright (C) 2015 Mael Valais <mael.valais@univ-tlse3.fr>
#
# Distributed under terms of the MIT license.
#

if [ $# -ne 1 ]; then
	echo "Usage: $0 fichier_noeuds"
	exit 1
fi

if [ ! -f $1 ]; then
	echo "$1 n'est pas un fichier"
	exit 1
fi


python parseur_noeuds.py --dat $1 > data_ctp.dat \
	&& glpsol -m ctp.mod -d data_ctp.dat -y resultats_ctp.txt \
	&& python parseur_noeuds.py --numeros --demandes --dot $1 resultats_ctp.txt > graphe_ctp.dot;
res_ctp=$?
python parseur_noeuds.py --dat $1 > data_ctpccvrp.dat \
	&& glpsol -m ctpccvrp.mod -d data_ctpccvrp.dat -y resultats_ctpccvrp.txt \
	&& python parseur_noeuds.py --numeros --demandes --dot $1 resultats_ctpccvrp.txt > graphe_ctpccvrp.dot
res_ctpccvrp=$?

echo "----------------------"
echo "Résultats du CTP-VRP :"
cat resultats_ctp.txt
echo "Résultats du CTP-CCVRP :"
cat resultats_ctpccvrp.txt
echo "----------------------"
echo "Résultats du CTP-VRP :"
if [ $res_ctp -eq 0 ]; then
	cat resultats_ctp.txt | head -3
else
	echo "PAS DE SOLUTION"	
fi	
echo "Résultats du CTP-CCVRP :"
if [ $res_ctpccvrp -eq 0 ]; then
	cat resultats_ctpccvrp.txt | head -3
else
	echo "PAS DE SOLUTION"	
fi	


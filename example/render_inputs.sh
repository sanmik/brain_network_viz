#!/bin/bash
echo "Rendering: nodes_1.csv + edges_1.csv"
python ../souce/main.py -n inputs/sample/nodes_1.csv -e inputs/sample/edges_1.csv -o outputs/fig_1.pdf
echo "Opening: fig_1.pdf"
open outputs/fig_1.pdf

echo "Rendering: nodes_2.csv + edges_2.csv"
python ../souce/main.py -n inputs/sample/nodes_2.csv -e inputs/sample/edges_2.csv -o outputs/fig_2.pdf
echo "Opening: fig_2.pdf"
open outputs/fig_2.pdf

# Many Nodes, 3 Labeled Layers
echo "Rendering: nodes_3.csv + edges_3.csv"
python ../souce/main.py -n inputs/sample/nodes_3.csv -e inputs/sample/edges_3.csv -o outputs/fig_3.pdf
echo "Opening: fig_3.pdf"
open outputs/fig_3.pdf

# Many Nodes, 1 Labeled Layer
echo "Rendering: nodes_4.csv + edges_4.csv"
python ../souce/main.py -n inputs/sample/nodes_4.csv -e inputs/sample/edges_4.csv -o outputs/fig_4.pdf
echo "Opening: fig_4.pdf"
open outputs/fig_4.pdf

# Many Nodes, 1 Unlabeled Layer 
echo "Rendering: nodes_5.csv + edges_5.csv"
python ../souce/main.py -n inputs/sample/nodes_5.csv -e inputs/sample/edges_5.csv -o outputs/fig_5.pdf
echo "Opening: fig_5.pdf"
open outputs/fig_5.pdf

# All properties left unspecified 
echo "Rendering: nodes_6.csv + edges_6.csv"
python ../souce/main.py -n inputs/sample/nodes_6.csv -e inputs/sample/edges_6.csv -o outputs/fig_6.pdf
echo "Opening: fig_6.pdf"
open outputs/fig_6.pdf

# Non-numeric colors 
echo "Rendering: nodes_7.csv + edges_7.csv"
python ../souce/main.py -n inputs/sample/nodes_7.csv -e inputs/sample/edges_7.csv -o outputs/fig_7.pdf
echo "Opening: fig_7.pdf"
open outputs/fig_7.pdf

# Rendering when lobe dimensions are given in a lobe file
python ../souce/main.py -n inputs/sample/nodes_with_lobefile.csv -e inputs/sample/edges_with_lobefile.csv -l inputs/sample/lobefile.csv -o outputs/fig_with_lobefile.pdf
echo "Opening: fig_with_lobefile.pdf"
open outputs/fig_with_lobefile.pdf

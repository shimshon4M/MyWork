#!/bin/bash

#find ./data/papers/NLP_LATEX_CORPUS/ -type f -name "*.xml" | while read -r file;
#find ./data/xml/ -type f -name "*terms.txt" | while read -r file;
find ./data/xml/ -type f -name "*_feature.json" | while read -r file;
do
    echo $file
    #python wordExtract/appendLabel2.py $file
    mv $file "./data/xml/features/"
    #cp $file "./data/papers/tmp_xmls/"
done
#find ./data/xml/BoW/ -type f -name "*feature_BoW.txt" | while read -r file;
#do
#   echo $file
#    python labelMerge.py $file
#done

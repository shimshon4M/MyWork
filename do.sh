#!/bin/bash

find ./data/xml/ -type f -name "*feature_W2VSum.txt" | while read -r file;
do
    echo $file
    mv $file "./data/xml/W2VSum/"
done
#find ./data/xml/BoW/ -type f -name "*feature_BoW.txt" | while read -r file;
#do
#   echo $file
#    python labelMerge.py $file
#done

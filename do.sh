#!/bin/bash

find ./data/papers/NLP_LATEX_CORPUS -type f -name "*feature_BoW.txt" | while read -r file;
do
    echo $file
    mv $file ./data/feature_data/BoW/
done

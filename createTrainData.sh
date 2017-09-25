#!/bin/bash

find ./data/papers/NLP_LATEX_CORPUS -type f -name "*.xml" | while read -r file;
do
    echo $file
    python createTrainData.py $file
done

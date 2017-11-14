#!/bin/bash

find ./data/papers/NLP_LATEX_CORPUS -type f -name "*.tex" | while read -r file;
do
    echo $file
    python texCompiler.py $file
done

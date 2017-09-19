#!/bin/bash

find ./data/papers/NLP-anual -type f -name "*.pdf" | while read -r file;
do
    echo $file
    python pdf2txt.py -o $file".txt" $file
done

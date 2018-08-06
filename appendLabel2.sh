#!/bin/bash

find ./data/xml/ -type f -name "*feature_W2VSum.txt" | while read -r file;
do
    echo $file
    python wordExtract/appendLabel2.py $file
done

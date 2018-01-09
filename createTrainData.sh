#!/bin/bash

find ./data/xml/ -type f -name "*.xml" | while read -r file;
do
    echo $file
    python createTrainData.py $file
done

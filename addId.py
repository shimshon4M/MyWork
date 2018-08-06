import sys
import re
from utils import get_files

files=get_files("./data/xml/labeled/")

for filename in files:
    print(filename)
    outlines=[]
    with open(filename,"r")as f:
        for i,line in enumerate(f.readlines()):
            spl=line.split("\t")
            spl.insert(1,str(i))
            outlines.append("\t".join(spl))
    with open(filename,"w")as f:
        f.write("".join(outlines))

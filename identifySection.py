import sys
import re
from utils import get_files
from xmlAnalyzer import removeTags
import xml.etree.ElementTree as ET

BG=0
MET=1
RES=2

files=get_files("./data/xml/")

for filename in files:
    print(filename,end="")
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #dict
    absts=re.split("[．。]",texts["abstract"])

    background=-1
    method=-1
    result=-1
    now=BG

    pos=0
    for sent in absts:
        if now==BG:
            if re.search("本稿で|本論文で|本研究で|提案",sent)!=None:
                method=pos
                now=MET
        if now==MET:
            if re.search("実験|結果|評価|精度が|精度に",sent)!=None:
                result=pos
                now=RES
                break
        pos+=len(sent)+len(".")

    if method>0:
        background=0

    if background==-1 and method==-1 and result==-1:
        method=0

    outfilename=filename.replace("xml","txt").replace("/txt/","/xml/sectionData/")
    print(" -> ",outfilename)
    with open(outfilename,"w")as f:
        f.write("background\t"+str(background)+"\n")
        f.write("method\t"+str(method)+"\n")
        f.write("result\t"+str(result)+"\n")

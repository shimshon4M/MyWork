import glob
import sys
import re
import pyknp
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags

def main():
    files=glob.glob("./data/papers/NLP_LATEX_CORPUS/*/*.xml",recursive=True)
    with open("./data/wakachi/done.txt","r")as donef:
        donefiles=donef.readlines()
    for i,file in enumerate(files):
        print(i+1,"/",len(files)," ",file)
        if file+"\n" in donefiles:
            print("exist")
            continue
        contents=parseContents(file)
        if contents==None:
            continue
        surfaces=getWakachi(contents)
        with open("./data/wakachi/NLP_L_C_wakachi_J.txt","a") as f:
            for surface in surfaces:
                if(len(surface)>2): #len(surface)==2が空行
                    f.write("__label__nlpcorpus,"+" ".join(surface)+"\n")
                    #f.write(" ".join(surface)+"\n")
        with open("./data/wakachi/done.txt","a")as donef:
            donef.write(file+"\n")

def isEngPaper(text):
    i=0
    for c in text:
        if re.match("[a-zA-Z0-9]",c):
            i+=1
    if i/len(text)>0.8:
        return True
    return False

def isJapPaper(text):
    for c in text:
        if re.match("[あ-ん]",c):
            return True
    return False
                    
def parseContents(file):
    tree=ET.parse(file)
    root=tree.getroot()
    contentsDict=removeTags(root)
    contentsDict.pop("author",None)
    contentsDict.pop("jauthor",None)
    contentsDict.pop("keywords",None)
    contentsDict.pop("jkeywords",None)
    for content in contentsDict.values():
        if content==None or content=="":
            continue
        if not isJapPaper(content):
            return None
    return contentsDict.values() #各セクションからなるlist 
    
def getWakachi(contents):
    juman=pyknp.Jumanpp()
    results=[]
    for i,content in enumerate(contents):
        if len(content)==0:
            continue
        if len(content)>5000:
            continue
        print(" ",i+1,"/",len(contents)," ",len(content))
        surf=[]
        for morph in juman.analysis(content):
            surf.append(morph.midasi)
        results.append(surf)
    return results
        
if __name__=="__main__":
    main()

import glob
import sys
import re
import pyknp
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags

def main():
    joshis=[]
    files=glob.glob("./data/papers/NLP_LATEX_CORPUS/*/*.xml",recursive=True)
    with open("./data/wakachi/done.txt","r")as donef:
        donefiles=donef.readlines()
    for i,file in enumerate(files):
        print(i+1,"/",len(files)," ",file)
        if file+"\n" not in donefiles:
            continue
        contents=parseContents(file)
        if contents==None:
            continue
        surfaces=getJoshi(contents)
        joshis.extend(surfaces)
        joshis=list(set(joshis))
        #print(len(joshis)," ",joshis)
    with open("./data/joshi.txt","w") as f:
        for joshi in list(set(joshis)):
            f.write(joshi+"\n")
        

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
    
def getJoshi(contents):
    juman=pyknp.Jumanpp()
    results=[]
    for i,content in enumerate(contents):
        if len(content)==0:
            continue
        if len(content)>5000:
            continue
        print(" ",i+1,"/",len(contents)," ",len(content))
        for morph in juman.analysis(content):
            if morph.hinsi=="助詞":
                results.append(morph.bunrui+"\t"+morph.genkei)
    return list(set(results))
        
if __name__=="__main__":
    main()

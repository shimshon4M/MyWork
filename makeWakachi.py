import MeCab
import glob
import sys
import re
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags

def main():
    files=glob.glob("./data/papers/NLP_LATEX_CORPUS/*/*.xml",recursive=True)
    for i,file in enumerate(files):
        print(i+1,"/",len(files))
        contents=parseContents(file)
        if contents==None:
            continue
        surfaces=getWakachi(contents)
        with open("./data/wakachi/NLP_L_C_wakachi_nolabel.txt","a") as f:
            for surface in surfaces:
                if(len(surface)>2): #len(surface)==2が空行
                    #f.write("__label__nlpcorpus,"+" ".join(surface)+"\n")
                    f.write(" ".join(surface)+"\n")

def isEngPaper(text):
    i=0
    for c in text:
        if re.match("[a-zA-Z0-9]",c):
            i+=1
    if i/len(text)>0.8:
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
        if isEngPaper(content):
            return None
    return contentsDict.values() #各セクションからなるlist 
    
def getWakachi(contents):
    results=[]
    for content in contents:
        #tagger=MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
        tagger=MeCab.Tagger("")
        tagger.parse("")
        surf=[]
        node=tagger.parseToNode(content)
        while node:
            surf.append(node.surface)
            node=node.next
        results.append(surf)
    return results
        
if __name__=="__main__":
    main()

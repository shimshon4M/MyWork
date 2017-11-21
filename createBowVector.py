from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
from createTrainData import mecab,join_body_text_all
import MeCab
import sys
import constants
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def paper2only_text(filename):
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root)
    joined_text=join_body_text_all(texts)
    with open("./data/joined_paper_text/"+filename[35:]+"_text.txt","w")as f:
        f.write(joined_text)

def load_all_paper_text():
    text_list=[]
    files=get_files("./data/joined_paper_text/")
    for filename in files:
        with open(filename,"r")as f:
            text_list.append(f.read())
    return text_list
            
def vectorizer_main():
    text_list=load_all_paper_text()
    vectorizer=TfidfVectorizer(token_pattern=u'(?u)\\b\\w+\\b',tokenizer=mecab_tokenizer,sublinear_tf=True)
    tfidf_weighted_matrix=vectorizer.fit_transform(text_list)
    print("テキスト数%d,単語種類数%d"%tfidf_weighted_matrix.shape)
    terms=vectorizer.get_feature_names()
    tfidfs=tfidf_weighted_matrix.toarray()[constants.DOC_NUM]
    with open("./data/bow/BOW_list.txt","w")as f:
        for term in terms:
            f.write(term+"\t"+tfidfs[terms.index(term)]+"\n")
        
def mecab_tokenizer(text):
    t=MeCab.Tagger("-Ochasen -d /home/momoi/mecab/mecab-ipadic/")
    node=t.parseToNode(text)
    word_list=list()
    while node:
        if node.surface!="":
            res=node.feature/split(",")
            word_type=res[0]
            basic_word=res[6]
            if basic_word!="*":
                word_list.append(basic_word)
        node=node.next
        if node is None:
            break
    return word_list
    
def main(filename):
    word_list=[]
    with open(filename,"r")as f:
        tree=ET.parse(filename)
        root=tree.getroot()
        texts=removeTags(root)
        joined_text_all=join_body_text_all(texts)
        mecab_result=mecab(joined_text_all)
        for rslt in mecab_result.split("\n"):
            if rslt in ["","EOS"]:
                continue
            morph=rslt.split("\t")[1].split(",")[6]
            if morph not in word_list:
                word_list.append(morph)
    with open("./data/bow/"+filename[35:]+"_box.txt","w")as f:
        for word in word_list:
            f.write(word+" ")
    print(len(word_list))

def merge():
    files=get_files("./data/bow/")
    word_list=[]
    for filename in files:
        c=0
        print(filename)
        with open(filename,"r")as f:
            for word in f.read().split(" "):
                if word not in word_list:
                    c+=1
                    word_list.append(word)
            print(c)
    with open("./data/bow/BOW.txt","w")as f:
        for word in word_list:
            f.write(word+" ")
    print(len(word_list))

            
if __name__=="__main__":
    #main(sys.argv[1])
    #merge()
    vectorizer_main()
    #paper2only_text(sys.argv[1])

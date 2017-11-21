from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
from createTrainData import mecab,join_body_text_all
import MeCab
import sys

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
    word_dic_all={}
    for i,text in enumerate(text_list,1):
        if i%20==0:
            print(i,"/",len(text_list))
        word_list_part=[]
        m_rslts=mecab(text).split("\n")
        for rslt in m_rslts:
            if rslt in ["","EOS"]:
                continue
            base=rslt.split("\t")[1].split(",")[6]
            if base=="*":
                continue
            if base not in word_list_part:
                word_list_part.append(base)
        for word in word_list_part:
            if word in word_dic_all:
                word_dic_all[word]+=1
            else:
                word_dic_all[word]=0
    with open("./data/bow/df_list.txt","w")as f:
        i=1
        for word,cnt in word_dic_all.items():
            f.write(word+"\t"+str(cnt/len(text_list))+"\n")
            if i%100==0:
                print(i,"/",len(word_dic_all))
            i+=1

            
def mecab_tokenizer(text):
    t=MeCab.Tagger("-Ochasen -d /home/momo/mecab/mecab-ipadic/")
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

def extract_upper_df_word():
    thr=0.3
    with open("./data/bow/df_list.txt","r")as fr:
        with open("./data/bow/df_list_"+str(thr)+".txt","w")as fw:
            word_list=[]
            for line in fr.readlines():
                word,df=line.split("\t")
                if(float(df)>thr):
                    word_list.append(word)
                    fw.write(word+"\t"+str(df))
            print(len(word_list))
        
    
if __name__=="__main__":
    #main(sys.argv[1])
    #vectorizer_main()
    #paper2only_text(sys.argv[1])
    #extract_upper_df_word()

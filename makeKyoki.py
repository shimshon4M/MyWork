import sys
import os
import glob
import pyknp
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
from createTrainData import processJ

def isJapPaper(contentsDict):
    if "Introduction" in contentsDict.keys():
        return False
    return True

def getTextList(contentsDict):
    retlist=[]
    for key,value in contentsDict.items():
        if key!="":
            retlist.append(key)
        if value!="":
            retlist.append(value)
    return retlist
     
def juman2mecab(juman_result):
    return [[morph.midasi,morph.yomi,morph.genkei,morph.hinsi,morph.bunrui,morph.katuyou1,morph.katuyou2,morph.imis,morph.repname] for morph in juman_result]


def isTargetMorphemeUni(midasi,hinsi,bunrui):
    #a. 1形態素でもキーワード候補になるもの
    if midasi in [".","．","〜"]:
        return False
    if hinsi=="名詞" and bunrui in ["サ変名詞","普通名詞","固有名詞","地名","人名","組織名","形式名詞","副詞的名詞","時相名詞"]:
        return True
    if hinsi=="未定義語":
        return True
    return False

def isTargetMorphemeNotUni(midasi,hinsi,bunrui,katuyou2):
    #b. aと連接することでキーワード候補になるもの
    if midasi in [".","．","〜"]:
        return False
    if hinsi in ["接頭辞","副詞"] or(hinsi in ["形容詞","接尾辞"] and katuyou2 in ["*","語幹"]) or (hinsi=="名詞" and bunrui=="数詞") or (midasi in ["・"]):
        return True
    return False

def execJuman(text):
    juman=pyknp.Jumanpp()
    return juman.analysis(text) #mrph_listが返される
   
def main():
    files=glob.glob("./data/papers/NLP_LATEX_CORPUS/*/*.xml",recursive=False)
    for j,file in enumerate(files): 
        print(j+1," / ",len(files), " : ",file)
        tree=ET.parse(file)
        root=tree.getroot()
        contentsDict=removeTags(root)
        contentsDict.pop("author",None)
        contentsDict.pop("jauthor",None)
        contentsDict.pop("keywords",None)
        contentsDict.pop("jkeywords",None)
        if not isJapPaper(contentsDict):
            #print(list(contentsDict.keys())[:2])
            continue

        text_list=getTextList(contentsDict)
        term_list=[]
        juman_results=[]
        
        #各文に対して処理
        for sec_i,text in enumerate(text_list):
            term_list_s=[]
            #print(text)
            try:
                juman_result=juman2mecab(execJuman(text))
            except:
                continue
            juman_results.append(juman_result)
            #キーワード抽出
            partof_term="" #複合名詞抽出用tmp
            partof_termex="" #用語的表現抽出用tmp
            tmp_partof_termex="" #「○○の△△」の△△の部分を保存しておき、次の○○にする
            now_pos=0 #用語的表現抽出用 現在の場所 0:空 1:○○中 2:"の"済 3:△△中
            word_head_pos=0 #複合語の頭の位置
            word_head_posex=0 #用語的表現の頭の位置
            tmp_word_head_posex=0 #tmp_partof_termexと同じく
            nowread_head_pos=0 #現在処理している形態素の頭の位置
            tmp_i_term=0
            tmp_i_termex=0
            tmp_tmp_i_termex=0
            containsNorm=False
            tailIsSahen=False
            for i,morpheme in enumerate(juman_result):
                #print(morpheme[0])
                #キーワード抽出
                if morpheme[0] not in ["EOS",""]:
                    midasi,yomi,genkei,hinsi,bunrui,katuyou1,katuyou2,imis,repname=morpheme
                    if isTargetMorphemeUni(midasi,hinsi,bunrui):
                        if len(partof_term)==0:
                            word_head_pos=nowread_head_pos
                            tmp_i_term=i
                        partof_term+=midasi
                        containsNorm=True
                        if bunrui=="サ変名詞":
                            tailIsSahen=True
                        else:
                            tailIsSahen=False
                    elif isTargetMorphemeNotUni(midasi,hinsi,bunrui,katuyou2):
                        if len(partof_term)==0:
                            word_head_pos=nowread_head_pos
                            tmp_i_term=i
                        partof_term+=midasi
                        tailIsSahen=False
                    else: # キーワードを構成し得ない形態素の場合
                        if len(partof_term)>0 and containsNorm:
                            term_list_s.append(partof_term)
                            if len(partof_termex)>0 and tailIsSahen: #「○○の」が住んでいて次にサ変名詞で終わるtermが来た場合
                                tmp_partof_termex=partof_term
                                tmp_word_head_posex=word_head_pos
                                tmp_tmp_i_termex=tmp_i_term
                                partof_termex+=partof_term
                                term_list_s.append(partof_termex)
                                partof_termex=""
                                word_head_posex=0
                            elif len(partof_termex)>0 and not tailIsSahen: #「○○の」が済んていて次にサ変名詞で終わらないtermが来た場合、それを次の「○○の」候補に
                                tmp_partof_termex=partof_term
                                tmp_word_head_posex=word_head_pos
                                tmp_tmp_i_termex=tmp_i_term
                            if midasi in ["の","を"] and hinsi=="助詞":
                                if len(tmp_partof_termex)>0: # この前にも「○○の△△」が来た場合
                                    partof_termex=(tmp_partof_termex+"の")
                                    word_head_posex=tmp_word_head_posex
                                    tmp_i_termex=tmp_tmp_i_termex
                                    tmp_partof_termex=""
                                    tmp_word_head_posex=0
                                    partof_term=""
                                    nowread_head_pos+=len(midasi)
                                    continue
                                if len(partof_termex)==0: # 初めて「○○の」を作る場合
                                    partof_termex+=(partof_term+"の")
                                    word_head_posex=word_head_pos
                                    tmp_i_termex=tmp_i_term
                                    tailIsSahen=False
                                    partof_term=""
                                    word_head_pos=0
                                    tmp_partof_termex=""
                                    tmp_word_head_posex=0
                                    nowread_head_pos+=len(midasi)
                                    continue
                                
                            
                        partof_term=""
                        partof_termex=""
                        tmp_partof_termex=""
                        now_pos=0
                        word_head_pos=0
                        word_head_posex=0
                        tmp_word_head_posex=0
                        containsNorm=False
                        tailIsSahen=False
                    if i+1==len(juman_result):
                        if len(partof_term)>0 and containsNorm:
                            term_list_s.append(partof_term)
                            if len(partof_termex)>0 and tailIsSahen:
                                tmp=partof_term
                                partof_termex+=partof_term
                                term_list_s.append(partof_termex)
                nowread_head_pos+=len(midasi)
            term_list.append(set(term_list_s))
        
        #for l in term_list:
        #    print(l)

        term_dic={}
        term_files=glob.glob("./data/xml/Kyoki/*.txt",recursive=False)                    
        for i,term_list_s in enumerate(term_list):
            for term in term_list_s:
                if term not in term_dic:
                    term_dic[term]={}
                for term2 in term_list_s:
                    if term==term2:
                        continue
                    if term2 not in term_dic[term]:
                        term_dic[term][term2]=1
                    else:
                        term_dic[term][term2]+=1

        for term,term_dic_inner in term_dic.items():
            term_tmp=""
            if "<SLASH>" in term_tmp:
                term_tmp=term.replace("<SLASH>","/")
            if "<BSLASHA>" in term_tmp:
                term_tmp=term.replace("<BSLASHA>","\a")
            if "<BSLASHB>" in term_tmp:
                term_tmp=term.replace("<BSLASHB>","\b")
            if "<BSLASHF>" in term_tmp:
                term_tmp=term.replace("<BSLASHF>","\f")
            if "<BSLASHT>" in term_tmp:
                term_tmp=term.replace("<BSLASHT>","\t")
            if "<BSLASHR>" in term_tmp:
                term_tmp=term.replace("<BSLASHR>","\r")
            if "<BSLASHN>" in term_tmp:
                term_tmp=term.replace("<BSLASHN>","\n")
            if "<BSLASHV>" in term_tmp:
                term_tmp=term.replace("<BSLASHV>","\v")
            if "<BSLASHU>" in term_tmp:
                term_tmp=term.replace("<BSLASHU>","\\u")
            if "<BSLASHUU>" in term_tmp:
                term_tmp=term.replace("<BSLASHUU>","\\U")
            if "<BSLASHX>" in term_tmp:
                term_tmp=term.replace("<BSLASHX>","\\x")
            if "<BSLASHO>" in term_tmp:
                term_tmp=term.replace("<BSLASHO>","\\o")
            if "<BSLASH0>" in term_tmp:
                term_tmp=term.replace("<BSLASH0>","\0")
            if not os.path.exists("./data/xml/Kyoki/"+term_tmp+".txt"):
                continue
            with open("./data/xml/Kyoki/"+term+".txt","r")as f:
                for line in f.readlines():
                    tl=""
                    if "<SLASH>" in line:
                        tl=line.replace("<SLASH>","/")
                    if "<BSLASHA>" in line:
                        tl=line.replace("<BSLASHA>","\a")
                    if "<BSLASHB>" in line:
                        tl=line.replace("<BSLASHB>","\b")
                    if "<BSLASHF>" in line:
                        tl=line.replace("<BSLASHF>","\f")
                    if "<BSLASHT>" in line:
                        tl=line.replace("<BSLASHT>","\t")
                    if "<BSLASHR>" in line:
                        tl=line.replace("<BSLASHR>","\r")
                    if "<BSLASHN>" in line:
                        tl=line.replace("<BSLASHN>","\n")
                    if "<BSLASHV>" in line:
                        tl=line.replace("<BSLASHV>","\v")
                    if "<BSLASHU>" in line:
                        tl=line.replace("<BSLASHU>","\\u")
                    if "<BSLASHUU>" in line:
                        tl=line.replace("<BSLASHUU>","\\U")
                    if "<BSLASHX>" in line:
                        tl=line.replace("<BSLASHX>","\\x")
                    if "<BSLASHO>" in line:
                        tl=line.replace("<BSLASHO>","\\o")
                    if "<BSLASH0>" in line:
                        tl=line.replace("<BSLASH0>","\0")
                    if tl=="":
                        t2,c=line.strip().split("\t")
                    else:
                        t2,c=tl.strip().split("\t")
                    if t2 in term_dic_inner:
                        term_dic[term_tmp][t2]+=int(c)
                    else:
                        term_dic[term_tmp][t2]=int(c)
                        
        for term,term_dic_inner in term_dic.items():
            if "/" in term:
                term=term.replace("/","<SLASH>")
            if "\a" in term:
                term=term.replace("\a","<BSLASHA>")
            if "\b" in term:
                term=term.replace("\b","<BSLASHB>")
            if "\f" in term:
                term=term.replace("\f","<BSLASHF>")
            if "\t" in term:
                term=term.replace("\t","<BSLASHT>")
            if "\r" in term:
                term=term.replace("\r","<BSLASHR>")
            if "\n" in term:
                term=term.replace("\n","<BSLASHN>")
            if "\v" in term:
                term=term.replace("\v","<BSLASHV>")
            if "\\u" in term:
                term=term.replace("\\u","<BSLASHU>")
            if "\\U" in term:
                term=term.replace("\\U","<BSLASHUU>")
            if "\\x" in term:
                term=term.replace("\\x","<BSLASHX>")
            if "\\o" in term:
                term=term.replace("\\o","<BSLASHO>")
            if "\0" in term:
                term=term.replace("\0","<BSLASH0>")
            with open("./data/xml/Kyoki/"+term+".txt","w")as f:
                for term2,count in term_dic_inner.items():
                    term2t=term2
                    if "/" in term2:
                        term2t=term2.replace("/","<SLASH>")
                    if "\a" in term2:
                        term2t=term2.replace("\a","<BSLASHA>")
                    if "\b" in term2:
                        term2t=term2.replace("\b","<BSLASHB>")
                    if "\f" in term2:
                        term2t=term2.replace("\f","<BSLASHF>")
                    if "\t" in term2:
                        term2t=term2.replace("\t","<BSLASHT>")
                    if "\r" in term2:
                        term2t=term2.replace("\r","<BSLASHR>")
                    if "\n" in term2:
                        term2t=term2.replace("\n","<BSLASHN>")
                    if "\v" in term2:
                        term2t=term2.replace("\v","<BSLASHV>")
                    if "\\u" in term2:
                        term2t=term2.replace("\\u","<BSLASHU>")
                    if "\\U" in term2:
                        term2t=term2.replace("\\U","<BSLASHUU>")
                    if "\\x" in term2:
                        term2t=term2.replace("\\x","<BSLASHX>")
                    if "\\o" in term2:
                        term2t=term2.replace("\\o","<BSLASHO>")
                    if "\0" in term2:
                        term2t=term2.replace("\0","<BSLASH0>")
                    f.write(term2t+"\t"+str(count)+"\n")
        
    
if __name__=="__main__":
    main()

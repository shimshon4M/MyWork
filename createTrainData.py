"""
実行時は引数に論文xmlファイルを指定
"""

import collections
import sys
import re
import os
import math
import pdb
from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
import pyknp
import pandas as pd
import json


f_type="BoW"
#BoW W2V posBoW posW2V W2VSum W2VSumBoW

        
def read_w2v():
    dic={}
    with open("../fastText/model_J_d200n25w10.vec","r")as f:
    #with open("./data/jvectors50000.txt","r")as f:
    #with open("./data/model/word2vec_NLP_LCorpus.txt","r")as f:
        for line in f.readlines()[1:]:
            word=line.split(" ")[0].strip()
            dic[word]=[str(v).strip() for v in line.split(" ")[1:]] #研究室w2vなら2,fasttextなら1,gensimword2vecなら1：
    return dic
w2vDic=read_w2v()

def processEachTerm(term_num,term_dic,mecab_result_list,n,titleabst_str=[],keywords=[],fulltext=""): #n:素性とするngramの範囲
    """
    各語に対する素性抽出処理
    素性データは[対象語,出現場所pos,出現頻度,1文字か,タイトルに含まれるか,アブストに含まれるか,キーワードに含まれるか,前後n形態素基本形列挙,前後n形態素品詞列挙,基本形ベクトル化,品詞ベクトル化]
    """
    knp=pyknp.KNP(command='knp',option='-tab -anaphora',jumancommand='jumanpp',jumanpp=True)
    knp_results=[[],[]] #list of title,list of abst
    knp_results[0].append(knp.parse(titleabst_str[0]))
    for sentence in re.split(r"\.|。",replaceDpoint(titleabst_str[1].replace("．","."))):
    #for sentence in replaceDpoint(titleabst_str[1].replace("．",".")).split("."):
        #print(sentence.replace("<dpoint>","."))
        knp_results[1].append(knp.parse(sentence.replace("<dpoint>",".")+"．"))
        #print(sentence.replace("<dpoint>",".")+"．")
    head_morph_ids=[0]#abst各文の先頭の形態素番号を保持
    #print(re.split(r"\.|。",replaceDpoint(titleabst_str[1].replace("．",".")).replace("<dpoint>",".")))
    #sys.exit()
    now=0
    for rslt in knp_results[1]:
        now=now+len(rslt.mrph_list())
        head_morph_ids.append(now)
        #print(len(rslt.mrph_list()))
        #for m in rslt.mrph_list():
        #    print(m.midasi+" ",end="")
        #print()
    head_morph_ids.pop()

    #for rslt in knp_results:
    #    for r in rslt:
    #        for m in r.mrph_list():
    #            print(m.midasi)

    #num=0
    #for rslt in knp_results[1]:
    #    print(rslt.mrph_list()[0].midasi,num)
    #    num+=len(rslt.mrph_list())
    #print(head_morph_ids)
    #sys.exit()
    outputdata=[] #素性 dictのlist returnする
    freq_list=getFreqList(term_dic,fulltext)
    for term,pos_list in term_dic.items():
        in_title="0.0"
        in_abst="0.0"
        in_kw="0.0"
        if term in titleabst_str[0]:
            in_title="1.0"
        if term in titleabst_str[1]:
            in_abst="1.0"
        if term in keywords:
            int_kw="1.0"
        #freq=str(calcFreqFeature(freq_list,len(pos_list),10))#これ使うか単純に出現頻度そのまま入れるか
        freq=str(calcTfidfFeature(term,len(pos_list),term_num))
        is_uni="0.0"
        if len(term)==1:
            is_uni="1.0"
        digit_rate=str(digit_num_per_term(term))
        alpha_rate=str(alpha_num_per_term(term))
        #tmpdata=[term,freq,is_uni,digit_rate,alpha_rate,in_title,in_abst,in_kw]
        tmpdata={"term":term,"freq":freq,"is_uni":is_uni,"digit_rate":digit_rate,"alpha_rate":alpha_rate,"in_title":in_title,"in_abst":in_abst,"in_kw":in_kw}
        #print("term : ",term)
        for pos in pos_list:
            #print("  pos : ",pos)
            e_pos=pos[1]
            sec_num=pos[0]
            #単語が含まれているknp解析結果を取得
            if sec_num==0:
                knprslt=knp_results[0][0]
                s_id=pos[1]
            else:
                #print(term,e_pos,":")
                for h_i,head in enumerate(head_morph_ids):
                    if e_pos<head:
                        #print(e_pos,head)
                        knprslt=knp_results[1][h_i-1]
                        h=head_morph_ids[h_i-1]
                        break
                s_id=e_pos-h#その文での形態素id
                #print(term,knprslt.mrph_list()[s_id].midasi,s_id,h)
                
            e_id=s_id
            tmp_term_len=len(mecab_result_list[sec_num][e_pos][0])
            #print(term)
            while tmp_term_len!=len(term):#単語の末尾posを求める
                #print(" ",mecab_result_list[sec_num][e_pos+1][0])
                tmp_term_len+=len(mecab_result_list[sec_num][e_pos+1][0])
                e_pos+=1
                e_id+=1
            #print(term,s_id,e_id,knprslt)
            #kihon_b,kihon_f,hinshi_b,hinshi_f=getBehindFrontNMorphenes(mecab_result_list[sec_num],pos[1],e_pos,n)
            kihon_b,kihon_f,hinshi_b,hinshi_f=getBehindFrontNMorphenesByKNP(knprslt,s_id,e_id,n)            
            #print(kihon_b,term,kihon_f)
            kihon_kakari_f,hinshi_kakari_f=getBehindFrontNMorphenesKakariByKNP(knprslt,s_id,e_id,n)
            #print(term,kihon_kakari_f)
            
            #print("".join(kihon[:4]),term,"".join(kihon[4:]))
            tmpdata["pos"]=pos
            tmpdata["kihon_before_appear"]=(kihon_b)
            tmpdata["kihon_front_appear"]=(kihon_f)
            tmpdata["hinshi_before_appear"]=(hinshi_b)
            tmpdata["hinshi_front_appear"]=(hinshi_f)
            tmpdata["kihon_kakari_front_appear"]=(kihon_kakari_f)
            tmpdata["hinshi_kakari_front_appear"]=(hinshi_kakari_f)
            extend_feature_vector(tmpdata,term,kihon_b,kihon_f,hinshi_b,hinshi_f,kihon_kakari_f,hinshi_kakari_f)
            outputdata.append(tmpdata)
            tmpdata={"term":term,"freq":freq,"is_uni":is_uni,"digit_rate":digit_rate,"alpha_rate":alpha_rate,"in_title":in_title,"in_abst":in_abst,"in_kw":in_kw}
    #sys.exit()
    return outputdata

def getBehindFrontNMorphenesKakariByKNP(knp_result,s_id,e_id,n):
    """
    とりあえず係り先だけでいい？
    """
    #文節idの特定
    for bnst in knp_result.bnst_list():
        for mrph in bnst.mrph_list():
            #print(mrph.midasi,mrph.mrph_id,e_id)
            #if mrph.mrph_id==s_id:
            #    s_bnst_id=bnst.bnst_id
            if mrph.mrph_id==e_id:
                e_bnst_id=bnst.bnst_id
                break
    if knp_result.bnst_list()[e_bnst_id].parent!=None:
        if knp_result.bnst_list()[e_bnst_id].dpndtype=="P":
            if knp_result.bnst_list()[e_bnst_id].parent.parent!=None:
                kakari_bnst_id=knp_result.bnst_list()[e_bnst_id].parent.parent.bnst_id
            else:
                kakari_bnst_id=None
        else:
            kakari_bnst_id=knp_result.bnst_list()[e_bnst_id].parent.bnst_id
    else:
        kakari_bnst_id=None
    kihon_f=[]
    hinshi_f=[]
    #まずは同文節内に出現するならそれを
    flg=True
    for i,mrph in enumerate(knp_result.bnst_list()[e_bnst_id].mrph_list()):
        if mrph.mrph_id!=e_id and flg:
            continue
        flg=False
        if i+1<len(knp_result.bnst_list()[e_bnst_id].mrph_list()) and len(kihon_f)<3:
            kihon_f.append(knp_result.bnst_list()[e_bnst_id].mrph_list()[i+1].genkei)
            hinshi_f.append("-".join([knp_result.bnst_list()[e_bnst_id].mrph_list()[i+1].hinsi,knp_result.bnst_list()[e_bnst_id].mrph_list()[i+1].bunrui]))
    #次に係り先文節から
    while len(kihon_f)<3:
        if kakari_bnst_id==None:
            kihon_f.append("*")
            hinshi_f.append("*")
            continue
        for i,mrph in enumerate(knp_result.bnst_list()[kakari_bnst_id].mrph_list()):
            if len(kihon_f)<3:
                kihon_f.append(knp_result.bnst_list()[kakari_bnst_id].mrph_list()[i].genkei)
                hinshi_f.append("-".join([knp_result.bnst_list()[kakari_bnst_id].mrph_list()[i].hinsi,knp_result.bnst_list()[kakari_bnst_id].mrph_list()[i].bunrui]))
        if knp_result.bnst_list()[kakari_bnst_id].parent!=None:
            if knp_result.bnst_list()[kakari_bnst_id].dpndtype=="P":
                if knp_result.bnst_list()[kakari_bnst_id].parent.parent!=None:
                    kakari_bnst_id=knp_result.bnst_list()[kakari_bnst_id].parent.parent.bnst_id
                else:
                    kakari_bnst_id=None
            else:
                kakari_bnst_id=knp_result.bnst_list()[kakari_bnst_id].parent.bnst_id
        else:
            kakari_bnst_id=None
    return kihon_f,hinshi_f
        
def getBehindFrontNMorphenesByKNP(knp_result,s_id,e_id,n):
    """
    前後n形態素の基本形と品詞をそれぞれリストで返す
    """
    kihon_b=[]
    kihon_f=[]
    hinshi_b=[]
    hinshi_f=[]
    for i in range(s_id-n,s_id):
        #print(i)
        if i<0 or i>=len(knp_result.mrph_list()): #文外は＊で埋める
            kihon_b.append("*")
            hinshi_b.append("*")
        else:
            kihon_b.append(knp_result.mrph_list()[i].genkei)
            hinshi_b.append("-".join([knp_result.mrph_list()[i].hinsi,knp_result.mrph_list()[i].bunrui]))
    for i in range(e_id+1,e_id+n+1):
        #print(i)
        if i<0 or i>=len(knp_result.mrph_list()): #文外は＊で埋める
            kihon_f.append("*")
            hinshi_f.append("*")
        else:
            kihon_f.append(knp_result.mrph_list()[i].genkei)
            hinshi_f.append("-".join([knp_result.mrph_list()[i].hinsi,knp_result.mrph_list()[i].bunrui]))
    return kihon_b,kihon_f,hinshi_b,hinshi_f


def calcTfidfFeature(term,appear_num,term_num):
    tf=appear_num/term_num
    with open("./data/df.txt","r")as f:
        lines=f.readlines()
        for line in lines:
            if line.split("\t")[0]==term:
                df=float(line.split("\t")[1])
                idf=math.log(len(lines)/df)+1
                return tf*idf
    return 0.0

def digit_num_per_term(term):
    cnt=0
    for t in term:
        if t.isdigit():
            cnt+=1
    return cnt/len(term)

def alpha_num_per_term(term):
    cnt=0
    for t in term:
        if t.isalpha():
            cnt+=1
    return cnt/len(term)

def extend_feature_vector(feature_dict,term,kihon_b,kihon_f,hinshi_b,hinshi_f,kihon_kakari_f,hinshi_kakari_f):
    components_kihon,components_hinshi=get_term_components(term)
    #General
    extend_feature_vector_BoW(feature_dict,components_hinshi,"hinshi","own_hinshi_bow")#自身
    extend_feature_vector_BoW(feature_dict,hinshi_b,"hinshi","hinshi_b_bow")#周辺の品詞b
    extend_feature_vector_BoW(feature_dict,hinshi_f,"hinshi","hinshi_f_bow")#周辺の品詞f
    extend_feature_vector_BoW(feature_dict,hinshi_kakari_f,"hinshi","hinshi_kakari_f_bow")#周辺の品詞f_kakari
    extend_feature_vector_contains_NO(feature_dict,term)#"○○の△△"か
    #BOW
    extend_feature_vector_BoW(feature_dict,components_kihon,"kihon","own_kihon_bow")#自身
    extend_feature_vector_BoW(feature_dict,kihon_b,"kihon","kihon_b_bow")#周辺の基本形before
    extend_feature_vector_BoW(feature_dict,kihon_f,"kihon","kihon_f_bow")#周辺の基本形front
    extend_feature_vector_BoW(feature_dict,kihon_kakari_f,"kihon","kihon_kakari_f_bow")#周辺の基本形front_kakari
    #W2V
    extend_feature_vector_W2VSum(feature_dict,components_kihon,"own_kihon_w2v")#自身
    extend_feature_vector_W2VSum(feature_dict,kihon_b,"kihon_b_w2v")#周辺の基本形
    extend_feature_vector_W2VSum(feature_dict,kihon_f,"kihon_f_w2v")#周辺の品詞
    extend_feature_vector_W2VSum(feature_dict,kihon_kakari_f,"kihon_kakari_f_w2v")#周辺の品詞_kakari
        

    
def extend_feature_vector_contains_NO(feature_dict,term):
    #mecab_results=mecab(term).split("\n")
    #if "の\t助詞,連体化,*,*,*,*,の,ノ,ノ" in mecab_results:
        #print("contain")
    #    feature_list.append("1.0")
    #else:
        #print("not contain")
    #    feature_list.append("0.0")
    juman_result=juman2mecab(execJuman(term))
    for morph in juman_result:
        if morph[0]=="の" and morph[3]=="助詞":
            feature_dict["contains_no"]="1.0"
            return
    feature_dict["contains_no"]="0.0"
    
def get_term_components(term):
    kihon=[]
    hinshi=[]
    juman_result=juman2mecab(execJuman(term))
    kihon.append(juman_result[0][2])
    kihon.append(juman_result[-1][2])
    hinshi.append("-".join(juman_result[0][3:4]))
    hinshi.append("-".join(juman_result[-1][3:4]))
    #mecab_results=mecab(term).split("\n")
    #if mecab_results[0].split("\t")[1].split(",")[6]=="*":
    #    kihon.append(mecab_results[0].split("\t")[0])
    #else:
    #    kihon.append(mecab_results[0].split("\t")[1].split(",")[6])
    #if mecab_results[-3].split("\t")[1].split(",")[6]=="*":
    #    kihon.append(mecab_results[-3].split("\t")[0])
    #else:
    #    kihon.append(mecab_results[-3].split("\t")[1].split(",")[6])
    #hinshi.extend(["-".join(mecab_results[0].split("\t")[1].split(",")[0:2]),"-".join(mecab_results[-3].split("\t")[1].split(",")[0:2])])
    #print(kihon,hinshi)
    return kihon,hinshi

def extend_feature_vector_BoW(feature_dict,extend_list,vec_type,dict_key_label):
    """
    出現頻度を考慮しない単純なBoW(前後n形態素を見るがその位置情報は不保持)
    """
    if vec_type=="kihon":
        with open("./data/bow/df_list_0.3.txt","r")as f:
            feature_list=[]
            for line in f.readlines():
                word=line.split("\t")[0]
                if word in extend_list:
                    feature_list.append("1.0")
                else:
                    feature_list.append("0.0")
            feature_dict[dict_key_label]=feature_list
    elif vec_type=="hinshi":
        with open("./data/bow/HINSHI.txt","r")as f:
            feature_list=[]
            for word in f.readlines():
                if word.strip() in extend_list:
                    feature_list.append("1.0")
                else:
                    feature_list.append("0.0")
            feature_dict[dict_key_label]=feature_list

def extend_feature_vector_W2VSum(feature_dict,extend_list,dict_key_label): #位置考慮せず単語分散表現平均
    append_vector=[0.0 for i in range(200)]
    exist_num=0 #素性単語の中で辞書に存在する単語の数
    for ex_elem in extend_list:
        if ex_elem in w2vDic:
            append_vector=[x+float(y) for x,y in zip(append_vector,w2vDic[ex_elem])]
            exist_num+=1
    if exist_num>0:
        #append_vector=[str(x) for x in append_vector] #全加算
        append_vector=[str(x/exist_num) for x in append_vector] #平均
    else:
        append_vector=["0.0" for i in range(200)]
    feature_dict[dict_key_label]=append_vector

def getFreqList(term_dic,fulltext):
    freq_list=[len(re.findall(key,fulltext)) for key in term_dic.keys()]
    freq_list.sort()
    return freq_list

def calcFreqFeature(freq_list,freq,n):#n:分割数
    pos_dif=len(freq_list)//n
    pos=pos_dif
    ret=0
    for i in range(n-1):
        if freq>=freq_list[pos]:
            ret=i+1
        pos+=pos_dif
    return ret

def getBehindFrontNMorphenes(juman_results,s_pos,e_pos,n): #s_pos,e_posはキーワード(複合語)のpos
    """
    前後n形態素の基本形と品詞をそれぞれリストで返す
    """
    kihon_b=[]
    kihon_f=[]
    hinshi_b=[]
    hinshi_f=[]
    for i in range(s_pos-n,s_pos):
        #print(i)
        if i<0 or i>=len(juman_results) or juman_results[i]=="": #文外は＊で埋める
            kihon_b.append("*")
            hinshi_b.append("*")
        else:
            kihon_b.append(juman_results[i][2])
            hinshi_b.append("-".join(juman_results[i][3:5]))
    for i in range(e_pos+1,e_pos+n+1):
        #print(i)
        if i<0 or i>=len(juman_results) or juman_results[i]=="": #文外は＊で埋める
            kihon_f.append("*")
            hinshi_f.append("*")
        else:
            kihon_f.append(juman_results[i][2])
            hinshi_f.append("-".join(juman_results[i][3:5]))
            
    return kihon_b,kihon_f,hinshi_b,hinshi_f

    
def execJuman(text):
    juman=pyknp.Jumanpp()
    return juman.analysis(text) #mrph_listが返される

def removeUnderValueFromDict(target_dict,rmv_value):
    """
    指定のrmv_value以下の出現回数の語を辞書から除去
    """
    for k,v in list(target_dict.items()):
        if len(v)<rmv_value:
            del(target_dict[k])

def remove_later_pos_terms(term_dic,rmv_pos):
    """
    引数pos以降にしか出現しない語は除去する
    """
    is_appear=False
    for term,poses in list(term_dic.items()):
        for pos in poses:
            if pos<rmv_pos:
                is_appear=True
                break
        if not is_appear:
            del(term_dic[term])
        
            
def writeFile(filename,datas):
    with open(filename,"w")as f:
        for data in datas:
            f.write("\t".join(data)+"\n")

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
    
    
def processJ(filename,text_list,title,abstract,keywords,fulltext,retTermDic=False):
    """
    メイン処理 juman ver
    """
    term_dic={}#キーワードリスト key:キーワード value:出現位置リスト(lenで出現回数も求まる) セクションナンバーと出現位置(形態素番号)と出現位置(単純文字列)のタプル
    juman_results=[]
    #各文に対して処理
    for sec_i,text in enumerate(text_list):
        #print(text)
        juman_result=juman2mecab(execJuman(text))
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
                        if(partof_term in term_dic):
                            term_dic[partof_term].append((sec_i,tmp_i_term,word_head_pos))
                        else:
                            term_dic[partof_term]=[(sec_i,tmp_i_term,word_head_pos)]
                        if len(partof_termex)>0 and tailIsSahen: #「○○の」が住んでいて次にサ変名詞で終わるtermが来た場合
                            tmp_partof_termex=partof_term
                            tmp_word_head_posex=word_head_pos
                            tmp_tmp_i_termex=tmp_i_term
                            partof_termex+=partof_term
                            if(partof_termex in term_dic):
                                term_dic[partof_termex].append((sec_i,tmp_i_termex,word_head_posex))
                            else:
                                term_dic[partof_termex]=[(sec_i,tmp_i_termex,word_head_posex)]
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
                        if(partof_term in term_dic):
                            term_dic[partof_term].append((sec_i,tmp_i_term,word_head_pos))
                        else:
                            term_dic[partof_term]=[(sec_i,tmp_i_term,word_head_pos)]
                        if len(partof_termex)>0 and tailIsSahen:
                            tmp=partof_term
                            partof_termex+=partof_term
                            if(partof_termex in term_dic):
                                term_dic[partof_termex].append((sec_i,tmp_i_termex,word_head_posex))
                            else:
                                term_dic[partof_termex]=[(sec_i,tmp_i_termex,word_head_posex)]
            nowread_head_pos+=len(midasi)
    term_num=0# termの総個数(tf用
    for value in term_dic.values():
        term_num+=len(value)
    if retTermDic:
        return term_dic
    #print(term_dic.items())
    feature_data=processEachTerm(term_num,term_dic,list(filter(lambda x:x not in ["EOS",""],juman_results)),3,[title,abstract],keywords.split(","),fulltext)
    #print(term_num,len(feature_data),type(feature_data))

    #for f in feature_data:
    #   print(f)
    writeFileJson(filename[:-4]+"_feature.json",feature_data)

    #tfidf(アブストのみ)用
    #with open(filename[:-4]+"_terms.txt","w")as f:
    #    for term,poses in term_dic.items():
    #        f.write(term+"\t"+str(len(poses))+"\n")
    #-------------------------



    
def split_texts(unit_texts):
    """
    ピリオドでsplitした方が後々やりやすいと思うから
    """
    for attrib,texts in unit_texts.items():
        unit_texts[attrib]=re.split(r"\.|。|．",texts) #。も残したい？(素性になりうるかもなので)
        print(unit_texts[attrib])

def get_partof_text_list(texts,join_section_pattern):
    """
    join_section_patternは[a,b,c,d,e,f]の5要素リスト
    a==1->title b==1->abstract c==1->キーワード d==1->序論 e==1->結論 f==1->残り をjoined_textに含む
    """
    ret_text_list_tmp=[]
    keywords=""
    for attrib,text in texts.items():
        if attrib=="title" and join_section_pattern[0]==1:
            ret_text_list_tmp.append(get_section_text(texts,"title"))
        elif attrib=="abstract" and join_section_pattern[1]==1:
            ret_text_list_tmp.append(get_section_text(texts,"abstract"))
        elif attrib=="keywords" and join_section_pattern[2]==1:
            keywords+=get_section_text(texts,"keywords")
        elif attrib not in ["title","abstract"] and join_section_pattern[2]==1:
            ret_text_list_tmp.append(text)
    ret_text_list=[text.replace("(","（").replace(")","）") for text in ret_text_list_tmp]
    #ret_text_list=[text for text in ret_text_list_tmp]
    return ret_text_list,keywords

def join_body_text_all(texts):
    joined_text=""
    for attrib,text in texts.items():
        if attrib =="title":
            joined_text+=text
            joined_text+="."
        else:
            joined_text+=text
    return joined_text

"""
序論って背景とか一般知識も書かれているから使うべきじゃない？
セクション見てて発見したもの
・まとめとおわりにが両方あるもの
・「序論-○○」みたいな特殊形
"""
def get_section_text(texts,section_type):
    """
    辞書textsの中から引数section_typeの本文を返す
    title,abstract,intro,conclusion,etc
    """
    if section_type=="title":
        return texts["title"].replace(" ","")
    elif section_type=="abstract":
        return texts["abstract"].replace(" ","")
    elif section_type=="keywords":
        return texts["keywords"].replace(" ","")
    for attrib,text in texts.items():
        if section_type=="intro" and attrib in ["はじめに","序論","まえがき","はしがき"]:
            return text.replace(" ","")
        elif section_type=="conclusion" and attrib in ["おわりに","終わりに","結論","結論と今後の課題","結論および今後の課題","むすび","結び","まとめ","まとめと今後の課題","まとめと今後の方針","まとめ,及び今後の課題","まとめと今後の研究","あとがき"]:
            return text.replace(" ","")
    return ""


def replaceDpoint(text):
    ret_text=""
    for i,c in enumerate(text):
        if c=="." and i+1<len(text) and i>0:
            if text[i-1] in ["0","1","2","3","4","5","6","7","8","9"] and text[i+1] in ["0","1","2","3","4","5","6","7","8","9"]:
                ret_text+="<dpoint>"
            else:
                ret_text+=c
        else:
            ret_text+=c
    return ret_text
        
def createRelTrainData(filename,text_list,term_dic,n=3):
    juman_results=[]
    #各文に対して処理
    for sec_i,text in enumerate(text_list):
        #print(text)
        juman_result=juman2mecab(execJuman(text))
        juman_results.append(juman_result)
    mecab_result_list=list(filter(lambda x:x not in ["EOS",""],juman_results))
    head_poses=[]#アブスト各文の文頭位置
    p=0
    for sentence in replaceDpoint(text_list[1].replace("．",".")).split("."):
        head_poses.append(p)
        p+=(len(sentence.replace("<dpoint>","."))+1)
    #termを出現文によって分離
    print("process term list")
    title_terms=[] #タプル(term,pos)のリスト
    abst_terms={}  #タプル(term,pos)のリスト の辞書
    for p in head_poses:
        abst_terms[p]=[] #空のリストで初期化しておく
    for term,poses in term_dic.items():
        for pos in poses:
            if pos[0]==0:
                title_terms.append((term,pos))
            else:
                abst_terms[getPosIndex(pos[2],head_poses)].append((term,pos))
                #print(term,pos[2],getPosIndex(pos[2],head_poses))
    terms_list=abst_terms.values()
    #print(abst_terms.keys())
    #for k,v in abst_terms.items():
    #    print("key:",k," value:",v)
    #print("len(terms_list)= ",len(terms_list))
    print("process KNP")
    knp=pyknp.KNP(command='knp',option='-tab -anaphora',jumancommand='jumanpp',jumanpp=True)
    knp_results=[[],[]] #list of title,list of abst
    knp_results[0].append(knp.parse(text_list[0]))
    for sentence in re.split(r"\.|。",replaceDpoint(text_list[1].replace("．","."))):
    #for sentence in replaceDpoint(titleabst_str[1].replace("．",".")).split("."):
        #print(sentence.replace("<dpoint>","."))
        knp_results[1].append(knp.parse(sentence.replace("<dpoint>",".")+"．"))
        #print(sentence.replace("<dpoint>",".")+"．")
    head_morph_ids=[0]#abst各文の先頭の形態素番号を保持
    #print(re.split(r"\.|。",replaceDpoint(titleabst_str[1].replace("．",".")).replace("<dpoint>",".")))
    #sys.exit()
    now=0
    for rslt in knp_results[1]:
        now=now+len(rslt.mrph_list())
        head_morph_ids.append(now)
        #print(len(rslt.mrph_list()))
        #for m in rslt.mrph_list():
        #    print(m.midasi+" ",end="")
        #print()
    head_morph_ids.pop()
    feature_datas=[]
    done_mrph_num=0
    done_mrph_num_next=0
    print("process each term")
    for i,terms in enumerate(terms_list):
        print(terms)
        #print(i," ",terms)
        if i>0:
            done_mrph_num_next+=len(knp_results[1][i-1].mrph_list())
        for termL in terms: # L->R
            #print("same sentence")
            #print(termL)
            s_posL=termL[1][1]-done_mrph_num
            e_posL=termL[1][1]-done_mrph_num
            sec_numL=termL[1][0]
            #単語が含まれているknp解析結果を取得
            if sec_numL==0:
                knprslt=knp_results[0][0]
                s_idL=termL[1][1]
            else:
                #print(term,e_pos,":")
                for h_i,head in enumerate(head_morph_ids):
                    if e_posL<head:
                        #print(e_pos,head)
                        knprslt=knp_results[1][h_i-1]
                        h=head_morph_ids[h_i-1]
                        break
                s_idL=e_posL-h#その文での形態素id
                #print(term,knprslt.mrph_list()[s_id].midasi,s_id,h)
                
            e_idL=s_idL
            tmp_term_len=len(mecab_result_list[sec_numL][e_posL][0])#e_pos求める
            while tmp_term_len!=len(termL[0]):
                #print(e_posL," ",knp_results[i-1].mrph_list()[e_posL+1].midasi)
                tmp_term_len+=len(mecab_result_list[sec_numL][e_posL+1][0])
                e_posL+=1
                e_idL+=1
            kihonL_b,kihonL_f,hinshiL_b,hinshiL_f=getBehindFrontNMorphenesByKNP(knprslt,s_idL,e_idL,n) #この辺途中
            kihon_kakariL_f,hinshi_kakariL_f=getBehindFrontNMorphenesKakariByKNP(knprslt,s_idL,e_idL,n)
            #print("start:",termL[1][1]," end:",e_posL)
            #print(kihonL,hinshiL)
            for termR in terms:
                if isSameTerm(termL,termR):
                    continue
                print(termL[0],"->",termR[0])
                s_posR=termR[1][1]-done_mrph_num
                e_posR=termR[1][1]-done_mrph_num
                sec_numR=termR[1][0]
                #単語が含まれているknp解析結果を取得
                if sec_numR==0:
                    knprslt=knp_results[0][0]
                    s_idR=termR[1][1]
                else:
                    #print(term,e_pos,":")
                    for h_i,head in enumerate(head_morph_ids):
                        if e_posR<head:
                            #print(e_pos,head)
                            knprslt=knp_results[1][h_i-1]
                            h=head_morph_ids[h_i-1]
                            break
                    s_idR=e_posR-h#その文での形態素id
                    #print(term,knprslt.mrph_list()[s_id].midasi,s_id,h)
                e_idR=s_idR
                tmp_term_len=len(mecab_result_list[sec_numR][e_posR][0])#e_pos求める
                while tmp_term_len!=len(termR[0]):
                    tmp_term_len+=len(mecab_result_list[sec_numR][e_posR+1][0])
                    e_posR+=1
                    e_idR+=1
                #print(termL[0]," ",termR[0]," ",knpresult.mrph_list()[s_posR].midasi," ",knp_results[i-1].mrph_list()[e_posR].midasi)
                kihonR_b,kihonR_f,hinshiR_b,hinshiR_f=getBehindFrontNMorphenesByKNP(knprslt,s_idR,e_idR,n) #この辺途中
                kihon_kakariR_f,hinshi_kakariR_f=getBehindFrontNMorphenesKakariByKNP(knprslt,s_idR,e_idR,n)
                tmpdata={"termL":termL[0],"termR":termR[0],"termLpos":str(termL[1][0])+","+str(termL[1][1])+","+str(termL[1][2]),"termRpos":str(termR[1][0])+","+str(termR[1][1])+","+str(termR[1][2])}
                """
                tmpdata["kihonL_before_appear"]=(kihonL_b)
                tmpdata["kihonL_front_appear"]=(kihonL_f)
                tmpdata["hinshiL_before_appear"]=(hinshiL_b)
                tmpdata["hinshiL_front_appear"]=(hinshiL_f)
                tmpdata["kihonL_kakari_front_appear"]=(kihon_kakariL_f)
                tmpdata["hinshiL_kakari_front_appear"]=(hinshi_kakariL_f)
                tmpdata["kihonR_before_appear"]=(kihonR_b)
                tmpdata["kihonR_front_appear"]=(kihonR_f)
                tmpdata["hinshiR_before_appear"]=(hinshiR_b)
                tmpdata["hinshiR_front_appear"]=(hinshiR_f)
                tmpdata["kihonR_kakari_front_appear"]=(kihon_kakariR_f)
                tmpdata["hinshiR_kakari_front_appear"]=(hinshi_kakariR_f)
                """
                #extend_feature_vector_rel(tmpdata,termL[0],kihonL_b,kihonL_f,hinshiL_b,hinshiL_f,kihon_kakariL_f,hinshi_kakariL_f,termR[0],kihonR_b,kihonR_f,hinshiR_b,hinshiR_f,kihon_kakariR_f,hinshi_kakariR_f) #この辺途中
                #extend_feature_vector_kaku_rel(tmpdata,termL[1][1],e_posL,knp_results[i-1]) # 格の種類　左
                #extend_feature_vector_kaku_rel(tmpdata,termR[1][1],e_posR,knp_results[i-1])#右
                #extend_feature_vector_kakarinum_rel(tmpdata,termL[0],termL[1][1],e_posL,termR[0],termR[1][1],e_posR,knp_results[i-1]) # 係り受け数
                #extend_feature_vector_kakaritype_rel(tmpdata,termR[1][1],e_posR,knp_results[i-1]) # 係り受けのタイプ
                feature_datas.append(tmpdata)
            if i+1!=len(terms_list): #次の文
                #print("next sentence")
                #print(list(terms_list)[i+1])
                for termR in list(terms_list)[i+1]:
                    print(termL[0],"->",termR[0])
                    s_posR=termR[1][1]-done_mrph_num_next
                    e_posR=termR[1][1]-done_mrph_num_next
                    if isSameTerm(termL,termR):
                        continue
                    print(termL[0],"->",termR[0])
                    s_posR=termR[1][1]-done_mrph_num
                    e_posR=termR[1][1]-done_mrph_num
                    sec_numR=termR[1][0]
                    #単語が含まれているknp解析結果を取得
                    if sec_numR==0:
                        knprslt=knp_results[0][0]
                        s_idR=termR[1][1]
                    else:
                        #print(term,e_pos,":")
                        for h_i,head in enumerate(head_morph_ids):
                            if e_posR<head:
                                #print(e_pos,head)
                                knprslt=knp_results[1][h_i-1]
                                h=head_morph_ids[h_i-1]
                                break
                        s_idR=e_posR-h#その文での形態素id
                        #print(term,knprslt.mrph_list()[s_id].midasi,s_id,h)
                    e_idR=s_idR
                    tmp_term_len=len(mecab_result_list[sec_numR][e_posR][0])#e_pos求める
                    while tmp_term_len!=len(termR[0]):
                        #print(termR[0])
                        #print(" ",knp_results[i].mrph_list()[e_posR].midasi)
                        tmp_term_len+=len(mecab_result_list[sec_numR][e_posR+1][0])
                        e_posR+=1
                        e_idR+=1
                    #print(termR[1][1])
                    #print(termL[0]," ",termR[0]," ",knpresult.mrph_list()[s_posR].midasi," ",knp_results[i].mrph_list()[e_posR].midasi)
                    kihonR_b,kihonR_f,hinshiR_b,hinshiR_f=getBehindFrontNMorphenesByKNP(knprslt,s_idR,e_idR,n) #この辺途中
                    kihon_kakariR_f,hinshi_kakariR_f=getBehindFrontNMorphenesKakariByKNP(knprslt,s_idR,e_idR,n)
                    tmpdata={"termL":termL[0],"termR":termR[0],"termLpos":str(termL[1][0])+","+str(termL[1][1])+","+str(termL[1][2]),"termRpos":str(termR[1][0])+","+str(termR[1][1])+","+str(termR[1][2])}
                    """
                    tmpdata["kihonL_before_appear"]=(kihonL_b)
                    tmpdata["kihonL_front_appear"]=(kihonL_f)
                    tmpdata["hinshiL_before_appear"]=(hinshiL_b)
                    tmpdata["hinshiL_front_appear"]=(hinshiL_f)
                    tmpdata["kihonL_kakari_front_appear"]=(kihon_kakariL_f)
                    tmpdata["hinshiL_kakari_front_appear"]=(hinshi_kakariL_f)
                    tmpdata["kihonR_before_appear"]=(kihonR_b)
                    tmpdata["kihonR_front_appear"]=(kihonR_f)
                    tmpdata["hinshiR_before_appear"]=(hinshiR_b)
                    tmpdata["hinshiR_front_appear"]=(hinshiR_f)
                    tmpdata["kihonR_kakari_front_appear"]=(kihon_kakariR_f)
                    tmpdata["hinshiR_kakari_front_appear"]=(hinshi_kakariR_f)
                    """
                    #extend_feature_vector_rel(tmpdata,termL[0],kihonL_b,kihonL_f,hinshiL_b,hinshiL_f,kihon_kakariL_f,hinshi_kakariL_f,termR[0],kihonR_b,kihonR_f,hinshiR_b,hinshiR_f,kihon_kakariR_f,hinshi_kakariR_f) #この辺途中
                    #extend_feature_vector_joshi_rel(tmpdata,s_posL,e_posL,knp_results[i-1]) # 前後の助詞　左
                    #extend_feature_vector_joshi_rel(tmpdata,s_posR,e_posR,knp_results[i])#右
                    # 格の種類
                    # 係り受け数
                    # 係り受けのタイプ
                    feature_datas.append(tmpdata)
        if i>0:
            done_mrph_num+=len(knp_results[1][i-1].mrph_list())
    return feature_datas
            

def extend_feature_vector_joshi_rel(feature_list,s_pos,e_pos,knp_results): # 前後の助詞の種類
    exlistL=[]
    exlistR=[]
    with open("./data/bow/JOSHI.txt","r")as f:
        for line in f.readlines():
            bunrui,midasi=line.split("\t")
            if s_pos-1>0:
                #print(" ",knp_results.mrph_list()[s_pos].midasi)
                if knp_results.mrph_list()[s_pos-1].bunrui==bunrui and knp_results.mrph_list()[s_pos-1].midasi==midasi:
                    exlistL.append("1.0")
                else:
                    exlistL.append("0.0")
            else:
                exlistL.append("0.0")
            if e_pos+1<len(knp_results.mrph_list()):
                if knp_results.mrph_list()[e_pos+1].bunrui==bunrui and knp_results.mrph_list()[e_pos+1].midasi==midasi:
                    exlistR.append("1.0")
                else:
                    exlistR.append("0.0")
            else:
                exlistR.append("0.0")
    feature_list.extend(exlistL)
    feature_list.extend(exlistR)
                

def extend_feature_vector_kaku_rel(feature_list,s_pos,e_pos,knp_results): # 格の種類
    a=1

def extend_feature_vector_kakarinum_rel(feature_list,termL,s_posL,e_posL,termR,s_posR,e_posR,knp_results): # 係り受け数
    termL_mrph_id=(knp_results.mrph_list()[s_posL].mrph_id,knp_results.mrph_list()[e_posL].mrph_id)
    termR_mrph_id=(knp_results.mrph_list()[s_posR].mrph_id,knp_results.mrph_list()[e_posR].mrph_id)
    termL_bnst_id=(-1,-1)
    termR_bnst_id=(-1,-1)
    for bnst in  knp_results.bnst_list():
        for mrph in bnst.mrph_list():
            if mrph.id==termL_mrph_id[0]:
                termL_bnst_id[0]=bnst.bnst_id
            if mrph.id==termL_mrph_id[1]:
                termL_bnst_id[1]=bnst.bnst_id
            if mrph.id==termR_mrph_id[0]:
                termR_bnst_id[0]=bnst.bnst_id
            if mrph.id==termR_mrph_id[1]:
                termR_bnst_id[1]=bnst.bnst_id
    kakarinum=0        

def extend_feature_vector_kakaritype_rel(feature_list,s_pos,e_pos,knp_results): # 係り受けのタイプ
    a=1
                    
def extend_feature_vector_rel(feature_dict,termL,kihonL_b,kihonL_f,hinshiL_b,hinshiL_f,kihon_kakariL_f,hinshi_kakariL_f,termR,kihonR_b,kihonR_f,hinshiR_b,hinshiR_f,kihon_kakariR_f,hinshi_kakariR_f): # 単語ベクトルの素性
    components_kihonL,components_hinshiL=get_term_components(termL)
    components_kihonR,components_hinshiR=get_term_components(termR)
    #General
    extend_feature_vector_BoW(feature_dict,components_hinshiL,"hinshi","own_hinshiL_bow")#自身
    extend_feature_vector_BoW(feature_dict,hinshiL_b,"hinshi","hinshiL_b_bow")#周辺の品詞b
    extend_feature_vector_BoW(feature_dict,hinshiL_f,"hinshi","hinshiL_f_bow")#周辺の品詞f
    extend_feature_vector_BoW(feature_dict,hinshi_kakariL_f,"hinshi","hinshi_kakariR_f_bow")#周辺の品詞f_kakari
    extend_feature_vector_BoW(feature_dict,components_hinshiR,"hinshi","own_hinshiR_bow")#自身
    extend_feature_vector_BoW(feature_dict,hinshiR_b,"hinshi","hinshiR_b_bow")#周辺の品詞b
    extend_feature_vector_BoW(feature_dict,hinshiR_f,"hinshi","hinshiR_f_bow")#周辺の品詞f
    extend_feature_vector_BoW(feature_dict,hinshi_kakariR_f,"hinshi","hinshi_kakariR_f_bow")#周辺の品詞f_kakari
    #BOW
    extend_feature_vector_BoW(feature_dict,components_kihonL,"kihon","own_kihonL_bow")#自身
    extend_feature_vector_BoW(feature_dict,kihonL_b,"kihon","kihonL_b_bow")#周辺の基本形before
    extend_feature_vector_BoW(feature_dict,kihonL_f,"kihon","kihonL_f_bow")#周辺の基本形front
    extend_feature_vector_BoW(feature_dict,kihon_kakariL_f,"kihon","kihon_kakariL_f_bow")#周辺の基本形front_kakari
    extend_feature_vector_BoW(feature_dict,components_kihonR,"kihon","own_kihonR_bow")#自身
    extend_feature_vector_BoW(feature_dict,kihonR_b,"kihon","kihonR_b_bow")#周辺の基本形before
    extend_feature_vector_BoW(feature_dict,kihonR_f,"kihon","kihonR_f_bow")#周辺の基本形front
    extend_feature_vector_BoW(feature_dict,kihon_kakariR_f,"kihon","kihon_kakariR_f_bow")#周辺の基本形front_kakari
    #W2V
    extend_feature_vector_W2VSum(feature_dict,components_kihonL,"own_kihonL_w2v")#自身
    extend_feature_vector_W2VSum(feature_dict,kihonL_b,"kihonL_b_w2v")#周辺の基本形
    extend_feature_vector_W2VSum(feature_dict,kihonL_f,"kihonL_f_w2v")#周辺の品詞
    extend_feature_vector_W2VSum(feature_dict,kihon_kakariL_f,"kihon_kakariL_f_w2v")#周辺の品詞_kakari
    extend_feature_vector_W2VSum(feature_dict,components_kihonR,"own_kihonR_w2v")#自身
    extend_feature_vector_W2VSum(feature_dict,kihonR_b,"kihonR_b_w2v")#周辺の基本形
    extend_feature_vector_W2VSum(feature_dict,kihonR_f,"kihonR_f_w2v")#周辺の品詞
    extend_feature_vector_W2VSum(feature_dict,kihon_kakariR_f,"kihon_kakariR_f_w2v")#周辺の品詞_kakari

def getBehindFrontMorphemesJ(knp_results,s_pos,e_pos,n):
    kihon_b=[]
    kihon_f=[]
    hinshi_b=[]
    hinshi_f=[]
    """
    for i in range(s_pos-n,e_pos+n+1):
        if i>=s_pos and i<=e_pos:
            continue
        if i<0 or i>=len(knp_results.mrph_list()) or knp_results.mrph_list()[i].midasi=="":
            kihon.append("*")
            hinshi.append("*")
        else:
            kihon.append(knp_results.mrph_list()[i].midasi)
            hinshi.append(knp_results.mrph_list()[i].hinsi+"-"+knp_results.mrph_list()[i].bunrui)
    """
    for i in range(s_pos-n,s_pos):
        print(i)
    for i in range(e_pos+1,e_pos+n+1):
        print(i)
    sys.exit()
            
    return kihon,hinshi
        
def isSameTerm(term1,term2):
    if term1[0]==term2[0] and term1[1]==term2[1]:
        return True
    return False
                    
                    
def getPosIndex(pos,head_poses):
    for i,p in enumerate(head_poses,1):
        if i==len(head_poses) or pos<p:
            return p
    return -1
        

def writeFileJson(filename,feature_dict_list):
    #df=pd.io.json.json_normalize(feature_dict_list)
    #df.to_json(filename,force_ascii=False)
    with open(filename,"w")as f:
        json.dump(feature_dict_list,f,ensure_ascii=False)
        
def main():
    filename=sys.argv[1]
    if os.path.exists(filename[:-4]+"_feature_"+f_type+".txt"):
        sys.exit()
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #texts=dict{section title:body text}
    process_text_list,keywords=get_partof_text_list(texts,[1,1,1,0,0,0])#[title,abst,keywords,intro,conclusion,etc]
    tmp_fulltext,tmp_kw=get_partof_text_list(texts,[1,1,0,1,1,1])
    fulltext="".join(tmp_fulltext)
    #processJ(filename,process_text_list,process_text_list[0],process_text_list[1],keywords,fulltext) #通常

    #関係抽出素性用
    term_dic=processJ(filename,process_text_list,texts["title"],texts["abstract"],keywords,fulltext,True)
    features=createRelTrainData(filename,process_text_list,term_dic)
    writeFileJson(filename[:-4]+"_feature_rel.json",features)
    
if __name__=="__main__":
    main()
    

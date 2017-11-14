"""
実行時は引数に論文xmlファイルを指定
"""


#import termextract.mecab
#import termextract.core
import collections
import sys
import re
from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
import MeCab
import CaboCha

def processOneFile(filename):
    with open(filename)as f:
        words=f.readlines() #いっぺん全部読み込んでおく
    processTermExtract("".join(words))

def processTermExtract(text):
    """
    分かち書きテキストを引数に
    """
    freq=termextract.mecab.cmp_noun_dict(text)
    LR=termextract.core.score_lr(freq,ignore_words=termextract.mecab.IGNORE_WORDS,lr_mode=1,average_rate=1)
    term_imp_dic=termextract.core.term_importance(freq,LR)
    #print(term_imp_dic)
    #data_collection=collections.Counter(term_imp_dic)#大きい順にソート
    #for cmp_noun, value in data_collection.most_common():
    #    print(termextract.core.modify_agglutinative_lang(cmp_noun),value,sep="\t")
    return term_imp_dic

def processEachTerm(term_dic,mecab_result_list,n,titleabst_str=[]): #n:素性とするngramの範囲
    outputdata=[] #素性 リストのリスト returnする
    freq_list=getFreqList(term_dic)
    for term,pos_list in term_dic.items():
        #term=term.replace(" ","")
        in_title="0"
        in_abst="0"
        if term in titleabst_str[0]:
            in_title="1"
        if term in titleabst_str[1]:
            in_abst="1"
        freq=calcFreqFeature(freq_list,len(pos_list),10)#これ使うか単純に出現頻度そのまま入れるか
        tmpdata=[term,"freq="+str(freq),"in_title="+in_title,"in_abst="+in_abst]#対象語 出現回数 表題か 概要or序論か 前後ngramの基本形及び品詞
        #print("term : ",term)
        for pos in pos_list:
            #print("  pos : ",pos)
            e_pos=pos
            tmp_term_len=len(mecab_result_list[pos].split("\t")[0])
            while tmp_term_len!=len(term):#単語の末尾posを求める
                tmp_term_len+=len(mecab_result_list[e_pos+1].split("\t")[0])
                e_pos+=1
            kihon,hinshi=getBANgram(mecab_result_list,pos,e_pos,n)            
            #print("".join(kihon[:4]),term,"".join(kihon[4:]))
            tmpdata.insert(1,"pos="+str(pos))
            tmpdata.extend(appendFeatureLabel(kihon,n,"kihon"))
            tmpdata.extend(appendFeatureLabel(hinshi,n,"hinshi"))
            outputdata.append(tmpdata)
            tmpdata=[term,"freq="+str(freq),"in_title="+in_title,"in_abst="+in_abst]
    return outputdata

def appendFeatureLabel(target_list,n,label):#前後ngramのn
    pos=-n
    labeled_list=[]
    for i,elem in enumerate(target_list):
        labeled_list.append(label+"["+str(pos)+"]="+elem)
        pos+=1
        if pos==0:pos+=1
    return labeled_list
        
def getFreqList(term_dic):
    freq_list=[len(pos_list) for pos_list in term_dic.values()]
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

def processEachTermPair(term_dic,mecab_results,n=2,titleabst_str=""):
    """
    文中の二単語について
    TermExtract使わないverで作った
    """
    outputdata=[] #素性 リストのリスト
    for attrib,mecab_result in mecab_results.items():
        for i,morpheme in enumerate(mecab_result.split("\n")):
            appear=morpheme.split("\n")[0]
    
    return outputdata

def getBANgram(mecab_results,s_pos,e_pos,n): #s_pos,e_posはキーワード(複合語)のpos
    """
    前後ngramの基本形と品詞をそれぞれリストで返す
    """
    kihonkei=[]
    hinshi=[]
    for i in range (s_pos-n,e_pos+n+1):
        if i>=s_pos and i<=e_pos:
            continue
        if i<0 or i>=len(mecab_results) or mecab_results[i]=="":
            kihonkei.append("*")
            hinshi.append("*")
        else:
            #print("  "+mecab_results[i])
            if mecab_results[i]=="EOS":
                kihonkei.append("EOS")
                hinshi.append("EOS")
            else:
                tmp_kihon=mecab_results[i].split("\t")[1].split(",")[6]
                if tmp_kihon=="*":
                    kihonkei.append(mecab_results[i].split("\t")[0])
                else:
                    kihonkei.append(tmp_kihon)
                hinshi.append("-".join(mecab_results[i].split("\t")[1].split(",")[0:2]))
    return kihonkei,hinshi

def mecab(text):
    #m=MeCab.Tagger("")
    m=MeCab.Tagger("-d /home/momo/mecab/mecab-ipadic/") #記号がサ変接続になるのを修正した辞書※研究室PC
    m.parse("")
    return m.parse(text)#type:str

def removeUnderValueFromDict(target_dict,rmv_value):
    for k,v in list(target_dict.items()):
        #if v<rmv_value:
        if len(v)<rmv_value:
            del(target_dict[k])

def writeFile(filename,datas):
    with open(filename,"w")as f:
        for data in datas:
            f.write("\t".join(data)+"\n")
"""
def process_withTE(filename,texts):
    mecab_results={}
    for attrib,text in texts.items():
        mecab_result=mecab(text)
        mecab_results[attrib]=mecab_result
    mecab_result_joined="".join(mecab_results.values())
    term_imp_dic=processTermExtract("".join(mecab_result_joined)) # dict{word:imp}
    term_imp_dic=removeSpecificValueFromDict(term_imp_dic,1.0) # 指定重要度以下の語を除去
    if "title" in texts:
        title=texts["title"]
    else:
        title=""
    if "abstract" in texts:
        abst=texts["abstract"]
    else:
        abst=""
    #data=processEachTerm(term_imp_dic,mecab_results,3,[title,abst])#前後の語の分析 arg3:前後何gramまで素性にするか arg4:タイトル・アブスト素性用
    data=processEachTermPair(term_imp_dic,mecab_results,3,[title,abst])#
    writeFile(filename+".txt",data)
"""
    
def process(filename,text,title,abstract):
    """
    TermExtractを使わず、複合名詞や用語的表現(○○の△△)などのキーワードリストを作ってから関係抽出するver
    """
    term_dic={}#キーワードリスト key:キーワード value:出現位置リスト(lenで出現回数も求まる) i-1(形態素番号)かword_head_pos(文字番号)か要検討
    mecab_result=mecab(text)#mecab_resultは1行1形態素情報のstr
    #キーワード抽出
    partof_term="" #複合名詞抽出用tmp
    partof_termex="" #用語的表現抽出用tmp
    now_pos=0 #用語的表現抽出用 現在の場所 0:空 1:○○済 2:の済 3:△△済
    word_head_pos=0 #複合語の頭の位置
    nowread_head_pos=0 #現在処理している形態素の頭の位置
    tmp_i_term=0
    tmp_i_termex=0
    for i,morpheme in enumerate(mecab_result.split("\n")): #複合名詞の抽出と用語的表現の抽出はこのfor文中で別々に
        if morpheme not in ["EOS",""]:
            appear,infos=morpheme.split("\t")#出現形と品詞情報
            if(len(infos.split(","))==9):
                hinshi,hinshi_det1,hinshi_det2,hinshi_det3,katsuyo1,katsuyo2,base,read,pron=infos.split(",")
            else:
                hinshi,hinshi_det1,hinshi_det2,hinshi_det3,katsuyo1,katsuyo2,base=infos.split(",")
            #---複合名詞抽出処理---
            if(hinshi=="名詞"):
                if(len(partof_term)==0):
                    word_head_pos=nowread_head_pos
                    tmp_i_term=i
                partof_term+=appear
            elif(hinshi!="名詞" and len(partof_term)>0):
                if(partof_term in term_dic):
                    term_dic[partof_term].append(tmp_i_term)#(word_head_pos)
                else:
                    term_dic[partof_term]=[tmp_i_term]#word_head_pos]
                partof_term=""
            #---用語的表現抽出処理---
            if(hinshi=="名詞" and now_pos==0):#○○の部分
                partof_termex+=appear
                now_pos=1
                word_head_pos=nowread_head_pos
                tmp_i_termex=i
            elif(appear in ["の","を"] and now_pos==1):#「の」の部分
                partof_termex+="の"
                now_pos=2
            elif(hinshi!="名詞" and now_pos==2):#「の」までいいけど次に名詞が来ない場合
                partof_termex=""
                now_pos=0
            elif(hinshi=="名詞" and hinshi_det1=="サ変接続" and now_pos==2):#△△の部分
                partof_termex+=appear
                if(partof_termex in term_dic):
                    term_dic[partof_termex].append(tmp_i_termex)#word_head_pos)
                else:
                    term_dic[partof_termex]=[tmp_i_termex]#word_head_pos]
                partof_termex=""
                now_pos=0
            else:
                partof_termex=""
                now_pos=0
            #----------------------
            nowread_head_pos+=len(appear)
    removeUnderValueFromDict(term_dic,2)#任意の出現回数以下の単語を除去
    #for k,v in term_dic.items(): #表示テスト
    #    print(k,v)
    #print(len(term_dic))
    feature_data=processEachTerm(term_dic,list(filter(lambda x:x not in ["EOS",""],mecab_result.split("\n"))),4,[title,abstract])
    #for f in feature_data:
    #   print(f)
    writeFile(filename[:-4]+"_feature.txt",feature_data)

def split_texts(unit_texts):
    """
    ピリオドでsplitした方が後々やりやすい？
    """
    for attrib,texts in unit_texts.items():
        unit_texts[attrib]=re.split(r"\.|。|．",texts) #。も残したい？(素性になりうるかもなので)
        print(unit_texts[attrib])

def joinBodyText(texts):
    joined_text=""
    for attrib,text in texts.items():
        if attrib!="title":
            joined_text+=text
    return joined_text
        
def main():
    filename=sys.argv[1]
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #texts = dict{section title:body text}
    #split_texts(texts)
    joined_text=joinBodyText(texts).replace(" ","")
    #process_withTE(filename,texts)
    process(filename,joined_text,texts["title"],texts["abstract"])

if __name__=="__main__":
    main()

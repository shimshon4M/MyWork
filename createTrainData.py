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

def processEachTerm(term_dic,mecab_results,n=2,titleabst_str=""): #n:素性とするngramの範囲
    outputdata=[] #素性 リストのリスト
    for term,imp in term_dic.items():
        term=term.replace(" ","")
        imp=str(imp)
        in_title="0"
        in_abst="0"
        if term in titleabst_str[0]:
            in_title="1"
        if term in titleabst_str[1]:
            in_abst="1"
        tmpdata=[term,imp,in_title,in_abst]#対象語 TermExtractの重要度 表題か 概要or序論か 前後ngramの基本形及び品詞
        for attrib,mecab_result in mecab_results.items():
            mecab_result_spl=mecab_result.split("\n")
            for i in range(len(mecab_result_spl)):
                morph=mecab_result_spl[i]
                if morph=="EOS" or morph=="":
                    continue
                appear=morph.split("\t")[0]
                hinshi=morph.split("\t")[1]
                part_term=appear #部分一致のときに使う
                if term==appear: #完全一致の場合
                    #print(term)
                    kihon,hinshi=getBANgram(mecab_result_spl,i,i,n)
                    tmpdata.extend(kihon)
                    tmpdata.extend(hinshi)
                    #print(tmpdata)
                    outputdata.append(tmpdata)
                    tmpdata=[term,imp,in_title,in_abst]
                elif term.startswith(appear):#部分一致の場合
                    tmp_i=i+1
                    while term.startswith(part_term+mecab_result_spl[tmp_i].split("\t")[0]):
                        part_term+=mecab_result_spl[tmp_i].split("\t")[0]
                        tmp_i+=1
                        if part_term==term:
                            kihon,hinshi=getBANgram(mecab_result_spl,i,tmp_i-1,n)
                            tmpdata.extend(kihon)
                            tmpdata.extend(hinshi)
                            #print(tmpdata)
                            outputdata.append(tmpdata)
                            tmpdata=[term,imp,in_title,in_abst]
    return outputdata

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
                hinshi.append(mecab_results[i].split("\t")[1].split(",")[0])
    return kihonkei,hinshi

def mecab(text):
    #m=MeCab.Tagger("")
    m=MeCab.Tagger("-d /home/momo/mecab/mecab-ipadic/") #記号がサ変接続になるのを修正した辞書※研究室PC
    m.parse("")
    return m.parse(text)#結果はstr型

def removeSpecificValueFromDict(target_dict,rmv_value):
    for k,v in list(target_dict.items()):
        if v==rmv_value:
            del(target_dict[k])
    return target_dict

def writeFile(filename,datas):
    with open(filename,"w")as f:
        for data in datas:
            f.write("\t".join(data)+"\n")

def process_withTE(filename,texts):
    """
    TermExtractを使うver
    """
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

def process(filename,texts):
    """
    TermExtractを使わず、複合名詞や用語的表現(○○の△△)などのキーワードリストを作ってから関係抽出するver
    """
    mecab_results={}
    term_dic={}#キーワードリスト key:キーワード value:文番号リスト(lenで出現回数も求まる)
    for attrib,text in texts.items():
        mecab_result=mecab(text)#mecab_resultは1行1形態素情報のstr
        mecab_results[attrib]=mecab_result
        #キーワード抽出
        partof_term="" #複合名詞抽出用tmp
        partof_termex="" #用語的表現抽出用tmp
        now_pos=0 #用語的表現抽出用 現在の場所 0:空 1:○○済 2:の済 3:△△済
        for i,morpheme in enumerate(mecab_result.split("\n")): #複合名詞の抽出と用語的表現の抽出はこのfor文中で別々に
            print(morpheme)
            if morpheme not in ["EOS",""]:
                appear,infos=morpheme.split("\t")#出現形と品詞情報
                if(len(infos.split(","))==9):
                    hinshi,hinshi_det1,hinshi_det2,hinshi_det3,katsuyo1,katsuyo2,base,read,pron=infos.split(",")
                else:
                    hinshi,hinshi_det1,hinshi_det2,hinshi_det3,katsuyo1,katsuyo2,base=infos.split(",")
                #---複合名詞抽出処理---
                if(hinshi=="名詞"):
                    partof_term+=appear
                elif(hinshi!="名詞" and len(partof_term)>0):
                    if(partof_term in term_dic):term_dic[partof_term].append((attrib,i))
                    else:term_dic[partof_term]=[(attrib,i)]
                    partof_term=""
                #---用語的表現抽出処理---
                if(hinshi=="名詞" and now_pos==0):#○○の部分
                    partof_termex+=appear
                    now_pos=1
                elif(appear in ["の","を"] and now_pos==1):#「の」の部分
                    partof_termex+="の"
                    now_pos=2
                elif(hinshi!="名詞" and now_pos==2):#「の」までいいけど次に名詞が来ない場合
                    partof_termex=""
                    now_pos=0
                elif(hinshi=="名詞" and hinshi_det1=="サ変接続" and now_pos==2):#△△の部分
                    partof_termex+=appear
                    if(partof_termex in term_dic):term_dic[partof_termex].append((attrib,i))
                    else:term_dic[partof_termex]=[(attrib,i)]
                    partof_termex=""
                    now_pos=0
                #----------------------
    remove_terms=[term for term,appear_pos in term_dic.items() if len(appear_pos)<2]#任意の出現回数以下のものは除く
    for rmterm in remove_terms:
        term_dic.pop(rmterm)
    for k,v in term_dic.items():
        print(k,v)
    print(len(term_dic))
    if "title" in texts:
        title=texts["title"]
    else:
        title=""
    if "abstract" in texts:
        abst=texts["abstract"]
    else:
        abst=""
    #data=processEachTermPair(term_dic,mecab_results,4,[title,abst])#単語ペアについて分析して素性作成 arg3:前後何gramまで素性にするか arg4:タイトル・アブスト文字列リスト
    #writeFile(filename+".txt",data)

def split_texts(unit_texts):
    """
    ピリオドでsplitした方が後々やりやすい？
    """
    for attrib,texts in unit_texts.items():
        unit_texts[attrib]=re.split(r"\.|。|．",texts) #。も残したい？(素性になりうるかもなので)
        print(unit_texts[attrib])
    
def main():
    filename=sys.argv[1]
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #texts = dict{section title:body text}
    split_texts(texts)
    #process_withTE(filename,texts)
    #process(filename,texts)

    
if __name__=="__main__":
    main()

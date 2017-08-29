import termextract.mecab
import termextract.core
import collections
import sys
from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
import MeCab

def processOneFile(filename):
    with open(filename)as f:
        words=f.readlines() #いっぺん全部読み込んでおく
    processTermExtract("".join(words))

"""
分かち書きテキストを引数とする
"""
def processTermExtract(text):
    freq=termextract.mecab.cmp_noun_dict(text)
    LR=termextract.core.score_lr(freq,ignore_words=termextract.mecab.IGNORE_WORDS,lr_mode=1,average_rate=1)
    term_imp_dic=termextract.core.term_importance(freq,LR)
    #print(term_imp_dic)
    #data_collection=collections.Counter(term_imp_dic)#大きい順にソート
    #for cmp_noun, value in data_collection.most_common():
    #    print(termextract.core.modify_agglutinative_lang(cmp_noun),value,sep="\t")
    return term_imp_dic

def processEachTerm(term_dic,mecab_results,n=2): #n:素性とするngramの範囲
    outputdata=[] #素性 リストのリスト
    for term,imp in term_dic.items():
        term=term.replace(" ","")
        imp=str(imp)
        tmpdata=[term,imp]#対象語 TermExtractの重要度 表題か 概要or序論か 前後ngramの基本形及び品詞
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
                    tmpdata=[term,imp]
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
                            tmpdata=[term,imp]
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
    m=MeCab.Tagger("")
    m.parse("")
    return m.parse(text)

def removeSpecificValueFromDict(target_dict,rmv_value):
    for k,v in list(target_dict.items()):
        if v==rmv_value:
            del(target_dict[k])
    return target_dict

def writeFile(filename,datas):
    with open(filename,"w")as f:
        for data in datas:
            f.write("\t".join(data)+"\n")

if __name__=="__main__":
    filename=sys.argv[1]
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #dict{section title:body text}
    mecab_results={}
    for attrib,text in texts.items():
        mecab_result=mecab(text)
        mecab_results[attrib]=mecab_result
    mecab_result_joined="".join(mecab_results.values())
    term_imp_dic=processTermExtract("".join(mecab_result_joined)) # dict{word:imp}
    term_imp_dic=removeSpecificValueFromDict(term_imp_dic,1.0) # 指定重要度以下の語を除去
    data=processEachTerm(term_imp_dic,mecab_results,3)#前後の語の分析 第3引数は前後何gramまで素性にするか
    writeFile(filename+".txt",data)

"""
実行時は引数に論文xmlファイルを指定
"""

import collections
import sys
import re
from utils import get_files
import xml.etree.ElementTree as ET
from xmlAnalyzer import removeTags
import MeCab
import CaboCha

f_type="BoW"

def processEachTerm(term_dic,mecab_result_list,n,titleabst_str=[]): #n:素性とするngramの範囲
    """
    各語に対する素性抽出処理
    素性データは[対象語,出現場所pos,出現頻度,1文字か,タイトルに含まれるか,アブストに含まれるか,前後n形態素基本形列挙,前後n形態素品詞列挙,基本形ベクトル化,品詞ベクトル化]
    """
    outputdata=[] #素性 リストのリスト returnする
    freq_list=getFreqList(term_dic)
    for term,pos_list in term_dic.items():
        #term=term.replace(" ","")
        in_title="0.0"
        in_abst="0.0"
        if term in titleabst_str[0]:
            in_title="1.0"
        if term in titleabst_str[1]:
            in_abst="1.0"
        freq=calcFreqFeature(freq_list,len(pos_list),10)#これ使うか単純に出現頻度そのまま入れるか
        is_uni="0.0"
        if len(term)==1:
            is_uni="1.0"
        digit_rate=str(digit_num_per_term(term))
        alpha_rate=str(alpha_num_per_term(term))
        tmpdata=[term,is_uni,digit_rate,alpha_rate,in_title,in_abst]
        #print("term : ",term)
        for pos in pos_list:
            #print("  pos : ",pos)
            e_pos=pos
            tmp_term_len=len(mecab_result_list[pos].split("\t")[0])
            while tmp_term_len!=len(term):#単語の末尾posを求める
                tmp_term_len+=len(mecab_result_list[e_pos+1].split("\t")[0])
                e_pos+=1
            kihon,hinshi=getBehindFrontNMorphenes(mecab_result_list,pos,e_pos,n)            
            #print("".join(kihon[:4]),term,"".join(kihon[4:]))
            tmpdata.insert(1,str(pos))
            tmpdata.insert(2,str(2+n*2*2+1))#素性が始まる場所
            tmpdata[3:3]=(hinshi)
            tmpdata[3:3]=(kihon)
            #extend_feature_vector(tmpdata,term,kihon,hinshi,"BoW")#ベクトルの作り方選択
            extend_feature_vector(tmpdata,term,kihon,hinshi,f_type)
            outputdata.append(tmpdata)
            tmpdata=[term,is_uni,digit_rate,alpha_rate,in_title,in_abst]
    return outputdata

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

def extend_feature_vector(feature_list,term,kihon,hinshi,vec_type):
    components_kihon,components_hinshi=get_term_components(term)
    if vec_type=="BoW":
        extend_feature_vector_BoW(feature_list,components_kihon,"kihon")#自身
        extend_feature_vector_BoW(feature_list,components_hinshi,"hinshi")#自身
        extend_feature_vector_contains_NO(feature_list,term)#"○○の△△"か
        extend_feature_vector_BoW(feature_list,kihon,"kihon")#周辺の基本形
        extend_feature_vector_BoW(feature_list,hinshi,"hinshi")#周辺の品詞
    elif vec_type=="posBoW":
        extend_feature_vector_posBoW(feature_list,components_kihon,"kihon")#自身
        extend_feature_vector_posBoW(feature_list,components_hinshi,"hinshi")#自身
        extend_feature_vector_contains_NO(feature_list,term)#"○○の△△"か
        extend_feature_vector_posBoW(feature_list,kihon,"kihon")#周辺の基本形
        extend_feature_vector_posBoW(feature_list,hinshi,"hinshi")#周辺の品詞

def extend_feature_vector_contains_NO(feature_list,term):
    mecab_results=mecab(term).split("\n")
    if "の\t助詞,連体化,*,*,*,*,の,ノ,ノ" in mecab_results:
        #print("contain")
        feature_list.append("1.0")
    else:
        #print("not contain")
        feature_list.append("0.0")

def get_term_components(term):
    kihon=[]
    hinshi=[]
    mecab_results=mecab(term).split("\n")
    if mecab_results[0].split("\t")[1].split(",")[6]=="*":
        kihon.append(mecab_results[0].split("\t")[0])
    else:
        kihon.append(mecab_results[0].split("\t")[1].split(",")[6])
    if mecab_results[-3].split("\t")[1].split(",")[6]=="*":
        kihon.append(mecab_results[-3].split("\t")[0])
    else:
        kihon.append(mecab_results[-3].split("\t")[1].split(",")[6])
    hinshi.extend(["-".join(mecab_results[0].split("\t")[1].split(",")[0:2]),"-".join(mecab_results[-3].split("\t")[1].split(",")[0:2])])
    #print(kihon,hinshi)
    return kihon,hinshi

def extend_feature_vector_BoW(feature_list,extend_list,vec_type):
    """
    出現頻度を考慮しない単純なBoW(前後n形態素を見るがその位置情報は不保持)
    """
    if vec_type=="kihon":
        with open("./data/bow/df_list_0.4.txt","r")as f:
                for line in f.readlines():
                    word=line.split("\t")[0]
                    if word in extend_list:
                        feature_list.append("1.0")
                    else:
                        feature_list.append("0.0")
    elif vec_type=="hinshi":
        with open("./data/bow/HINSHI.txt","r")as f:
                for word in f.readlines():
                    if word.strip() in extend_list:
                        feature_list.append("1.0")
                    else:
                        feature_list.append("0.0")


def extend_feature_vector_posBoW(feature_list,extend_list,vec_type):
    """
    出現順序を考慮したBoW(長さはn(前後)*次元数になる)
    """
    if vec_type=="kihon":
        for ex_elem in extend_list:
            with open("./data/bow/df_list_0.4.txt","r")as f:
                for line in f.readlines():
                    word=line.split("\t")[0].strip()
                    if word==ex_elem:
                        feature_list.append("1.0")
                    else:
                        feature_list.append("0.0")
    elif vec_type=="hinshi":
        for ex_elem in extend_list:
            with open("./data/bow/HINSHI.txt","r")as f:
                for word in f.readlines():
                    if word.strip()==ex_elem:
                        feature_list.append("1.0")
                    else:
                        feature_list.append("0.0")

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

def getBehindFrontNMorphenes(mecab_results,s_pos,e_pos,n): #s_pos,e_posはキーワード(複合語)のpos
    """
    前後n形態素の基本形と品詞をそれぞれリストで返す
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
                #hinshi.append(mecab_results[i].split("\t")[1].split(",")[0])
                hinshi.append("-".join(mecab_results[i].split("\t")[1].split(",")[0:2]))
    return kihonkei,hinshi

def mecab(text):
    """
    引数strに対してmecab実行、結果strを返す
    """
    #m=MeCab.Tagger("")
    m=MeCab.Tagger("-d /home/momoi/mecab/mecab-ipadic/") #記号がサ変接続になるのを修正した辞書※研究室PC:momo 自宅PD:momoi
    m.parse("")
    return m.parse(text)#type:str

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
            
def process(filename,text,title,abstract):
    """
    メイン処理
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
            elif(hinshi=="名詞" and now_pos==1):
                partof_termex+=appear
            elif(appear in ["の","を"] and now_pos==1):#「の」の部分
                partof_termex+="の"
                now_pos=2
            elif(hinshi!="名詞" and now_pos==2):#「の」までいいけど次に名詞が来ない場合
                partof_termex=""
                now_pos=0
            elif(hinshi=="名詞" and hinshi_det1!="サ変接続" and now_pos==2):
                partof_termex+=appear
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
    #removeUnderValueFromDict(term_dic,2)#任意の出現回数以下の単語を除去
    #remove_later_pos_terms(term_dic,1)#pos以降にしか出現しない語を除去(タイトル・アブストのみ分析するとき用)
    #for k,v in term_dic.items(): #表示テスト
    #    print(k,v)
    #print(len(term_dic))
    feature_data=processEachTerm(term_dic,list(filter(lambda x:x not in ["EOS",""],mecab_result.split("\n"))),4,[title,abstract])
    #for f in feature_data:
    #   print(f)
    writeFile(filename[:-4]+"_feature_"+f_type+".txt",feature_data)
    
def split_texts(unit_texts):
    """
    ピリオドでsplitした方が後々やりやすい？
    """
    for attrib,texts in unit_texts.items():
        unit_texts[attrib]=re.split(r"\.|。|．",texts) #。も残したい？(素性になりうるかもなので)
        print(unit_texts[attrib])

def join_body_text(texts,join_section_pattern):
    """
    join_section_patternは[a,b,c,d,e]の5要素リスト
    a==1->title b==1->abstract c==1->序論 d==1->結論 e==1->本文 をjoined_textに含む
    """
    joined_text=""
    for attrib,text in texts.items():
        if attrib=="title" and join_section_pattern[0]==1:
            joined_text+=get_section_text(texts,"title")
            joined_text+="."
        elif attrib=="abstract" and join_section_pattern[1]==1:
            joined_text+=get_section_text(texts,"abstract")
        elif attrib not in ["title","abstract"] and join_section_pattern[2]==1:
            joined_text+=text.replace(" ","")
    return joined_text

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
    for attrib,text in texts.items():
        if section_type=="intro" and attrib in ["はじめに","序論","まえがき","はしがき"]:
            return text.replace(" ","")
        elif section_type=="conclusion" and attrib in ["おわりに","終わりに","結論","結論と今後の課題","結論および今後の課題","むすび","結び","まとめ","まとめと今後の課題","まとめと今後の方針","まとめ,及び今後の課題","まとめと今後の研究","あとがき"]:
            return text.replace(" ","")
    return ""
    

def main():
    filename=sys.argv[1]
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root) #texts=dict{section title:body text}                   
    joined_text_part=join_body_text(texts,[1,1,0,0,0])#[title,abst,intro,conclusion,etc]
    #joined_text_all=join_body_text_all(texts)
    process(filename,joined_text_part,texts["title"],texts["abstract"])
    
if __name__=="__main__":
    main()
    

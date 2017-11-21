#coding:utf-8

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re
from collections import OrderedDict

OBRACK={"BOX":"[","CURLY":"{","NOBRACK":""}
CBRACK={"BOX":"]","CURLY":"}","NOBRACK":""}

BOX_CURLY_COMMANDS=["cite"
                    #,"documentclass"
                    #,"documentstyle"
                    #,"usepackage"
] #command[]{} いらない？
CURLIES_COMMANDS=[
    #"Volume"
    #,"Number"
    #,"Month"
    #,"Year"
    #,"received"
    #,"revised"
    #,"accepted"
    #,"setcounter"
    "title"      #言語指定なし題目(昔のだとこれ？)
    ,"author"     #言語指定なし著者(〃)
    ,"jtitle"     #日本語題目
    ,"jauthor"    #日本語著者
    ,"jabstract"  #日本語概要
    ,"jkeywords"  #日本語キーワード
    #,"etitle"     #英語題目
    #,"eauthor"    #英語著者
    #,"eabstract"  #英語概要
    #,"ekeywords"  #英語キーワード
    #,"headauthor" #主著者
    #,"headtitle"  #主題目
    #,"mbox"
    #,"caption"    #表・図題
    #,"input"      #外部からのデータ入力 表を作るときなどに使用
    ,"addtolength"#表の設定か何か？
    ,"notice"
    #,"bibliographystyle" #
    #,"bioauthor"    #著者情報
    ,"bibitem"      #参考文献１件に関するブロック
]#command{}*
BOX_COMMANDS=[
    "item"
]
REF_COMMANDS=[
    "affiref"     #所属参照 「†」
    ,"affilabel"  #所属被参照 「†○○大学」
    ,"footnote"   #フッタ参照 「*」
    ,"footnotetext" #〃
    ,"ref"        #論文内セクション参照 「*節」
    ,"cite"       #引用 「[*]」
    ,"citeA"
    ,"label"      #参照じゃないけど読み飛ばすからとりあえず
    ,"bibliographystyle"
    ,"bibliography"
    ,"biotitle"
    ,"bioreceived"
    ,"biorevised"
    ,"bioaccepted"
    ,"caption"
    ,"setcounter"
    ,"hspace"
    ,"mbox"
    ,"input"
    ,"caption"
    #,"appendix"
    ,"vspace"
]#command{}参照、引用ほか 直後にくるカッコ内は無視する
TREE_COMMANDS=[
    "tree" #command[]{}
    ,"leaf"#command{}
]#ツリー 中身は無視する
SECTION_COMMANDS=[
    "section"           # 大節
    ,"subsection"       # 小節
    ,"subsubsection"    # 小小節
]#command{}*...章構造を作る
labelCommands=["label"]
pbCommands=["pagebreak"]
BEGIN_COMMANDS=[
    "begin"
]
END_COMMANDS=[
    "end"
]
boxAndCurlyBracketCommands=["usepackage"]# 後ろに{}または[]{}がくるもの
tmpCommands=[
    "item"   #列挙　「●〜 (1)〜」
    ,"acknowledgment" #謝辞
]# 後ろに文字のみがくる 論文の形式を作る
DECORATE_COMMANDS=[
    "Jem"
    ,"BCAY"
    ,"BEDS"
    ,"Bem"
    ,"BPGS"
    ,"Bbf"
    ,"underline"
]# 文字の装飾 後ろには文字だけまたは{}？
ULINE_COMMANDS=[#underlineだけじゃないね
    "underline"
    ,"text"
    ,"textrm"
    ,"texttt"
    ,"textit"
]
BF_COMMANDS=[
    "bf"
]
nonCommands=[
    "maketitle"
    ,"Jetal"
    ,"protect"
    ,"biodate"
    ,"footmark"
]# 何も装飾せずコマンドだけのもの
SYMBOL_COMMANDS=[
    "BBOP"  # (
    ,"BBCP" # )
    ,"BBOQ" # "
    ,"BBCQ" # "
    ,"BBA"  # and
    ,"BBACOMMA"
    ,"JBA"  # ,
    ,"newblock" # 改行?
]#記号や文字に置換される
BEGINEND_TYPE=[
    "table"           #表
    ,"thebibliography" #参考文献の節
    ,"biography"       #著者情報
    ,"center"
    ,"tabular"
    ,"figure"
    ,"picture"
    ,"quote"
    ,"description"
    ,"equation"
    ,"array"
]#begin-endの種類 読み飛ばすもの
ITEM_TYPE=[
    "itemize"     # ●
    "enumerate"   # (1)(2)... (a)(b)...
]#列挙の種類
DEFINE_COMMANDS=[
    "unitlength"
]#コマンド=○○ サイズの指定など

is_begining=[]
sub_elements=[]

def main(filename):
    text=readFile(filename)
    xml_tree=analyze(text)
    writeFile(filename,xml_tree)

def readFile(filename):
    """
    texの読み込み
    改行詰めで全部つなげる
    空白も詰め
    """
    with open(filename,"r")as f:
        text=f.read()
    return text.replace("\n","")#.replace(" ","").replace("　","")

def writeFile(in_filename,xml_tree):
    """
    引数のElementTreeをtexファイル名+".xml"という名前のxmlで保存
    """
    pretty_string=minidom.parseString(ET.tostring(xml_tree,"utf-8")).toprettyxml(indent="  ")
    with open(in_filename+".xml","w")as f:
        f.write(pretty_string)

def analyze(text):
    """
    etreeを作るメイン作業
    """
    root=ET.Element("root") #xmlのroot
    read(text,root)
    createSubElementAll(root,text)
    return root

def read(text,root,brack_type="NOBRACK",read_body=True):
    """
    1文字ずつ読んで構文解析
    brack_type:括弧の種類(形)
    read_inner:括弧内を読むのか否か
    """
    if brack_type not in ["OBRACK","CBRACL","NOBRACK"] and text[0]!=OBRACK[brack_type]:
        return "",0#指定の括弧で始まらなければ空の読み取り文字列として返す(ここに入らないように作るけど)
    appear_open_brack=False#括弧の出現の有無
    appear_close_brack=False
    is_end_section=False #NOBRACKの場合は括弧の出現での範囲同定ができないのでこのフラグで管理
    read_text=""
    i=0
    while i<len(text):
        if len(is_begining)>0: #読み飛ばすべきbegin-end中での処理
            if text[i]=="\\":
                cmd,c_len=readCommand(text[i+1:])
                i+=c_len
                if cmd in END_COMMANDS:
                    b_type=text[i+2:].split("}",1)[0]#read(text[i+1:],root,"CURLY")
                    t_len=len(b_type)
                    i+=t_len+2
                    if b_type in is_begining:
                        is_begining.remove(b_type)
                elif cmd in BEGIN_COMMANDS:
                    b_type=text[i+2:].split("}",1)[0]#read(text[i+1:],root,"CURLY")
                    t_len=len(b_type)
                    i+=t_len+2
                    if b_type in BEGINEND_TYPE:
                        is_begining.append(b_type)
            i+=1
            continue
        if text[i]=="$":#andとか記号に使われる
            i+=1
            continue
        elif text[i]=="\\":#コマンドの始まり "\"
            cmd,c_len=readCommand(text[i+1:])#コマンドとその長さを得る
            i+=c_len
            #print(cmd)
            if cmd in BEGIN_COMMANDS:
                b_type,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                if b_type in BEGINEND_TYPE:
                    is_begining.append(b_type)
            elif cmd in BOX_CURLY_COMMANDS:#[]{}で出てくるものは不要なものしかない？
                txt,t_len=read(text[i+1:],root,"BOX")
                i+=t_len
                #read_text+=txt
                #read_text+=" "
                txt,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                #read_text+=txt
                #createSubElement(i,root,cmd,read_text)
            elif cmd in CURLIES_COMMANDS:
                txts=[]
                while text[i+1]=="{":
                    txt,t_len=read(text[i+1:],root,"CURLY")
                    i+=t_len
                    txts.append(txt)
                createSubElement(root,cmd," ".join(txts))
            elif cmd in BOX_COMMANDS:
                txt,t_len=read(text[i+1:],root,"BOX")
                i+=t_len
            elif cmd in SECTION_COMMANDS or cmd=="acknowledgment":
                tag,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                txt,t_len=read(text[i+1:],root,"NOBRACK")
                if txt=="":#スマートじゃないけどｗ
                    txt=" "
                if cmd in SECTION_COMMANDS:
                    createSubElement(root,cmd,txt,key="title",value=tag)
                is_end_section=True
            elif cmd in REF_COMMANDS:
                txt,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
            elif cmd in BF_COMMANDS:
                #コマンド直前の"{"と被装飾文字列直後の"}"を除去　ゴリ押し
                read_text=read_text[0:-1]#{
                bf_text=text[i+2:].split("}",1)[0]#被修飾文字列
                read_text+=bf_text
                i+=len(bf_text)+2
            elif cmd in ULINE_COMMANDS:
                #txts=[]
                #while text[i+1]=="{":
                txt,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                #txts.append(txt)
                read_text+=txt
        else:#コマンドではない(本文を読む)場合
            if text[i]==OBRACK[brack_type]:
                appear_open_brack=True
            elif text[i]==CBRACK[brack_type]:
                appear_close_brack=True
            else:
                read_text+=text[i]
            if brack_type!="NOBRACK" and appear_open_brack and appear_close_brack:
                break
            elif brack_type=="NOBRACK" and is_end_section:
                break
        i+=1
    read_text=read_text.replace("{itemize}","").replace("{enumerate}","")#.replace(" ","")#.replace("}","") #暫定処置
    read_text=re.sub("{=\dmm}","",read_text)#unitlengthの処理　暫定
    return read_text,i+1
        
def createSubElement(root,tag,text,key=None,value=None):
    """
    受け取ったElementTreeのrootにサブElementをつける
    """
    """#その都度一つずつsubを追加していく場合
    sub=ET.SubElement(root,tag)
    if tag in SECTION_COMMANDS:
        sub.text=text[0:-1]#sectionだとなぜか後ろに1字余計に入っちゃうんで　暫定処置
    else:
        sub.text=text
    if key!=None and value!=None:
        sub.set(key,value)
    return sub#返す必要ない？>subの下にsubを作るときには使う？
    """
    #最後に一括でsubを追加する場合
    sub_elements.append({"tag":tag,"text":text,"key":key,"value":value})
    
def createSubElementAll(root,text):#従来手法だと順序崩れる＆subsub関係が保持できないので最後に一気につなげる
    info_parts=[]
    tmp_sections={}
    for elem in sub_elements:#順序の整理
        if elem.get("tag") in SECTION_COMMANDS:
            pos=text.find("section{"+elem.get("value")+"}")
            tmp_sections[pos]=elem
        else:
            info_parts.append(elem)
    sections=OrderedDict(sorted(tmp_sections.items(),key=lambda x:x[0]))

    for elem in info_parts:
        sub=ET.SubElement(root,elem.get("tag"))
        sub.text=elem.get("text").replace("{","").replace("}","").replace(" ","").replace("　","")#{}除去ゴリ押し
        if elem.get("key")!=None and elem.get("value")!=None:
            sub.set(elem.get("key"),elem.get("value"))

    for elem in sections.values():
        sub=ET.SubElement(root,elem.get("tag"))
        sub.text=elem.get("text")[0:-1].replace("{","").replace("}","").replace(" ","").replace("　","")
        if elem.get("key")!=None and elem.get("value")!=None:
            sub.set(elem.get("key"),elem.get("value"))
    
def isAlpha(s):
    """
    アルファベット(a-z A-Z)ならTrueを返す
    (普通のisalpha()だと日本語全角もTrueになってしまうので自作)
    """
    return re.compile(r"[a-zA-Z]").match(s)

def readCommand(text):
    """
    コマンドとその長さを返す
    """
    read_cmd=""
    for i in range(len(text)):#アルファベットである間読み続けることで判別
        if isAlpha(text[i]): #普通のisalpha()だと日本語全角文字もTrueになってまうので自作
            read_cmd+=text[i]
        else:
            break
    return read_cmd,i

if __name__=="__main__":
    main(sys.argv[1])

#coding:utf-8

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re

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

REF_COMMANDS=[
    "affiref"     #所属参照 「†」
    ,"affilabel"  #所属被参照 「†○○大学」
    ,"footnote"   #フッタ参照 「*」
    ,"footnotetext" #〃
    ,"ref"        #論文内セクション参照 「*節」
    ,"cite"       #引用 「[*]」
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
BEGINEND_COMMANDS=[
    "begin"
    ,"end"
] #この２つは独立させとく？
boxAndCurlyBracketCommands=["usepackage"]# 後ろに{}または[]{}がくるもの
tmpCommands=[
    "item"   #列挙　「●〜 (1)〜」
    ,"acknowledgment" #謝辞
]# 後ろに文字のみがくる 論文の形式を作る
DECORATE_COMMANDS=[
    "bf" #太字
    ,"Jem"
    ,"BCAY"
    ,"BEDS"
    ,"Bem"
    ,"BPGS"
    ,"Bbf"
]# 文字の装飾 後ろには文字だけまたは{}？
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
beginEndType=[
    "table"           #表
    "thebibliography" #参考文献の節
    "biography"       #著者情報
]#begin-endの種類
ITEM_TYPE=[
    "itemize"     # ●
    "enumerate"   # (1)(2)... (a)(b)...
]#列挙の種類

def main(filename):
    text=readFile(filename)#改行詰め
    xml_tree=analyze(text)
    writeFile(filename,xml_tree)

def readFile(filename):
    """
    texの読み込み
    改行詰めで全部つなげる
    """
    with open(filename,"r")as f:
        text=f.read()
    return text.replace("\n","")

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
    return root

def read(text,root,brack_type="NOBRACK",read_inner=False):
    """
    1文字ずつ読んで構文解析
    brack_type:括弧の種類(形)
    read_inner:括弧内を読むのか否か
    """
    if brack_type not in ["OBRACK","CBRACL","NOBRACK"] and text[0]!=OBRACK[brack_type]:
        return "",0#指定の括弧で始まらなければ空の読み取り文字列として返す(ここに入らないように作るけど)
    open_curly_brack_num=0
    close_curly_brack_num=0
    appear_open_brack=False#出現の有無 上記numでなくこっち使うか？
    appear_close_brack=False
    is_end_section=False #NOBRACKの場合は括弧の出現での範囲同定ができないのでこのフラグで管理
    is_up_begin=False
    read_text=""
    i=0
    while i<len(text):
        #read_text=""
        if text[i]=="$":#andとか記号に使われる
            i+=1
            continue
        elif text[i]=="\\":#コマンドの始まり "\"
            cmd,c_len=readCommand(text[i+1:])#コマンドとその長さを得る
            i+=c_len
            #print(cmd)
            if cmd in BOX_CURLY_COMMANDS:#[]{}で出てくるものは不要なものしかない？
                txt,t_len=read(text[i+1:],root,"BOX")
                i+=t_len
                #read_text+=txt
                #read_text+=" "
                txt,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                #read_text+=txt
                #createSubElement(root,cmd,read_text)
            elif cmd in CURLIES_COMMANDS:
                txts=[]
                while text[i+1]=="{":
                    txt,t_len=read(text[i+1:],root,"CURLY")
                    i+=t_len
                    txts.append(txt)
                createSubElement(root,cmd," ".join(txts))
            elif cmd in SECTION_COMMANDS or cmd=="acknowledgment":
                tag,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
                txt,t_len=read(text[i+1:],root,"NOBRACK")
                if txt=="":#スマートじゃないけどｗ
                    txt=" "
                createSubElement(root,cmd,txt,key="title",value=tag)
                is_end_section=True
            elif cmd in REF_COMMANDS:
                txt,t_len=read(text[i+1:],root,"CURLY")
                i+=t_len
            elif cmd in BEGINEND_COMMANDS:
                is_up_begin=not is_up_begin
        else:#コマンドではない(本文を読む)場合
            if text[i]==OBRACK[brack_type]:
                open_curly_brack_num+=1
                appear_open_brack=True
            elif text[i]==CBRACK[brack_type]:
                close_curly_brack_num+=1
                appear_close_brack=True
            else:
                read_text+=text[i]
            if brack_type!="NOBRACK" and appear_open_brack and appear_close_brack:#open_curly_brack_num==close_curly_brack_num: #NOBRCAKのときは括弧で判定できない
                break
            elif brack_type=="NOBRACK" and is_end_section:
                break
        i+=1
    read_text=read_text.replace("{itemize}","").replace("{enumerate}","")#.replace("}","") #暫定処置
    return read_text,i+1
        
def createSubElement(root,tag,text,key=None,value=None):
    """
    受け取ったElementTreeのrootにサブElementをつける
    """
    sub=ET.SubElement(root,tag)
    sub.text=text
    if key!=None and value!=None:
        sub.set(key,value)
    return sub#返す必要ない？>subの下にsubを作るときには使う
        

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

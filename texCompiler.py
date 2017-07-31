#!usr/bin/env python

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re

BOX_CURLY_COMMANDS=["documentclass"
                    ,"usepackage"
] #command[]{}
CURLIES_COMMANDS=[
    "Volume"
    ,"Number"
    ,"Month"
    ,"Year"
    ,"received"
    ,"revised"
    ,"accepted"
    ,"setcounter"
    ,"jtitle"     #日本語題目
    ,"jauthor"    #日本語著者
    ,"jabstract"  #日本語概要
    ,"jkeywords"  #日本語キーワード
    ,"etitle"     #英語題目
    ,"eauthor"    #英語著者
    ,"eabstract"  #英語概要
    ,"ekeywords"  #英語キーワード
    ,"headauthor" #主著者
    ,"headtitle"  #主題目
    ,"footnote"   #フッタ参照 「*」
    ,"ref"        #論文内セクション参照 「*節」
    ,"cite"       #引用 「[*]」
    ,"mbox"
    ,"caption"    #表・図題
    ,"input"      #外部からのデータ入力 表を作るときなどに使用
    ,"addtolength"#表の設定か何か？
    ,"notice"
    ,"bibliographystyle" #
    ,"bioauthor"  #著者情報
    ,"bibitem"      #参考文献１件に関するブロック
] #command{}*

OMIT_COMMANDS=[
    "affiref"    #所属参照 「†」
    ,"affilabel"  #所属被参照 「†○○大学」
]#参照、引用
SECTION_COMMANDS=[
    "section"           # 大節
    ,"subsection"       # 小節
    ,"subsubsection"    # 小小節
]#command{}*...章構造を作る
labelCommands=["label"]
pbCommands=["pagebreak"]
beginAndEndCommands=[
    "begin"
    ,"end"
] #この２つは独立させとく？
boxAndCurlyBracketCommands=["usepackage"]# 後ろに{}または[]{}がくるもの
tmpCommands=[
    "item"   #列挙　「●〜 (1)〜」
    ,"acknowledgment" #謝辞
]# 後ろに文字のみがくる 論文の形式を作る
decorateCommands=[
    "bf" #太字
    ,"Jem"
    ,"BCAY"
    ,"BEDS"
    ,"Bem"
    ,"BPGS"
    ,"Bbf"
]# 文字の装飾 後ろには文字だけまたは{}？
nonCommands=["maketitle","Jetal","protect","biodate"]# 何も装飾せずコマンドだけのもの
symbolCommands=[
    "BBOP"  # (
    ,"BBCP" # )
    ,"BBOQ" # "
    ,"BBCQ" # "
    ,"BBA"  # and
    ,"BBACOMMA"
    ,"JBA"  # ,
    ,"newblock" # 改行?
]#記号や文字に置換されるもの
beginEndType=[
    "table"           #表
    "thebibliography" #参考文献の節
    "biography"       #著者情報
]#begin-endの種類
itemType=[
    "itemize"     # ●
    "enumerate"   # (1)(2)... (a)(b)...
]#列挙の種類

def main(filename):
    text=readFile(filename)
    xml_tree=analyze(text)
    writeFile(xml_tree)

def readFile(filename):
    with open(filename,"r")as f:
        text=f.read()
    return text.replace("\n","")

def writeFile(xml_tree):
    pretty_string=minidom.parseString(ET.tostring(xml_tree,"utf-8")).toprettyxml(indent="  ")
    with open("text.xml","w")as f:
        f.write(pretty_string)

def analyze(text):
    root=ET.Element("root") #xmlのroot
    for i in range(len(text)):
        read_text=""
        if text[i]=="\\":
            cmd,c_len=readCommand(text[i+1:])
            i+=c_len
            #print(cmd)
            if cmd in BOX_CURLY_COMMANDS:
                txt,t_len=readText(text[i+1:],"BOX")
                i+=t_len
                read_text+=txt
                read_text+=" "
                txt,t_len=readText(text[i+1:],"CURLY")
                i+=t_len
                read_text+=txt
                createSubElement(root,cmd,read_text)
            elif cmd in CURLIES_COMMANDS:
                txts=[]
                while text[i+1]=="{":
                    txt,t_len=readText(text[i+1:],"CURLY")
                    i+=t_len
                    txts.append(txt)
                createSubElement(root,cmd," ".join(txts))
            elif cmd in SECTION_COMMANDS:
                tag,t_len=readText(text[i+1:],"CURLY")
                i+=t_len
                    
    return root
                
def createSubElement(root,tag,text,key=None,value=None):
    sub=ET.SubElement(root,tag)
    sub.text=text
    if key!=None and value!=None:
        sub.set(key,value)
    return sub
        

def readCommand(text):
    read_cmd=""
    for i in range(len(text)):
        if text[i].isalpha():# and text[i]!="{" and text[i]!="[":
            read_cmd+=text[i]
        else:
            break
    return read_cmd,i

def readText(text,brack_type=None):
    OBRACK={"BOX":"[","CURLY":"{"}
    CBRACK={"BOX":"]","CURLY":"}"}
    open_curly_brack_num=0
    close_curly_brack_num=0
    read_text=""
    if brack_type!=None and text[0]!=OBRACK[brack_type]: #指定の括弧で始まらなければ空の読み取り文字列として返す
        return "",0
    for i in range(len(text)):
        if text[i]==OBRACK[brack_type]:
            open_curly_brack_num+=1
        elif text[i]==CBRACK[brack_type]:
            close_curly_brack_num+=1
        elif text[i]=="\\": #未対応
            cmd,c_len=readCommand(text[i+1:])
            i+=c_len
            inner_read_text,t_len=readText(text[i+1:],"CURLY")
            i+=t_len
            read_text+=inner_read_text
        else:
            read_text+=text[i]
        if open_curly_brack_num==close_curly_brack_num:
            break
    return read_text,i+1

if __name__=="__main__":
    main(sys.argv[1])

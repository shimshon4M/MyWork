#!usr/bin/env python

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re

boxBracketCommands=["documentclass" #文献情報
                    ,"bibitem"      #参考文献１件に関するブロック
] #後ろに[]{}がくるもの
curlyBracketCommands=[
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
    ,"affiref"    #所属参照 「†」
    ,"affilabel"  #所属被参照 「†○○大学」
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
] #後ろに{}*がくるもの
curlyBracketAndTextCommands=[
    "section"           # 大節
    ,"subsection"       # 小節
    ,"subsubsection"    # 小小節
]# 後ろに{}と本文がくるもの(labelが入ることも) 章構造を作る
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
    compile(text)

def readFile(filename):
    with open(filename,"r")as f:
        text=f.read()
    return text.replace("\n","")

def compile(text):
    for i in range(len(text)):
        if text[i]=="\\":
            cmd,c_len,c_type=getCommand(text[i+1:])
            i+=c_len
            print(cmd)
                

def getCommand(text):
    cmd=""
    for i in range(len(text)):
        if text[i].isalpha():# and text[i]!="{" and text[i]!="[":
            cmd+=text[i]
        else:
            break
    return cmd,i+1,1#コマンドタイプ　その後の処理（カッコ内を読むかなど）を決める　今はとりあえず１

if __name__=="__main__":
    main(sys.argv[1])

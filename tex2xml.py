#coding:utf-8

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re
from collections import OrderedDict

is_begining=[]
sub_elements=[] #各セクションの情報を保持した辞書のリスト

def main(filename):
    text=readFile(filename)
    xml_tree=parse(text)
    #writeFile(filename,xml_tree)
    
def readFile(filename):
    """
    texファイルの読み込み
    改行詰めで全部つなげる？
    空白も詰める？
    """
    with open(filename,"r")as f:
        text=f.read()
    return text#.replace("\n","")#.replace(" ","").replace("　","")

def writeFile(in_filename,xml_tree):
    """
    引数のElementTreeをtexファイル名+".xml"という名前のxmlで保存
    """
    pretty_string=minidom.parseString(ET.tostring(xml_tree,"utf-8")).toprettyxml(indent="  ")
    with open(in_filename+".xml","w")as f:
        f.write(pretty_string)

def parse(tex_text):
    root=ET.Element("root") #xmlのroot
    pos=0
    wholepaper(text,pos)
    createSubElementAll(root,text)
   
def wholepaper(text,pos):
    pos=paperheader(text,pos)
    pos=body(text,pos)

def paperheader(text,pos):
    a=1

def paperstyle(text,pos):
    a=1

def paperinfo(text,pos):
    a=1

def documentclass(text,pos):
    a=1

def documentstyle(text,pos):
    a=1

def usepackage(text,pos):
    a=1

def setcounter(text,pos):
    a=1

def titile(text,pos):
    if text[pos:].startswith("\jtitle"):
        pos=jtitle(text,pos)
    elif text[pos:].startswith("\etitle"):
        pos=etitle(text,pos)
    return pos
        
def author(text,pos):
    if text[pos:].startswith("\jauthor"):
        pos=jauthor(text,pos)
    elif text[pos:].startswith("\eauthor"):
        pos=eauthor(text,pos)
    return pos

def abstract(tex,pos):
    if text[pos:].startswith("\jabstract"):
        pos=jabstract(text,pos)
    elif text[pos:].startswith("\eabstract"):
        pos=eabstract(text,pos)
    return pos

def keywords(text,pos):
    if text[pos:].startswith("\jkeywords"):
        pos=jkeywords(text,pos)
    elif text[pos:].startswith("\ekeywords"):
        pos=ekeywords(text,pos)
    return pos

def jtitle(text,pos):
    tmp_pos=pos
    pos+=len("\jtitle")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"jtitle",sent)
    return pos

def etitle(text,pos):
    tmp_pos=pos
    pos+=len("\etitle")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"etitle",sent)
    return pos

def jauthor(text,pos):
    tmp_pos=pos
    pos+=len("\jauthor")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"jauthor",sent)
    return pos

def eauthor(text,pos):
    tmp_pos=pos
    pos+=len("\eauthor")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"eauthor",sent)
    return pos

def jabstract(text,pos):
    tmp_pos=pos
    pos+=len("\jabstract")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"jabstract",sent)
    return pos

def eabstract(text,pos):
    tmp_pos=pos
    pos+=len("\eabstract")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"eabstract",sent)
    return pos

def jkeywords(text,pos):
    tmp_pos=pos
    pos+=len("\jkeywords")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"jkeywords",sent)
    return pos

def ekeywords(text,pos):
    tmp_pos=pos
    pos+=len("\ekeywords")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"ekeywords",sent)
    return pos

def affilabel(text,pos):
    a=1

def headtitle(text,pos):
    tmp_pos=pos
    pos+=len("\headtitle")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"headtitle",sent)
    return pos

def headauthor(text,pos):
    tmp_pos=pos
    pos+=len("\headauthor")
    sent,pos=sentence(text,pos)
    createSubElement(tmp_pos,"headauthor",sent)
    return pos
    
def body(text,pos):
    a=1

def sentence(text,pos):
    ret=text[pos]
    pos+=1
    while pos<len(text) and text[pos] not in ["\\"]:#文字である間読み続ける
        ret+=text[pos]
        pos+=1
    return ret,pos
    
def parse_tmp(text):
    """
    etreeに変換するメイン処理
    """
    root=ET.Element("root") #xmlのroot
    read(text)
    createSubElementAll(root,text)
    return root


def createSubElement(pos,tag,text,key=None,value=None):
    #最後に一括でsubを追加する場合
    sub_elements.append({"pos":pos,"tag":tag,"text":text,"key":key,"value":value})
    
def createSubElementAll(root,text):#従来手法だと順序崩れる＆subsub関係が保持できないので最後に一気につなげる
    info_parts=[]
    tmp_sections={}
    for elem in sub_elements:#順序の整理
        if elem.get("tag") in cm.SECTION_COMMANDS:
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
    
def is_alpha(s):
    """
    アルファベット(a-z A-Z)ならTrueを返す
    (普通のisalpha()だと日本語全角もTrueになってしまうので自作)
    """
    return re.compile(r"[a-zA-Z]").match(s)

def readCommand(text):
    """
    コマンドを読んでコマンドとその長さを返す
    """
    read_cmd=""
    for i in range(len(text)):#アルファベットである間読み続けることで判別
        if is_alpha(text[i]): #普通のisalpha()だと日本語全角文字もTrueになってまうので自作
            read_cmd+=text[i]
        else:
            break
    return read_cmd,i

if __name__=="__main__":
    main(sys.argv[1])

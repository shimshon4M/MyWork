#!usr/bin/env python

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re

pattern_bracket="[{}]"
pattern_brackets="[{}]"

def main(filename):
    lines=read_file(filename)
    root=ET.Element("root")
    sub=None #節一時保持用
    subsub=None #サブ節一時保持用
    ignore_cmds=["", "\\n","\\documentclass","\\docmentstyle","\\setcounter","\\usepackage","\\unitlength","\\etitle","\\eauthor","\\eabstract","\\ekeywords","\\headauthor","\\headtitle","\\affilabel","\\bibliographystyle"]

    for line in lines:
        line_eles=re.split(pattern_brackets,line,2)
        texcmd=line_eles[0]
        #print(texcmd)

        if texcmd in ignore_cmds:
            continue
        elif texcmd=="\\jtitle": #タイトル
            create_subelement(root, "title",line_eles[1])
        elif texcmd=="\\jauthor": #著者
            continue
        elif texcmd=="\\jabstract": #アブスト
            create_subelement(root, "abstract",line_eles[1])
        elif texcmd=="\\jkeywords": #キーワード
            create_subelement(root, "keywords",line_eles[1])
        elif texcmd=="\\section": #節
            sub=create_subelement_withkey(root,"section","title",line_eles[1],line_eles[2])
        elif texcmd=="\\subsection": #サブ節
            subsub=create_subelement_withkey(sub,"subsection","title",line_eles[1],line_eles[2])
        elif texcmd.startswith("\\noindent") or texcmd=="\\subparagraph":
            create_subelement_withkey(subsub,"subsubsection","title",line_eles[1],line_eles[2])
        elif texcmd=="\\acknowledgment":
            continue


    pretty_string=minidom.parseString(ET.tostring(root,"utf-8")).toprettyxml(indent="  ")
    with open("test.xml","w")as f:
        f.write(pretty_string)

def read_file(filename):
    lines=[]
    with open(filename,"r")as f:
        join_flg=True
        ignore_flg=False
        stackline=""
        for line in f.readlines():
            line=line.replace("\\underline","").replace("\\bfseries","").replace("textbf","").replace("\\footnote","")
            line=line.replace("\\%","%").replace("\\&","&")
            #line=re.sub(r"\\cite{no(.*?)}","[\\1]",line) #引用部の書き換え
            line=re.sub(r"\\cite{(.*?)}","",line) #引用部消しちゃう？
            #図表を無視する処理-----
            if line.startswith("\\end{"):
                ignore_flg=False
                continue
            if ignore_flg:
                continue
            if line.startswith("\\begin{"):
                ignore_flg=True
                continue
            #-----------------------
            if line.startswith("\\"):
                if stackline!="":
                    lines.append(stackline)
                stackline=line
            else:
                stackline+=line
    return lines

def create_subelement(root,tag,text):
    ET.SubElement(root,tag).text=text

def create_subelement_withkey(root,tag,key,value,text):
    sub=ET.SubElement(root,tag)
    sub.set(key,value)
    sub.text=text
    return sub

if __name__=="__main__":
    main(sys.argv[1])
    

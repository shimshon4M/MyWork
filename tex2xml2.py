#coding:utf-8

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import re
from collections import OrderedDict

DEBUG=True

sub_elements=[] #各セクションの情報を保持した辞書のリスト
new_commands={} #key:command name value:macro
new_envs={} #key:command name value:macro
section_ref_dic={"sec_pos":0,"subsec_pos":0,"subsubsec_pos":0} #セクションのrefの参照情報 key:label value:number of section
ref_dic={"ref_pos":1}#その他refの参照情報

def main(filename):
    text=readFile(filename) #texの読み込み
    xml_tree=parse_tmp(text,filename) #ElementTreeの作成
    writeFile(filename,xml_tree) #xmlで出力

def parse_tmp_read(text,pos):
    open_num=1
    close_num=0
    ret=""
    while open_num!=close_num:
        pos+=1
        if text[pos]=="{":
            open_num+=1
        elif text[pos]=="}":
            close_num+=1
        ret+=text[pos]
    return ret.replace("\\%","%").replace("\\\\",""),pos
def parse_tmp_read_begin(text,pos):
    ret=""
    while not text[pos:].startswith("\end{abstract}"):
        ret+=text[pos]
        pos+=1
    return ret,pos
def parse_tmp(text,filename):
    root=ET.Element("root") #xmlのroot
    pos=0
    title=""
    abst=""
    keywords=""
    while pos<len(text):
        pos+=1
        #print(pos,text[pos:pos+5])
        if text[pos:].startswith("\jtitle"):
            pos+=len("\jtitle")
            title,pos=parse_tmp_read(text,pos)
        elif text[pos:].startswith("\\title"):
            pos+=len("\\title")
            title,pos=parse_tmp_read(text,pos)
            if per_eng(title)>0.9:
                print("english")
                with open("./data/englishPaperList.txt","a")as f:
                    f.write(filename+"\n")
                sys.exit()
        elif text[pos:].startswith("\jabstract"):
            pos+=len("\jabstract")
            abst,pos=parse_tmp_read(text,pos)
        elif text[pos:].startswith("\\abstract"):
            pos+=len("\\abstract")
            abst,pos=parse_tmp_read(text,pos)
        elif text[pos:].startswith("\\begin{abstract}"):
            pos+=len("\\begin{abstract}")
            abst,pos=parse_tmp_read_begin(text,pos)
        elif text[pos:].startswith("\jkeywords"):
            pos+=len("\jkeywords")
            keywords,pos=parse_tmp_read(text,pos)
        elif text[pos:].startswith("\keywords"):
            pos+=len("\keywords")
            keywords,pos=parse_tmp_read(text,pos)
        if title!="" and abst!="" and keywords!="":
            break
    if title=="" or abst=="" or keywords=="":
        print("english")
        with open("./data/englishPaperList.txt","a")as f:
            f.write(filename+"\n")
        sys.exit()
    createSubElement(0,"title",title[:-1],key=None,value=None)
    createSubElement(0,"abstract",abst[:-1],key=None,value=None)
    createSubElement(0,"keywords",keywords[:-1],key=None,value=None)
    createSubElementAll_tmp(root)
    return root

def createSubElementAll_tmp(root):
    for elem in sub_elements:
        sub=ET.SubElement(root,elem.get("tag"))
        sub.text=elem.get("text")#置換処理がないときのために１回は
        if elem.get("key")!=None and elem.get("value")!=None:
            sub.set(elem.get("key"),elem.get("value"))
   
def readFile(filename):
    """
    texファイルの読み込み
    改行詰めで全部つなげる？
    空白も詰める？
    """
    with open(filename,"r")as f:
        text=f.read()
    return text.replace("\n","").replace(" ","").replace("　","").replace("（","(").replace("）",")").replace("\t","")

def writeFile(in_filename,xml_tree):
    """
    引数のElementTreeをtexファイル名+".xml"という名前のxmlで保存
    """
    pretty_string=minidom.parseString(ET.tostring(xml_tree,"utf-8")).toprettyxml(indent="  ")
    with open(in_filename+".xml","w")as f:
        f.write(pretty_string)

def parse(text):
    root=ET.Element("root") #xmlのroot
    wholepaper(text,0)
    createSubElementAll(root,text)
    return root

def wholepaper(text,pos):
    while not text[pos:].startswith("\\begin{document}"):
        pos=paperheader(text,pos)
    pos=body(text,pos)
    return pos

def paperheader(text,pos):
    #print(pos,text[pos:pos+10])
    if text[pos+2:].startswith("title") or text[pos+1:].startswith("title"):
        pos=title(text,pos)
    elif text[pos+2:].startswith("author") or text[pos+1:].startswith("author"):
        pos=author(text,pos)
    elif text[pos+2:].startswith("abstract"):
        pos=abstract(text,pos)
    elif text[pos+2:].startswith("keywords"):
        pos=keywords(text,pos)
    elif text[pos:].startswith("\\affilabel"):
        pos=affilabel(text,pos)
    elif text[pos:].startswith("\headtitle"):
        pos=headtitle(text,pos)
    elif text[pos:].startswith("\headauthor"):
        pos=headauthor(text,pos)
    elif text[pos:].startswith("\documentclass"):
        pos=documentclass(text,pos)
    elif text[pos:].startswith("\documentstyle"):
        pos=documentstyle(text,pos)
    elif text[pos:].startswith("\\usepackage"):
        pos=usepackage(text,pos)
    elif text[pos:].startswith("\setcounter"):
        pos=setcounter(text,pos)
    elif text[pos:].startswith("\\newcounter"):
        pos=newcounter(text,pos)
    elif text[pos:].startswith("\let"):
        pos=let(text,pos)
    elif text[pos:].startswith("\\newtheorem"):
        pos=newtheorem(text,pos)
    elif text[pos:].startswith("\\newcommand"):
        pos=newcommand(text,pos)
    elif text[pos:].startswith("\\renewcommand"):
        pos=renewcommand(text,pos)
    elif text[pos:].startswith("\\newenvironment"):
        pos=newenvironment(text,pos)
    elif text[pos:].startswith("\setulminsep"):
        pos=setulminsep(text,pos)
    elif text[pos:].startswith("\setulwidth"):
        pos=setulwidth(text,pos)
    elif text[pos:].startswith("\setlength"):
        pos=setlength(text,pos)
    elif text[pos:].startswith("\\newlength"):
        pos=newlength(text,pos)
    elif text[pos:].startswith("\\addtolength"):
        pos=addtolength(text,pos)
    elif text[pos:].startswith("\def"):
        pos=define(text,pos)
    elif text[pos:].startswith("\makeatletter"):
        pos+=len("\makeatletter")
    elif text[pos:].startswith("\makeatother"):
        pos+=len("\makeatother")
    elif text[pos:].startswith("\\newif"):
        pos+=len("\\newif")
    elif text[pos:].startswith("\ifFINAL"):
        pos+=len("\ifFINAL")
    elif text[pos:].startswith("\FINALtrue"):
        pos+=len("\FINALtrue")
    else:
        pos=dateinfo(text,pos)
    return pos
        
def documentclass(text,pos):
    pos+=len("\documentclass")
    pos+=len("[")
    val1,pos=statement(text,pos)
    pos+=len("]")
    pos+=len("{")
    val2,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**documentclass**",val1,val2)
    return pos
    
def documentstyle(text,pos):
    pos+=len("\documentstyle")
    pos+=len("[")
    val1,pos=statement(text,pos)
    pos+=len("]")
    pos+=len("{")
    val2,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**documentstyle**",val1,val2)
    return pos

def usepackage(text,pos):
    vals=[]
    pos+=len("\\usepackage")
    while text[pos] in ["[","{"]:
        if text[pos]=="[":
            pos+=len("[")
            val,pos=statement(text,pos)
            vals.append(val)
            pos+=len("]")
        elif text[pos]=="{":
            pos+=len("{")
            val,pos=statement(text,pos)
            vals.append(val)
            pos+=len("}")
    if DEBUG:print("**usepackage**",vals)
    return pos
            
def setcounter(text,pos):
    vals=[]
    pos+=len("\setcounter")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**setcounter**",vals)
    return pos

def newcounter(text,pos):
    vals=[]
    pos+=len("\\newcounter")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**newcounter**",vals)
    return pos

def let(text,pos):
    pos+=len("\let")
    pos+=len("\\")
    val,pos=statement(text,pos)
    if DEBUG:print("**let**","\\"+val)
    return pos

def define(text,pos):
    vals=[]
    pos+=len("\def")
    pos+=len("\\")
    val,pos=statement(text,pos)
    m_name,m_args=val.split("#")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    new_commands[m_name]="".join(vals)
    if DEBUG:print("**def**","\\",m_name,m_args,vals)
    return pos

def newtheorem(text,pos):
    vals=[]
    in_cmd_name=True
    cmd_name=""
    pos+=len("\\newtheorem")
    while text[pos]=="{" or text[pos]=="[":
        pos+=len("{")
        if text[pos]=="\\":
            pos+=len("\\")
        val,pos=statement(text,pos)
        if in_cmd_name:
            cmd_name=val
            in_cmd_name=False
        else:
            vals.append(val)
        pos+=len("}")
    new_commands[cmd_name]="".join(vals)
    if DEBUG:print("**newtheorem**",val,vals)
    return pos

def newcommand(text,pos):
    vals=[]
    in_cmd_name=True
    cmd_name=""
    pos+=len("\\newcommand")
    while text[pos]=="{" or text[pos]=="[":
        pos+=len("{")
        if text[pos]=="\\":
            pos+=len("\\")
        val,pos=statement(text,pos)
        if in_cmd_name:
            cmd_name=val
            in_cmd_name=False
        else:
            vals.append(val)
        pos+=len("}")
    new_commands[cmd_name]="".join(vals)
    if DEBUG:print("**newcommand**",val,vals)
    return pos

def renewcommand(text,pos):
    vals=[]
    in_cmd_name=True
    cmd_name=""
    pos+=len("\\renewcommand")
    while text[pos]=="{" or text[pos]=="[":
        pos+=len("{")
        if text[pos]=="\\":
            pos+=len("\\")
        val,pos=statement(text,pos)
        if in_cmd_name:
            cmd_name=val
            in_cmd_name=False
        else:
            vals.append(val)
        pos+=len("}")
    new_commands[cmd_name]="".join(vals)
    if DEBUG:print("**renewcommand**",val,vals)
    return pos

def newenvironment(text,pos):
    vals=[]
    in_cmd_name=True
    cmd_name=""
    pos+=len("\\newenvironment")
    while text[pos]=="{" or text[pos]=="[":
        pos+=len("{")
        if text[pos]=="\\":
            pos+=len("\\")
        val,pos=statement(text,pos)
        if in_cmd_name:
            cmd_name=val
            in_cmd_name=False
        else:
            vals.append(val)
        pos+=len("}")
    new_envs[cmd_name]="".join(vals)
    if DEBUG:print("**newenvironment**",val,vals)
    return pos

def setulminsep(text,pos):
    vals=[]
    pos+=len("\setulminsep")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**setulminsep**",vals)
    return pos

def setulwidth(text,pos):
    vals=[]
    pos+=len("\setulwidth")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**setulwidth**",vals)
    return pos

def setlength(text,pos):
    vals=[]
    pos+=len("\setlength")
    while text[pos]=="{":
        pos+=len("{")
        while text[pos]!="}":
            pos+=1
        pos+=len("}")
    if DEBUG:print("**setlength**",vals)
    return pos

def newlength(text,pos):
    vals=[]
    pos+=len("\\newlength")
    while text[pos]=="{":
        pos+=len("{")
        while text[pos]!="}":
            pos+=1
        pos+=len("}")
    if DEBUG:print("**newlength**",vals)
    return pos

def addtolength(text,pos):
    vals=[]
    pos+=len("\\addtolength")
    while text[pos]=="{":
        pos+=len("{")
        while text[pos]!="}":
            pos+=1
        pos+=len("}")
    if DEBUG:print("**addtolength**",vals)
    return pos

def title(text,pos):
    if text[pos:].startswith("\jtitle"):
        pos=jtitle(text,pos)
    elif text[pos:].startswith("\etitle"):
        pos=etitle(text,pos)
    elif text[pos:].startswith("\\title"):
        pos=title_(text,pos)
    return pos
        
def author(text,pos):
    if text[pos:].startswith("\jauthor"):
        pos=jauthor(text,pos)
    elif text[pos:].startswith("\eauthor"):
        pos=eauthor(text,pos)
    elif text[pos:].startswith("\\author"):
        pos=author_(text,pos)
    return pos

def abstract(text,pos):
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
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"jtitle",val)
    if DEBUG:print("**jtitle**",val)
    return pos
    
def etitle(text,pos):
    tmp_pos=pos
    pos+=len("\etitle")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"etitle",val)
    if DEBUG:print("**etitle**",val)
    return pos

def title_(text,pos):
    tmp_pos=pos
    pos+=len("\\title")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"title",val)
    if DEBUG:print("**title**",val)
    return pos

def jauthor(text,pos):
    tmp_pos=pos
    vals=[]
    pos+=len("\jauthor")
    pos+=len("{")
    while text[pos]!="}":
        val,pos=authorinfo(text,pos)
        vals.append(val)
        if text[pos:].startswith("\\and"):
            pos+=len("\\and")
    pos+=len("}")
    createSubElement(tmp_pos,"jauthor",",".join(vals))
    if DEBUG:print("**jauthor**",",".join(vals))
    return pos

def per_eng(text):
    cnt=0
    for c in text:
        if is_alpha(c):
            cnt+=1
    return cnt/len(text)
    
def eauthor(text,pos):
    tmp_pos=pos
    vals=[]
    pos+=len("\eauthor")
    pos+=len("{")
    while text[pos]!="}":
        val,pos=authorinfo(text,pos)
        vals.append(val)
        if text[pos:].startswith("\\and"):
            pos+=len("\\and")
    pos+=len("}")
    createSubElement(tmp_pos,"eauthor",",".join(vals))
    if DEBUG:print("**eauthor**",",".join(vals))
    return pos

def author_(text,pos):
    tmp_pos=pos
    vals=[]
    pos+=len("\\author")
    pos+=len("{")
    while text[pos]!="}":
        val,pos=authorinfo(text,pos)
        vals.append(val)
        if text[pos:].startswith("\\and"):
            pos+=len("\\and")
    pos+=len("}")
    createSubElement(tmp_pos,"author",",".join(vals))
    if DEBUG:print("**author**",",".join(vals))
    return pos

def authorinfo(text,pos):
    val1,pos=statement(text,pos)
    while text[pos:].startswith("\\affiref"):
        pos+=len("\\affiref")
        pos+=len("{")
        val2,pos=statement(text,pos)
        pos+=len("}")
    return val1,pos

def jabstract(text,pos):
    tmp_pos=pos
    pos+=len("\jabstract")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"jabstract",val)
    if DEBUG:print("**jabstract**",val)
    return pos
    
def eabstract(text,pos):
    tmp_pos=pos
    pos+=len("\eabstract")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"eabstract",val)
    if DEBUG:print("**eabstract**",val)
    return pos
    
def jkeywords(text,pos):
    tmp_pos=pos
    pos+=len("\jkeywords")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"jkeywords",val)
    if DEBUG:print("**jkeywords**",val)
    return pos
    
def ekeywords(text,pos):
    tmp_pos=pos
    pos+=len("\ekeywords")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"ekeywords",val)
    if DEBUG:print("**ekeywords**",val)
    return pos
    
def affilabel(text,pos):
    vals=[]
    pos+=len("\\affilabel")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**affilabel**",vals)
    return pos
        
def headtitle(text,pos):
    tmp_pos=pos
    pos+=len("\headtitle")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"headtitle",val)
    if DEBUG:print("**headtitle**",val)
    return pos
    
def headauthor(text,pos):
    tmp_pos=pos
    pos+=len("\headauthor")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    createSubElement(tmp_pos,"headauthor",val)
    if DEBUG:print("**headauthor**",val)
    return pos
    
def dateinfo(text,pos):
    if text[pos:].startswith("\Volume"):
        pos=volume(text,pos)
    elif text[pos:].startswith("\\Number"):
        pos=number(text,pos)
    elif text[pos:].startswith("\Month"):
        pos=month(text,pos)
    elif text[pos:].startswith("\Year"):
        pos=year(text,pos)
    elif text[pos:].startswith("\\received"):
        pos=received(text,pos)
    elif text[pos:].startswith("\\revised"):
        pos=revised(text,pos)
    elif text[pos:].startswith("\\rerevised"):
        pos=rerevised(text,pos)
    elif text[pos:].startswith("\\accepted"):
        pos=accepted(text,pos)
    elif text[pos:].startswith("\受付"):
        pos=uketsuke(text,pos)
    elif text[pos:].startswith("\再受付"):
        pos=saiuketsuke(text,pos)
    elif text[pos:].startswith("\再々受付"):
        pos=saisaiuketsuke(text,pos)
    elif text[pos:].startswith("\採録"):
        pos=sairoku(text,pos)
    elif text[pos:].startswith("\number"):
        pos=number(text,pos)
    return pos
        
def volume(text,pos):
    pos+=len("\Volume")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**volume**",val)
    return pos

def number(text,pos):
    pos+=len("\\Number")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**number**",val)
    return pos

def month(text,pos):
    pos+=len("\Month")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**month**",val)
    return pos

def year(text,pos):
    pos+=len("\Year")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**year**",val)
    return pos

def received(text,pos):
    vals=[]
    pos+=len("\\received")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**received**",vals)
    return pos

def revised(text,pos):
    vals=[]
    pos+=len("\\revised")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**revised**",vals)
    return pos

def rerevised(text,pos):
    vals=[]
    pos+=len("\\rerevised")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**rerevised**",vals)
    return pos

def accepted(text,pos):
    vals=[]
    pos+=len("\\accepted")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**accepted**",vals)
    return pos

def uketsuke(text,pos):
    vals=[]
    pos+=len("\受付")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**uketsuke**",vals)
    return pos

def saiuketsuke(text,pos):
    vals=[]
    pos+=len("\再受付")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("saiuketsuke",vals)
    return pos

def saisaiuketsuke(text,pos):
    vals=[]
    pos+=len("\再々受付")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("saisaiuketsuke",vals)
    return pos

def sairoku(text,pos):
    vals=[]
    pos+=len("\採録")
    while text[pos]=="{":
        pos+=len("{")
        val,pos=statement(text,pos)
        vals.append(val)
        pos+=len("}")
    if DEBUG:print("**sairoku**",vals)
    return pos
    
def body(text,pos):
    pos+=len("\\begin{document}")
    if text[pos:].startswith("\maketitle"):
        pos+=len("\maketitle")
    while text[pos:].startswith("\section") or text[pos:].startswith("\subsection") or                     text[pos:].startswith("\subsubsection"):
        pos=section(text,pos)
    if text[pos:].startswith("\\acknowledgment"):
        pos=acknowledgment(text,pos)
    pos=biodata(text,pos)
    pos+=len("\end{document}")
    return pos

def section(text,pos):
    tmp_pos=pos
    pos+=len("\section")
    if text[pos]=="*":
        pos+=len("*")
    pos+=len("{")
    val_title,pos=statement(text,pos)
    pos+=len("}")
    val_label=None
    if text[pos:].startswith("\label"):
        pos+=len("\label")
        pos+=len("{")
        val_label,pos=statement(text,pos)
        pos+=len("}")
    section_ref_append(0,val_label)
    val_body,pos=statement(text,pos)
    if DEBUG:print("**section**",val_title,val_body[:])
    while text[pos:].startswith("\subsection"):
        pos=subsection(text,pos)
    createSubElement(tmp_pos,"section",val_body,"title",val_title)
    return pos

def subsection(text,pos):
    tmp_pos=pos
    pos+=len("\subsection")
    if text[pos]=="*":
        pos+=len("*")
    pos+=len("{")
    val_title,pos=statement(text,pos)
    pos+=len("}")
    val_label=None
    if text[pos:].startswith("\label"):
        pos+=len("\label")
        pos+=len("{")
        val_label,pos=statement(text,pos)
        pos+=len("}")
    section_ref_append(1,val_label)
    val_body,pos=statement(text,pos)
    if DEBUG:print("**subsection**",val_title,val_body)
    while text[pos:].startswith("\subsubsection"):
        pos=subsubsection(text,pos)
    createSubElement(tmp_pos,"subsection",val_body,"title",val_title)
    return pos

def subsubsection(text,pos):
    tmp_pos=pos
    pos+=len("\subsubsection")
    if text[pos]=="*":
        pos+=len("*")
    pos+=len("{")
    val_title,pos=statement(text,pos)
    pos+=len("}")
    val_label=None
    if text[pos:].startswith("\label"):
        pos+=len("\label")
        pos+=len("{")
        val_label,pos=statement(text,pos)
        pos+=len("}")
    section_ref_append(2,val_label)
    val_body,pos=statement(text,pos)
    if DEBUG:print("**subsubsection**",val_title,val_body)
    createSubElement(tmp_pos,"subsubsection",val_body,"title",val_title)
    return pos

def acknowledgment(text,pos):
    pos+=len("\\acknowledgment")
    val,pos=statement(text,pos)
    if DEBUG:print("**acknowledgment**",val)
    createSubElement(pos,"acknowledgment",val)
    return pos

def biodata(text,pos):
    pos=bibliographystyle(text,pos)
    pos=bibliography(text,pos)
    while not text[pos:].startswith("\\begin{biography}"):
        pos+=1
    pos=biography(text,pos)
    pos+=len("\\biodate")
    return pos
    
def bibliographystyle(text,pos):
    pos+=len("\\bibliographystyle")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    if DEBUG:print("**bibliographystyle**",val)
    return pos

def bibliography(text,pos):
    pos+=len("\\begin{thebibliograpy}")
    pos+=len("{}")
    while not text[pos:].startswith("\end{thebibliography}"):
        #中身未実装
        pos+=1
    pos+=len("\end{thebibliography}")
    return pos

def bibitem(text,pos):
    pos+=len("\\bibitem")
    #中身未実装

def biography(text,pos):
    bios=[]
    pos+=len("\\begin{biography}")
    while not text[pos:].startswith("\end{biography}"):
        bio_dic,pos=bioauthor(text,pos)
        bios.append(bio_dic)
    pos+=len("\end{biography}")
    if DEBUG:print("**biography**",bios)
    return pos
        
def bioauthor(text,pos):
    pos+=len("\\bioauthor")
    pos+=len("{")
    val_name,pos=statement(text,pos)
    pos+=len("}")
    pos+=len("{")
    val_info,pos=statement(text,pos)
    pos+=len("}")
    return {val_name:val_info},pos
    
def statement(text,pos):
    ret=""
    while True:
        if text[pos:].startswith("\\ref"):
            tmp,pos=ref(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\cite") or text[pos:].startswith("\shortcite"): #\citeyearも含む
            pos=cite(text,pos)
        elif text[pos:].startswith("\\begin{figure}"):
            pos=figure(text,pos)
        elif text[pos:].startswith("\\begin{table}"):
            pos=table(text,pos)
        elif text[pos:].startswith("\\begin{gather}"):
            pos=gather(text,pos)
        elif text[pos:].startswith("\\footnote"):
            pos=footnote(text,pos)
        elif text[pos:].startswith("\label"):
            pos=label(text,pos)
        elif text[pos:].startswith("\\begin{equation}"):
            tmp,pos=equation(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\\begin{quote}"):
            tmp,pos=quote(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\\begin{itemize}"):
            tmp,pos=itemize(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\\begin{enumerate}"):
            tmp,pos=enumerate_(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\\begin{description}"):
            tmp,pos=description(text,pos)
            ret+=tmp
        elif text[pos:].startswith("\\begin{algorithm}"):
            pos=algorithm(text,pos)
        elif text[pos:].startswith("\kern"):
            pos+=len("\kern")
            while text[pos] not in ["{","[","\\"]:
                pos+=1
        elif text[pos:].startswith("\\textbf"):
            pos+=len("\\textbf")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("\\textit"):
            pos+=len("\\textit")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("\\texttt"):
            pos+=len("\\texttt")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("\\boldsymbol"):
            pos+=len("\\boldsymbol")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("\\rm"):
            pos+=len("\\rm")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("\\emph"):
            pos+=len("\\emph")
            pos+=len("{")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("{\\bf"):
            pos+=len("{\\bf")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("{\\it"):
            pos+=len("{\\it")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("{\\em"):
            pos+=len("{\\em")
            tmp,pos=statement(text,pos)
            pos+=len("}")
            ret+=tmp
        elif text[pos:].startswith("{\\_}"):
            ret+=text[pos+2]
            pos+=len("{\\_}")
            continue
        elif text[pos:].startswith("{\\&}"):
            ret+=text[pos+2]
            pos+=len("{\\&}")
            continue
        elif text[pos:].startswith("{\\%}"):
            ret+=text[pos+2]
            pos+=len("{\\%}")
            continue
        elif text[pos:].startswith("{\\-}"):
            ret+=text[pos+2]
            pos+=len("{\\-}")
            continue
        elif text[pos]=="$":
            pos+=len("$")
            """
            if text[pos:].startswith("\mathrm"):
                pos+=len("\mathrm")
                pos+=len("{")
                tmp,pos=statement(text,pos)
                pos+=len("}")
                ret+=tmp
            elif text[pos:].startswith("\mathit"):
                pos+=len("\mathit")
                pos+=len("{")
                tmp,pos=statement(text,pos)
                pos+=len("}")
                ret+=tmp
            else:
                tmp=text[pos:].split("$",1)[0]
                pos=len(text[:pos])+text[pos:].find("$")
                ret+=tmp
            """
            #数式はすべて置換する場合
            ret+=""#"$-$"
            pos=len(text[:pos])+text[pos:].find("$")
            pos+=len("$")
        elif text[pos:].startswith("\\noindent"):
            pos+=len("\\noindent")
        elif text[pos:].startswith("\\pagebreak"):
            pos+=len("\\pagebreak")
        elif text[pos:].startswith("\\baselineskip"):
            pos+=len("\\baselineskip")
        elif text[pos:].startswith("{\\allowdisplaybreaks"):
            pos+=len("{\\allowdisplaybreaks")
            tmp,pos=statement(text,pos)
            ret+=tmp
            pos+=len("}")
        elif text[pos:].startswith("\\textwidth"):
            pos+=len("\\textwidth")
        elif text[pos:].startswith("\columnsep"):
            pos+=len("\columnsep")
        elif text[pos:].startswith("\linebreak"):
            pos+=len("\linebreak")
            pos=len(text[:pos])+text[pos:].find("]")
            pos+=len("]")
        elif text[pos] in ["{","}","[","]"]:
            break
        elif text[pos]=="\\":
            if text[pos+1]=="\\":
                pos+=2
                continue
            elif text[pos+1]=="_":
                ret+=text[pos+1]
                pos+=2
                continue
            elif text[pos+1]=="&":
                ret+=text[pos+1]
                pos+=2
                continue
            elif text[pos+1]=="%":
                ret+=text[pos+1]
                pos+=2
                continue
            elif text[pos+1]=="-":
                ret+=text[pos+1]
                pos+=2
                continue
            elif text[pos+1] in ["'","v","\""]:#アクセント文字
                pos+=2
                pos+=len("{")
                tmp,pos=statement(text,pos)
                pos+=len("}")
                ret+=tmp
                continue
            elif text[pos+1] in ["p","q"]:
                pos+=2
                continue
            elif text[pos+1]=="\\":
                pos+=2
                continue
            break
        else: #char
            ret+=text[pos]
            pos+=1
    return ret,pos

def ref(text,pos):
    ret=""
    pos+=len("\\ref")
    pos+=len("{")
    val,pos=statement(text,pos)
    if val.startswith("sec:"):
        ret+="<sec_ref>"+val+"</sec_ref>"
    elif val.startswith("item"):
        ret+="<item_ref>"+val+"</item_ref>"
    pos+=len("}")
    return ret,pos
    
def cite(text,pos):
    if text[pos:].startswith("\cite"):
        pos+=len("\cite")
    elif text[pos:].startswith("\citeyear"):
        pos+=len("\citeyear")
    elif text[pos:].startswith("\shortcite"):
        pos+=len("\shortcite")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    return pos
    
def figure(text,pos):
    pos+=len("\\begin{figure}")
    #内部未実装
    while not text[pos:].startswith("\end{figure}"):
        pos+=1
    pos+=len("\end{figure}")
    return pos
    
def table(text,pos):
    pos+=len("\\begin{table}")
    #内部未実装
    while not text[pos:].startswith("\end{table}"):
        pos+=1
    pos+=len("\end{table}")
    return pos
    
def gather(text,pos):
    pos+=len("\\begin{gather}")
    #内部未実装
    while not text[pos:].startswith("\end{gather}"):
        pos+=1
    pos+=len("\end{gather}")
    return pos

def footnote(text,pos):
    pos+=len("\\footnote")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    return pos

def label(text,pos):
    pos+=len("\\label")
    pos+=len("{")
    val,pos=statement(text,pos)
    pos+=len("}")
    ref_dic[val]=str(ref_dic["ref_pos"])
    ref_dic["ref_pos"]+=1
    return pos

def equation(text,pos):
    pos+=len("\\begin{equation}")
    while not text[pos:].startswith("\end{equation}"):
        pos+=1
    pos+=len("\end{equation}")
    val=""#"$式$"
    return val,pos

def quote(text,pos):
    vals=[]
    pos+=len("\\begin{qupte}")
    while not text[pos:].startswith("\end{quote}"):
        val,pos=statement(text,pos)
        vals.append(val)
    pos+=len("\end{equation}")
    return "".join(vals),pos

def itemize(text,pos):
    vals=[]
    pos+=len("\\begin{itemize}")
    while not text[pos:].startswith("\end{itemize}"):
        pos+=len("\item")
        val,pos=statement(text,pos)
        vals.append(val)
    pos+=len("\end{itemize}")
    #if DEBUG:print("**itemize**",vals)
    return "".join(vals),pos

def enumerate_(text,pos):
    vals=[]
    pos+=len("\\begin{enumerate}")
    while not text[pos:].startswith("\end{enumerate}"):
        pos+=len("\item")
        val,pos=statement(text,pos)
        vals.append(val)
    pos+=len("\end{enumerate}")
    #if DEBUG:print("**enumerate**",vals)
    return "".join(vals),pos

def description(text,pos):
    vals=[]
    pos+=len("\\begin{description}")
    #内部未実装
    while not text[pos:].startswith("\end{description}"):
        pos+=len("\item")
        val,pos=statement(text,pos)
        vals.append(val)
    pos+=len("\end{description}")
    #if DEBUG:print("**description**",vals)
    return "".join(vals),pos

def algorithm(text,pos):
    pos+=len("\\begin{algorithm}")
    #内部未実装
    while not text[pos:].startswith("\end{algorithm}"):
        pos+=1
    pos+=len("\end{algorithm}")
    return pos

def createSubElement(pos,tag,text,key=None,value=None):
    #最後に一括でsubを追加する場合
    sub_elements.append({"pos":pos,"tag":tag,"text":text,"key":key,"value":value})
    
def createSubElementAll(root,text):#従来手法だと順序崩れる＆subsub関係が保持できないので最後に一気につなげる
    info_parts=[]
    tmp_sections={}
    for elem in sub_elements:#順序の整理
        if elem.get("tag") in ["section","subsection","subsubsection"]:
            pos=elem.get("pos")
            tmp_sections[pos]=elem
        else:
            info_parts.append(elem)
    sections=OrderedDict(sorted(tmp_sections.items(),key=lambda x:x[0]))

    for elem in info_parts:
        sub=ET.SubElement(root,elem.get("tag"))
        #ref箇所の置換処理
        replace_list=re.compile(r"<sec_ref>([a-zA-Z0-9\-:]+)</sec_ref>").findall(elem.get("text"))
        sub.text=elem.get("text")#置換処理がないときのために１回は
        for ref in replace_list:
            sub.text=re.sub("<sec_ref>"+ref+"</sec_ref>",section_ref_dic[ref],sub.text)
        replace_list=re.compile(r"<item_ref>([a-zA-Z0-9\-:]+)</item_ref>").findall(sub.text)
        for ref in replace_list:
            sub.text=re.sub("<item_ref>"+ref+"</item_ref>",ref_dic[ref],sub.text)
        if elem.get("key")!=None and elem.get("value")!=None:
            sub.set(elem.get("key"),elem.get("value"))
    for elem in sections.values():
        sub=ET.SubElement(root,elem.get("tag"))
        #ref箇所の置換処理
        replace_list=re.compile(r"<sec_ref>([a-zA-Z0-9\-:]+)</sec_ref>").findall(elem.get("text"))
        sub.text=elem.get("text")#置換処理がないときのために１回は
        for ref in replace_list:
            sub.text=re.sub("<sec_ref>"+ref+"</sec_ref>",section_ref_dic[ref],sub.text)
        replace_list=re.compile(r"<item_ref>([a-zA-Z0-9\-:]+)</item_ref>").findall(sub.text)
        for ref in replace_list:
            sub.text=re.sub("<item_ref>"+ref+"</item_ref>",ref_dic[ref],sub.text)
        if elem.get("key")!=None and elem.get("value")!=None:
            sub.set(elem.get("key"),elem.get("value"))
            
def section_ref_append(rank,label=None):
    #rank 0:sec 1:subsec 2:subsubsec
    if rank==0:
        section_ref_dic["sec_pos"]+=1
        section_ref_dic["subsec_pos"]=0
        section_ref_dic["subsubsec_pos"]=0
        if label!=None:
            section_ref_dic[label]=str(section_ref_dic["sec_pos"])
    elif rank==1:
        section_ref_dic["subsec_pos"]+=1
        section_ref_dic["subsubsec_pos"]=0
        if label!=None:
            section_ref_dic[label]=str(section_ref_dic["sec_pos"])+"."+                                                             str(section_ref_dic["subsec_pos"])
    elif rank==2:
        section_ref_dic["subsubsec_pos"]+=1
        if label!=None:
            section_ref_dic[label]=str(section_ref_dic["sec_pos"])+"."+                                                             str(section_ref_dic["subsec_pos"])+"."+                                                          str(section_ref_dic["subsubsec_pos"])
            
def is_alpha(s):
    """
    アルファベット(a-z A-Z)ならTrueを返す
    (普通のisalpha()だと日本語全角もTrueになってしまうので自作)
    """
    return re.compile(r"[a-zA-Z]").match(s)

if __name__=="__main__":
    main(sys.argv[1])

#coding:utf-8

import sys
import re

openbrack=r'[〔]'
closebrack=r'[〕]'

def isCloseOnly(line): # 閉じカッコだけ存在する行ならtrue
    if re.search(openbrack,line)==None and re.search(closebrack,line):
        return True
    return False

def isDigitRow(line): # 索引ページ番号のみの行ならtrue
    if line.isdigit():
        return True
    tmps=re.split(r'[,，]',line)
    for tmp in tmps:
        tmp=re.sub(" ","",tmp)
        if not tmp.isdigit():
            return False
    return True

def isInfoRow(line): # ページ、インデックス、空白行ならtrue
    if line=="\n" or line.startswith("-") or line.startswith("【") or line=="" or "和英索引" in line or "英和索引" in line:
        return True
    return False

def parse(filename):
    lines=[]
    with open(filename,"r")as f:
        tmpline=""
        arc_brack_open_z=0  #（
        arc_brack_close_z=0 # ）
        arc_brack_open_h=0  # (
        arc_brack_close_h=0 # )
        shell_brack_open=0  #〔
        shell_brack_close=0 # 〕
        for line in f.readlines():
            line=line.strip()
            if isInfoRow(line) or isDigitRow(line):
                continue
            arc_brack_open_z+=line.count("（")
            arc_brack_close_z+=line.count("）")
            arc_brack_open_h+=line.count("(")
            arc_brack_close_h+=line.count(")")
            shell_brack_open+=line.count("〔")
            shell_brack_close+=line.count("〕")

            if arc_brack_open_h==arc_brack_close_h and arc_brack_open_z==arc_brack_close_z and shell_brack_open==shell_brack_close:
                line=tmpline+line
                arc_brack_open_z=0
                arc_brack_close_z=0
                arc_brack_open_h=0
                arc_brack_close_h=0
                shell_brack_open=0
                shell_brack_close=0
                tmpline=""
                #print(line)
                lines.append(line)
            else:
                tmpline+=line
                continue
    return lines
  
def remove_brack(lines):
    outlines=[]
    for line in lines:
        arc_z_pos=line.find("（")
        arc_h_pos=line.find("(")
        shell_pos=line.find("〔")
        if arc_z_pos==-1:arc_z_pos=999
        if arc_h_pos==-1:arc_h_pos=999
        if shell_pos==-1:shell_pos=999
        
        pos=min(arc_z_pos,arc_h_pos,shell_pos)
        outlines.append(line[0:pos])
    return outlines
    
def remove_index(lines):
    outlines=[]
    for line in lines:
        spllines=line.split(" ")
        for splline in spllines:
            if isDigitRow(splline):
                spllines.remove(splline)
        outlines.append("".join(spllines))
    return outlines

if __name__=="__main__":
    args=sys.argv
    lines=parse(args[1])
    lines=remove_brack(lines)
    lines=remove_index(lines)

    with open("worddic/AIdic.txt","w") as f:
        for line in lines:
            f.write(line+"\n")

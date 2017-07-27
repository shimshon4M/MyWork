#!usr/env/bin python
#coding:utf-8

import sys

def main():
    args=sys.argv
    
    words=[]#単語辞書
    with open("worddic/worddic.txt","r")as f:
        for line in f.readlines():
            words.append(line)
            
    lines=[]
    with open(args[1],"r")as f: #分析対象
        for line in f.readlines():
            lines.append(line.strip())
        paper="".join(lines)

    for word in words:
        if word.strip() in paper:
            print(word.strip()+" ",end="")
            continue

if __name__=="__main__":
    main()

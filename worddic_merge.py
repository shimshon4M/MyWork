#!usr/env/bin python
#coding:utf-8


def merge(dicname1,dicname2,outdicname):
    words=[]
    with open(dicname1,"r")as f:
    for line in f.readlines():
        words.append(line)

    with open(dicname2,"r")as f:
        for line in f.readlines():
            if line not in words:
                #print (line)
                words.append(line)

    words.sort()

    with open(outdicname,"w")as f:
        for word in words:
            f.write(word)

"""
引数：辞書１　辞書２　統合後辞書
"""
if __name__=="__main__":
    args=sys.argv
    merge(args[1],args[2],args[3])

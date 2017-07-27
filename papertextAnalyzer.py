#coding:utf-8

"""
##属性(分類先) 5
・タイトル
・著者
・メールアドレス
・本文
・参考文献
##素性(カッコ内は次元数)
・行番目(全行数で割る？)
・構成形態素中の
　・人名の割合
　・英数字の割合
・"@"や".jp"とかメアドっぽい文字が含まれているか(1)
・直前の文の属性(5)
"""
import sys
import MeCab

def analyze(filename):
    if isEnglishPaper(filename):#英語論文は対象外
        exit(1)
    m=MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
    m.parse("")

    with open(filename,"r")as f:
        lines=f.readlines()
        for i,line in enumerate(lines):
            vectors=[]#素性ベクトル
            rslts=m.parse(line).split("\n")#1行の形態素解析結果
            for morph in rslts:#各語について
                if morph=="" or morph=="EOS":#無意味なのは飛ばす
                    continue
                appear,tmp=morph.split("\t")
                hinshi1,hinshi2,hinshi3,hinshi4,hinshi5,hinshi6,base=tmp.split(",")[0:7] #読みは保持してない
            

def isEnglishPaper(filename):
    with open(filename,"r")as f:
        partline=f.readlines()[0:10]
        words=[]
        for line in partline:
            words.extend(line.split(" "))
        count=0
        for word in words:
            if word[1:].strip().islower():
                count+=1
        #print(count,len(words),count/len(words))
        return True if count/len(words)>0.6 else False
            
#param1: target filename
if __name__=="__main__":
    analyze(sys.argv[1])

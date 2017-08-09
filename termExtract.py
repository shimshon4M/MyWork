#!usr/env/bin python
#coding:utf-8

import termextract.mecab
import termextract.core
import collections
import MeCab
from pprint import pprint
import sys

args=sys.argv

m=MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
m.parse("")

with open(args[1],"r")as f:
    text=f.read()
    #text=text.replace(" ","")#スペースつめ
    text=text.replace("\n","")#改行つめ
text=m.parse(text)

frequency = termextract.mecab.cmp_noun_dict(text)
#pprint(frequency)

LR=termextract.core.score_lr(frequency,ignore_words=termextract.mecab.IGNORE_WORDS,lr_mode=1,average_rate=1)
#pprint(LR)

term_imp=termextract.core.term_importance(frequency,LR)
#pprint(term_imp)

data_collection=collections.Counter(term_imp)
for cmp_noun, value in data_collection.most_common():
    print(termextract.core.modify_agglutinative_lang(cmp_noun),value,sep="\t")

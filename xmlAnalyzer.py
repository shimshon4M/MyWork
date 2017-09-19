#!usr/bin/env python

import xml.etree.ElementTree as ET
import termextract.mecab
import termextract.core
import collections
import MeCab
from pprint import pprint
import sys
import re

def main(filename):
    tree=ET.parse(filename)
    root=tree.getroot()
    texts=removeTags(root)
    #attribs,texts=removeTags(root)
    #extractTerms(attribs,texts)
    #analyze(root)
    
def extractTerms(attribs,texts):
    mecab_result=toMorphemes(texts)+toMorphemes(attribs)
    frequency = termextract.mecab.cmp_noun_dict("".join(mecab_result))
    LR=termextract.core.score_lr(frequency,ignore_words=termextract.mecab.IGNORE_WORDS,lr_mode=1,average_rate=1)
    term_imp=termextract.core.term_importance(frequency,LR)
    data_collection=collections.Counter(term_imp)
    for cmp_noun, value in data_collection.most_common():
        print(termextract.core.modify_agglutinative_lang(cmp_noun),value,sep="\t")


def toMorphemes(texts):
    m=MeCab.Tagger("")
    m.parse("")

    ret_texts=[]
    for text in texts:
        if text!=None:
            ret_texts.append(m.parse(text))
    return ret_texts

def removeTags(root):
    """
    key:section title value:[body text]の辞書を返す
    """
    rettexts={}
    appeared_title=False#titleが処理済みか
    appeared_abst=False#abstが処理済みか
    for elem in root.iter():
        if "title" in elem.tag and not appeared_title:
            rettexts["title"]=elem.text
            appeared_title=True
        elif "abstract" in elem.tag and not appeared_abst:
            rettexts["abstract"]=elem.text
            appeared_abst=True
        elif "section" in elem.tag:
            rettexts[elem.attrib["title"]]=elem.text
    return rettexts

def period_split(text):
    """
    textを句点で分割したlistを返す
    普通のsplitと違い句点自体は消さない
    """
    i=0

def analyze(root):
    for elem in root.findall("section"):
        print(elem.tag,elem.attrib,elem.text[:10])
        for child in elem:
            print(child.tag,child.attrib,child.text[:10])

if __name__=="__main__":
    main(sys.argv[1])

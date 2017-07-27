#!usr/bin/env/python
#coding:utf-8

import sys
import xml.etree.ElementTree as ET

def convert2xml(filename):
    root=ET.Element("root")
    
    with open(filename,"r")as f:
       for line in f.readlines():
        #if len(line)==1:continue
        if line[0:2] in ["1 ","2 ","3 ","4 ","5 ","6 ","1.","2.","3.","4.","5.","6."] and len(line)>5:
           print line
            

if __name__=="__main__":
    args=sys.argv
    convert2xml(args[1])

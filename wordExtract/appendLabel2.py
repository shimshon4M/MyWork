import sys
import os.path

def append_label(filename):
    #existの方使わないように！
    if os.path.exists(filename.replace("BoW","labeled")):
        with open(filename.replace("BoW","labeled"),"r")as f:
            exist_data=[line for line in f.readlines()]
        outdata=[]
        with open(filename,"r")as f:
            for i,line_feature in enumerate(lines,1):
                line_spl=line_feature.split("\t")
                #if len(line_exist.split("\t"))==3:
                #    outdata.append(line_exist)
                #    print("already exists",line_exist.split("\t")[0])
                #    continue
                #作業サポート用print
                outdata.append("TERM\t"+line_spl[0]+"\t"+line_spl[1]+"\t\n")
        with open(filename.replace("BoW","labeled"),"w")as f:
            f.writelines(outdata)
    else:
        outdata=[]
        with open(filename,"r")as f:
            lines=f.readlines()
            for i,line in enumerate(lines,1):
                line_spl=line.split("\t")
                outdata.append("TERM\t"+line_spl[0]+"\t"+line_spl[1]+"\t\n")
        with open(filename.replace("BoW","labeled"),"w")as f:
            f.writelines(outdata)

if __name__=="__main__":
    append_label(sys.argv[1])

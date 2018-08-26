import sys
import os.path

def append_label(filename):#引数は素性の方
    #existの方使わないように！
    if os.path.exists(filename.replace("BoW","labeled_tmp")):
        with open(filename.replace("BoW","labeled_tmp"),"r")as f:
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
        with open(filename.replace("W2VSum","labeled_tmp"),"w")as f:
            f.writelines(outdata)
    else:
        outdata=[]
        with open(filename,"r")as f:
            lines=f.readlines()
            for i,line in enumerate(lines,1):
                line_spl=line.split("\t")
                outdata.append("TERM\t"+line_spl[0]+"\t"+line_spl[1]+"\t\n")
        with open(filename.replace("BoW","labeled_tmp"),"w")as f:
            f.writelines(outdata)

def fill_zero(filename):#引数はlabeled_tmpの方
    with open(filename,"r")as f:
        exist_data=[]
        for i,line in enumerate(f.readlines()):
            spl=line.split("\t")
            spl.insert(1,str(i))
            exist_data.append("\t".join(spl))
    with open(filename.replace("labeled_tmp","labeled"),"w")as f:
        for line in exist_data:
            if len(line.strip().split("\t"))==4: #ラベル無しならば
                f.write(line.strip()+"\t0\n")
            else:
                f.write(line)

if __name__=="__main__":
    #append_label(sys.argv[1])
    fill_zero(sys.argv[1])

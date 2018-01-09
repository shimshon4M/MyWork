import sys
import os.path

def append_label(filename):
    if os.path.exists(filename.replace("BoW","labeled")):
        with open(filename.replace("BoW","labeled"),"r")as f:
            exist_data=[line for line in f.readlines()]
        outdata=[]
        with open(filename,"r")as f:
            lines=f.readlines()
            for i,(line_feature,line_exist) in enumerate(zip(lines,exist_data),1):
                if i%10==1:
                    print("----0:not term 1:raw data 2:formated data 3:method 4:goal----")
                line_spl=line_feature.split("\t")
                if len(line_exist.split("\t"))==3:
                    outdata.append(line_exist)
                    print("already exists",line_exist.split("\t")[0])
                    continue
                #作業サポート用print
                back_text=[s for s in line_spl[3:7]]
                fromt_text=[s for s in line_spl[7:11]]
                print(str(i)+"/"+str(len(lines)),"".join(back_text)+"<"+line_spl[0]+">"+"".join(fromt_text),":",end="")
                label=input()
                outdata.append(line_spl[0]+"\t"+line_spl[1]+"\t"+label+"\n")
        with open(filename.replace("BoW","labeled"),"w")as f:
            f.writelines(outdata)
    else:
        outdata=[]
        with open(filename,"r")as f:
            lines=f.readlines()
            for i,line in enumerate(lines,1):
                if i%10==1:
                    print("----0:not term 1:raw data 2:formated data 3:method 4:goal----")
                line_spl=line.split("\t")
            
                #作業サポート用print
                back_text=[s for s in line.split("\t")[4:8]]
                fromt_text=[s for s in line.split("\t")[8:12]]
                print(str(i)+"/"+str(len(lines)),"".join(back_text)+"<"+line_spl[0]+">"+"".join(fromt_text),":",end="")
                label=input()
                outdata.append(line_spl[0]+"\t"+line_spl[1]+"\t"+label+"\n")

        with open(filename.replace("BoW","labeled"),"w")as f:
            f.writelines(outdata)

if __name__=="__main__":
    append_label(sys.argv[1])

import sys

def append_label(filename):
    outdata=[]
    with open(filename,"r")as f:
        lines=f.readlines()
        for i,line in enumerate(lines,1):
            if i%10==1:
                print("----0:not term 1:raw data 2:formated data 3:method 4:goal----")
            line_spl=line.split("\t")
            #作業サポート用print
            back_text=[s for s in line.split("\t")[6:10]]
            fromt_text=[s for s in line.split("\t")[10:14]]
            print(str(i)+"/"+str(len(lines)),"".join(back_text)+"<"+line_spl[0]+">"+"".join(fromt_text),"     :",end="")
            label=input()
            outdata.append(line.strip()+"\t"+label+"\n")

    with open(filename[:-4]+"_labeled.txt","w")as f:
        f.writelines(outdata)

if __name__=="__main__":
    append_label(sys.argv[1])

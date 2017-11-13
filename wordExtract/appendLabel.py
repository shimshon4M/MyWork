import sys

def append_label(filename):
    outdata=[]
    with open(filename,"r")as f:
        print("----1:term 0:not term----")
        lines=f.readlines()
        for i,line in enumerate(lines,1):
            line_spl=line.split("\t")
            print(str(i)+"/"+str(len(lines)),"".join(line.split("\t")[5:9])+"<"+line_spl[0]+">"+"".join(line.split("\t")[9:13]),":",end="")
            label=input()
            outdata.append(line.strip()+"\t"+label+"\n")

    with open(filename[:-4]+"_labeled.txt","w")as f:
        f.writelines(outdata)

if __name__=="__main__":
    append_label(sys.argv[1])

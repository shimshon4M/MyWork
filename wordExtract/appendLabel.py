import sys

def append_label(filename):
    outdata=[]
    with open(filename,"r")as f:
        print("1:is term 0:not term")
        lines=f.readlines()
        for i,line in enumerate(lines,1):
            line_spl=line.split("\t")
            print(str(i)+"/"+str(len(lines))+line_spl[4]+line_spl[5]+line_spl[6]+"<"+line_spl[0]+">"+line_spl[7]+line_spl[8]+line_spl[9],":",end="")
            label=input()
            outdata.append(line.strip()+"\t"+label+"\n")

    with open(filename[:-4]+"_labeled.txt","w")as f:
        f.writelines(outdata)

if __name__=="__main__":
    append_label(sys.argv[1])

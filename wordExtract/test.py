import sys

out=[]
with open(sys.argv[1],"r")as f:
    lines=f.readlines()
    for i,line in enumerate(lines):
        if i%5==0:
            out.append(line.strip()+"\t"+"1.0")
        else:
            out.append(line.strip()+"\t"+"0.0")
with open(sys.argv[1]+".txt","w")as f:
    f.write("\n".join(out))
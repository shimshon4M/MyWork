import glob

files=glob.glob("./data/xml/Terms/*",recursive=False)

term_dfs={} # key:term value:df 
for file in files:
    with open(file,"r")as f:
        for line in f.readlines():
            term=line.split("\t")[0]
            if term in term_dfs:
                term_dfs[term]+=1
            else:
                term_dfs[term]=1
with open("./data/df.txt","w")as f:
    for term,df in term_dfs.items():
        f.write(term+"\t"+str(df)+"\n")

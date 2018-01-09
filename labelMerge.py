import sys
import os

f_type="BoW"

def main():
    found=False
    new_filename=sys.argv[1]
    fr_oldfeatures=open(new_filename.replace("xml","feature_data"),"r")
    fr_newfeatures=open(new_filename,"r")
    if not os.path.exists(new_filename.replace("xml","feature_data").replace(f_type,"labeled")):
        print("  labeled file not found")
        sys.exit()
    fr_oldlabels=open(new_filename.replace("xml","feature_data").replace(f_type,"labeled"),"r")
    fw_newlabels=open(new_filename.replace(f_type,"labeled"),"w")
    
    old_features=[line for line in fr_oldfeatures.readlines()]
    fr_oldfeatures.close()
    old_labels=[line for line in fr_oldlabels.readlines()]
    fr_oldlabels.close()
    for line in fr_newfeatures.readlines():
        line_spl=line.split("\t",12)
        for old in old_features:
            old_spl=old.split("\t",12)
            if line_spl[0]==old_spl[0] and line_spl[3:11]==old_spl[3:11]:
                #print(line_spl[0:11])
                for ol in old_labels:
                    ol_spl=ol.split("\t")
                    if ol_spl[0:2]==old_spl[0:2]: 
                        fw_newlabels.write(line_spl[0]+"\t"+line_spl[1]+"\t"+ol_spl[2])
                        break
                found=True    
                break
        if not found:
            fw_newlabels.write(line_spl[0]+"\t"+line_spl[1]+"\n")
        found=False
    print(" wrote to :"+new_filename.replace(f_type,"labeled"))
    fr_newfeatures.close()
    fw_newlabels.close()
            
if __name__=="__main__":
    main()

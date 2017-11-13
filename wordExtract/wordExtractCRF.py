from itertools import chain
import pycrfsuite
import sklearn
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import sys

def readData(filename):
    data=[]
    with open(filename,"r",encoding="utf-8") as f:
        for line in f.readlines():
            """
            tmp_data=[]
            for d in line.split("\t"):
                tmp_data.append(str(d.encode("utf-8")))
            data.append(tmp_data)
           """
            data.append(line.split("\t"))
    train_num=0#int(len(data)*0.9)
    train_data=data[:train_num]
    test_data=data[train_num:]
    return train_data,test_data

def train(train_data):
    trainer=pycrfsuite.Trainer(verbose=False)
    train_features=[data2features(d) for d in train_data]
    train_labels=[data2labels(d) for d in train_data]
    trainer.append(train_features,train_labels)#学習データの読み込み
    trainer.set_params({
        "c1":1.0,
        "c2":1e-3,
        "max_iterations":50,
        "feature.possible_transitions":True
    })#パラメータ設定
    trainer.train("model.crfsuite")

def data2features(data):
    if float(data[1])>100:
        imp="1"
    else:
        imp="0"
    ret_data=[str(imp)]
    ret_data.extend(data[2:-1])
    return ret_data
    #return data[1:-1]

def data2labels(data):
    return data[-1]

def data2terms(data):
    return data[0]

def test(test_data):
    test_features=[data2features(d) for d in test_data]
    test_labels=[data2labels(d) for d in test_data]
    test_terms=[data2terms(d) for d in test_data]#分類対象キーワード候補
    tagger=pycrfsuite.Tagger()
    tagger.open("model.crfsuite")
    
    pred_labels=tagger.tag(test_features)#分類
    correct_num=0
    for i in range(len(test_terms)):
        pred_label=pred_labels[i].strip()
        correct_label=test_labels[i].strip()
        #print("pred:",pred_label," correct:",correct_label)
        if pred_label==correct_label:
            correct_num+=1
        if pred_label=="1":
            print(test_terms[i],":",test_features[i][4],test_features[i][5],test_terms[i],test_features[i][6],test_features[i][7],"\n")
        #print(test_terms[i],"pred:%s"%pred_label,"correct:%s"%correct_label)
    print(correct_num/len(test_terms))

if __name__=="__main__":
    train_data,test_data=readData(sys.argv[1])
    #train(train_data)
    test(test_data)

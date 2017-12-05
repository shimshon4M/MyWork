from sklearn import svm
from sklearn.externals import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import numpy as np
import sys
from utils import get_files
import random

test_all=False

def readData(dirname):
    print("read data")
    data=[]
    files=get_files(dirname)
    i=0
    for filename in files:
        feature_filename=filename.replace("labeled","BoW")
        with open(feature_filename,"r") as f:
            for line in f.readlines():
                line=line.strip()
                data.append(line.split("\t"))
        #素性データとラベルデータが別々の場合
        with open(filename,"r")as f:
            for line in f.readlines():
                data[i].append(line.strip().split("\t")[-1])
                i+=1
    if test_all:train_num=0
    else:train_num=int(len(data)*0.9)
    random.shuffle(data)
    train_data=data[:train_num]
    test_data=data[train_num:]
    return train_data,test_data

def data2features(data):
    f_pos=d[2]
    return [d[f_pos:-1] for d in data]

def data2labels(data):
    return [d[-1] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def train(train_data):
    print("train")
    #学習データ
    train_features=np.array(data2features(train_data))#d) for d in train_data])
    train_labels=np.array(data2labels(train_data))#d) for d in train_data])
    #学習
    estimator=svm.SVC(kernel='linear', C=1.0, class_weight="balanced")
    classifier=OneVsRestClassifier(estimator)
    classifier.fit(train_features,train_labels)
    joblib.dump(classifier,"term_extract_svc.pkl",compress=True)

def test(test_data):
    print("predict")
    test_features=data2features(test_data)#d) for d in test_data]
    test_labels=data2labels(test_data)#d) for d in test_data]
    test_terms=data2terms(test_data)#d) for d in test_data]#分類対象キーワード候補
    classifier=joblib.load("term_extract_svc.pkl")
    #予測
    pred_labels=classifier.predict(test_features)
    correct_num=0
    """
    for i in range(len(test_data)):
        pred_label=pred_labels[i].strip()
        correct_label=test_labels[i].strip()
        if pred_label==correct_label:
            correct_num+=1
        if int(pred_label)>0:
            print(test_data[i][0],":",pred_label)
    """
    #print(correct_num,"/",len(test_labels),"=",correct_num/len(test_labels))
    print(classification_report(test_labels,pred_labels))
    print(confusion_matrix(test_labels,pred_labels))
    
if __name__=="__main__":
    train_data,test_data=readData(sys.argv[1])
    if not test_all:train(train_data)
    test(test_data)

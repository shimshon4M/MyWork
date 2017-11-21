from sklearn import svm
from sklearn.externals import joblib
import numpy as np
import sys
from utils import get_files

def readData(dirname):
    print("read data")
    data=[]
    files=get_files(dirname)
    for filename in files:
        with open(filename,"r") as f:
            for line in f.readlines():
                line=line.strip()
                data.append(line.split("\t"))
    train_num=int(len(data)*0.9)
    train_data=data[:train_num]
    test_data=data[train_num:]
    return train_data,test_data

def data2features(data):
    return [d[23:-1] for d in data]

def data2labels(data):
    return [d[2] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def train(train_data):
    print("train")
    #学習データ
    train_features=np.array(data2features(train_data))#d) for d in train_data])
    train_labels=np.array(data2labels(train_data))#d) for d in train_data])
    #学習
    estimator=svm.SVC(kernel='linear', C=1)
    estimator.fit(train_features,train_labels)
    joblib.dump(estimator,"term_extract_svc.pkl",compress=True)

def test(test_data):
    print("predict")
    test_features=data2features(test_data)#d) for d in test_data]
    test_labels=data2labels(test_data)#d) for d in test_data]
    test_terms=data2terms(test_data)#d) for d in test_data]#分類対象キーワード候補
    estimator=joblib.load("term_extract_svc.pkl")
    #予測
    pred_labels=estimator.predict(test_features)
    correct_num=0
    for i in range(len(test_data)):
        pred_label=pred_labels[i].strip()
        correct_label=test_labels[i].strip()
        if pred_label==correct_label:
            correct_num+=1
    print(correct_num/len(test_labels))
        
if __name__=="__main__":
    train_data,test_data=readData(sys.argv[1])
    train(train_data)
    test(test_data)

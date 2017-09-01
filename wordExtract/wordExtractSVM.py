from sklearn.svm import LinearSVC
from sklearn.externals import joblib
import numpy as np
import sys

def readData(filename):
    data=[]
    with open(filename,"r") as f:
        for line in f.readlines():
            data.append(line.split("\t"))
    train_num=int(len(data)*0.9)
    train_data=data[:train_num]
    test_data=data[train_num:]
    return train_data,test_data

def data2features(data):
    return [d[1:-1] for d in data]

def data2labels(data):
    return [d[-1] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def train(train_data):
    #学習データ
    train_features=np.array([data2features(d) for d in train_data])
    train_labels=np.array([data2labels(d) for d in train_data])
    #学習
    estimator=LinearSVC(C=1.0)
    estimator.fit(train_features,train_labels)
    joblibb.dump(estimator,"term_extract_svc.pkl",compress=True)

def test(test_data):
    test_features=[data2features(d) for d in test_data]
    test_labels=[data2labels(d) for d in test_data]
    test_terms=[data2terms(d) for d in test_data]#分類対象キーワード候補
    estimator=joblib.load("term_extract_svc.pkl")
    #予測
    pred_label=estimator.predict(test_data)
    return pred_label

if __name__=="__main__":
    train_data,test_data=readData(sys.argv[1])
    train(train_data)
    pred_label=test(test_data)
    
    print(pred_label)

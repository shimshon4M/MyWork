from sklearn import svm
from sklearn.externals import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
#from sklearn.grid_search import GridSearchCV
import numpy as np
import pandas
import sys
from utils import get_files

doPCA=False
pca=PCA(n_components=300)
feature_type="posW2V"
classifier_pkl_name="term_extract_svc_"+feature_type+".pkl"

def readData(dirname,all_return=False,shuffle=True):
    print("read data")
    data=[]
    files=get_files(dirname)
    i=0
    for filename in files:
        feature_filename=filename.replace("labeled",feature_type)
        with open(feature_filename,"r") as f:
            for line in f.readlines():
                line=line.strip()
                data.append(line.split("\t"))
        #素性データとラベルデータが別々の場合
        with open(filename,"r")as f:
            for line in f.readlines():
                data[i].append(line.strip().split("\t")[-1])
                i+=1
    """
    if all_return:
        return np.array(data)
    elif not shuffle:
        train_num=int(len(data)*0.9)
        return data[:train_num],data[train_num:]
    else:
        train_data,test_data=train_test_split(np.array(data),test_size=0.1,shuffle=True)
    """
    if all_return:
        return np.array(data2features(data)).astype(np.float32),np.array(data2labels(data)).astype(np.float32)
    train_data,test_data=train_test_split(np.array(data),test_size=0.1,shuffle=False)
    #return train_data,test_data
    return np.array(data2features(train_data)).astype(np.float32),np.array(data2labels(train_data)).astype(np.float32),np.array(data2features(test_data)).astype(np.float32),np.array(data2labels(test_data)).astype(np.float32)

def data2features(data):
    f_pos=int(data[0][2])#素性ベクトルの開始位置
    return [d[f_pos:-1] for d in data]

def data2labels(data):
    return [d[-1] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def cross_valid(data):
    features=np.array(data2features(data))
    labels=np.array(data2labels(data))
    train_features,test_features,train_labels,test_labels=train_test_split(features,labels,test_size=0.2)
    tune_params=[
        #{"estimator__kernel":["rbf"],"estimator__gamma":[1e-3,1e-4],"estimator__C":[1,10,100,1000],"estimator__class_weight":["balanced"]},
        {"estimator__kernel":["linear"],"estimator__C":[1,10],"estimator__class_weight":["balanced"]}
    ]
    scores=["precision","recall"]
    for score in scores:
        print("Tuning parameters for %s"%score)
        estimator=OneVsRestClassifier(svm.SVC())
        classifier=GridSearchCV(estimator,tune_params,cv=10,scoring="%s_weighted"%score)
        classifier.fit(train_features,train_labels)
        print("Best parameter:")
        print(classifier.best_params_)
        print("Grid scores:")
        for params,mean_score,scores in classifier.grid_scores_:
            print("%0.3f for %r"%(mean_score,scores.std()*2,params))
        print("Classification report:")
        pred_labels=classifier.predict(test_features)
        print(classification_report(test_labels,pred_labels,target_names=["None","data","formated_data","method","purpose"]))
        print()

def train(train_features,train_labels):
    print("train")
    #学習データ
    #train_features=np.array(data2features(train_data))#d) for d in train_data])
    #train_labels=np.array(data2labels(train_data))#d) for d in train_data])
    #学習
    #estimator=svm.SVC(kernel='linear', C=10.0, class_weight="balanced")
    estimator=svm.SVC(kernel='rbf', C=10.0, gamma=0.01 ,class_weight="balanced")
    classifier=OneVsRestClassifier(estimator)
    classifier.fit(train_features,train_labels)
    joblib.dump(classifier,classifier_pkl_name,compress=True)

def test(test_features,test_labels):
    print("predict")
    #test_features=data2features(test_data)#d) for d in test_data]
    #test_labels=data2labels(test_data)#d) for d in test_data]
    test_terms=data2terms(test_features)#d) for d in test_data]#分類対象キーワード候補
    classifier=joblib.load(classifier_pkl_name)
    #予測
    pred_labels=classifier.predict(test_features)
    correct_num=0

    """
    for i in range(len(test_data)):
        pred_label=pred_labels[i].strip()
        correct_label=test_labels[i].strip()
        if pred_label==correct_label:
            correct_num+=1
        if pred_label!="0" and correct_label!="0":
            if pred_label==correct_label:
                print("correct   : ",end="")
            else:
                print("incorrect : ",end="")
            print(test_data[i][1],test_data[i][0],":","pred",pred_label,"correct",correct_label)
    """
    
    #print(correct_num,"/",len(test_labels),"=",correct_num/len(test_labels))
    print(classification_report(test_labels,pred_labels,target_names=["None","data","formated_data","method","purpose"]))
    print(confusion_matrix(test_labels,pred_labels))

def main():
    train_features,train_labels,test_features,test_labels=readData(sys.argv[1],shuffle=False)
    if doPCA:
        pca.fit(train_features)
        train_features=pca.transform(train_features)
        test_features=pca.transform(test_features)
    #test_features,test_labels=readData(sys.argv[1],shuffle=False,all_return=True) #全部でテスト
    train(train_features,train_labels)
    test(test_features,test_labels)
    #data=readData(sys.argv[1],all_return=True)
    #cross_valid(data)
    
if __name__=="__main__":
    main()

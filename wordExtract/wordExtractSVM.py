from sklearn import svm
from sklearn.externals import joblib
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
import numpy as np
import pandas
import sys
from utils import get_files

balanceSplit=True
identifySection=True
doPCA=False
pca=PCA(n_components=300)
feature_type="W2VSum"
classifier_pkl_name="term_extract_svc_"+feature_type+".pkl"

def readData(dirname,all_return=False,shuffle=True):
    print("read data")
    datas=[]
    files=get_files(dirname)
    for filename in files:
        i=0
        data=[]
        feature_filename=filename.replace("labeled",feature_type)
        with open(feature_filename,"r") as f:
            for line in f.readlines():
                line=line.strip()
                data.append(line.split("\t"))
        #素性データとラベルデータが別々の場合
        with open(filename,"r")as f:
            for line in f.readlines():
                label=line.strip().split("\t")[-1]
                #if label=="2":label="1"
                data[i].append(label)
                i+=1
        #methodの文からのみ抽出する場合
        if identifySection:
            sectiondata_filename=filename.replace("/labeled/","/sectionData/").replace("_feature_labeled","")
            with open(sectiondata_filename,"r")as f:
                ls=f.readlines()
                method_pos=int(ls[1].split("\t")[1])
                result_pos=int(ls[2].split("\t")[1])
            remove_indexes=[]
            for j,d in enumerate(data):
                if isInTitleSection(d):
                    continue
                pos=features2pos(d)
                if method_pos==-1:
                    continue
                if result_pos==-1:
                    if pos>=method_pos:
                        continue
                else:
                    if pos>=method_pos and pos<result_pos:
                        continue
                remove_indexes.append(j)
            for j,idx in enumerate(remove_indexes):
                data.pop(idx-j)
        #if len(data)==0:print(sectiondata_filename)
        datas.extend(data)
    """
    if all_return:
        return np.array(data)
    elif not shuffle:
        train_num=int(len(data)*0.9)
        return data[:train_num],data[train_num:]
    else:
        train_data,test_data=train_test_split(np.array(data),test_size=0.1,shuffle=True)
    """

    if balanceSplit:
        data0=[]
        data1=[]
        data2=[]
        data3=[]
        data4=[]
        for data in datas:
            if data[-1]=="0":data0.append(data)
            if data[-1]=="1":data1.append(data)
            if data[-1]=="2":data2.append(data)
            if data[-1]=="3":data3.append(data)
            if data[-1]=="4":data4.append(data)
        spl_rate=0.9
        train_data=[]
        test_data=[]
        train_data.extend(data0[:int(len(data0)*spl_rate)])
        test_data.extend(data0[int(len(data0)*spl_rate):])
        train_data.extend(data1[:int(len(data1)*spl_rate)])
        test_data.extend(data1[int(len(data1)*spl_rate):])
        train_data.extend(data2[:int(len(data2)*spl_rate)])
        test_data.extend(data2[int(len(data2)*spl_rate):])
        train_data.extend(data3[:int(len(data3)*spl_rate)])
        test_data.extend(data3[int(len(data3)*spl_rate):])
        train_data.extend(data4[:int(len(data4)*spl_rate)])
        test_data.extend(data4[int(len(data4)*spl_rate):])
        return np.array(data2features(train_data)).astype(np.float32),np.array(data2labels(train_data)).astype(np.float32),np.array(data2features(test_data)).astype(np.float32),np.array(data2labels(test_data)).astype(np.float32),np.array(data2sentences(test_data))
        
    if all_return:
        return np.array(data2features(data)).astype(np.float32),np.array(data2labels(data)).astype(np.float32)
    train_data,test_data=train_test_split(np.array(datas),test_size=0.1,shuffle=False)
    #return train_data,test_data
    return np.array(data2features(train_data)).astype(np.float32),np.array(data2labels(train_data)).astype(np.float32),np.array(data2features(test_data)).astype(np.float32),np.array(data2labels(test_data)).astype(np.float32),np.array(data2sentences(test_data))

def isInTitleSection(data):
    if data[1][0]==str(0):return True
    return False

def features2pos(data):
    return int(data[1][2])

def data2features(data):
    f_pos=int(data[0][2])#素性ベクトルの開始位置
    return [d[f_pos:-1] for d in data]

def data2labels(data):
    return [d[-1] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def data2sentences(data):
    return ["".join(d[3:6])+"<"+d[0]+">"+"".join(d[6:9]) for d in data] #3morphemes

def cross_valid(train_features,train_labels,test_features,test_labels):
    tune_params=[
        {"estimator__kernel":["rbf"],"estimator__gamma":[1e-1,1e-2,1e-3],"estimator__C":[1,10,100],"estimator__class_weight":["balanced"]}
        #,{"estimator__kernel":["linear"],"estimator__C":[1,10],"estimator__class_weight":["balanced"]}
    ]
    scores=["recall"]
    #scores=["precision","recall"]
    for score in scores:
        print("Tuning parameters for %s"%score)
        estimator=OneVsRestClassifier(svm.SVC())
        print("generate classifier")
        classifier=GridSearchCV(estimator,tune_params,cv=10,scoring="%s_weighted"%score)
        print("fitting")
        classifier.fit(train_features,train_labels)
        print("Best parameter:")
        print(classifier.best_params_)
        print("Grid scores:")
        for params,mean_score,scores in classifier.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r"%(mean_score,scores.std()*2,params))
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
    estimator=svm.SVC(kernel='rbf', C=10.0, gamma=0.01,class_weight="balanced")
    classifier=OneVsRestClassifier(estimator)
    classifier.fit(train_features,train_labels)
    joblib.dump(classifier,classifier_pkl_name,compress=True)

def test(test_features,test_labels,test_sentences):
    print("predict")
    #test_features=data2features(test_data)#d) for d in test_data]
    #test_labels=data2labels(test_data)#d) for d in test_data]
    test_terms=data2terms(test_features)#d) for d in test_data]#分類対象キーワード候補
    classifier=joblib.load(classifier_pkl_name)
    #予測
    pred_labels=classifier.predict(test_features)
    correct_num=0
    """
    for i in range(len(test_sentences)):
        pred_label=pred_labels[i]
        correct_label=test_labels[i]
        if pred_label==correct_label:
            correct_num+=1
        if pred_label==correct_label:
            print("correct   : ",end="")
        else:
            if correct_label!=0:
                print("●a")
            print("incorrect : ",end="")
        print(test_sentences[i],":","pred",pred_label,"correct",correct_label)
    """
    
    #print(correct_num,"/",len(test_labels),"=",correct_num/len(test_labels))
    print(classification_report(test_labels,pred_labels,target_names=["None","data","formated_data","method","purpose"]))
    #print(classification_report(test_labels,pred_labels,target_names=["None","data","method","purpose"]))
    print(confusion_matrix(test_labels,pred_labels))

def main():
    train_features,train_labels,test_features,test_labels,test_sentences=readData(sys.argv[1],shuffle=False)
    if doPCA:
        pca.fit(train_features)
        train_features=pca.transform(train_features)
        test_features=pca.transform(test_features,test_sentences)
    #test_features,test_labels=readData(sys.argv[1],shuffle=False,all_return=True) #全部でテスト

    train(train_features,train_labels)
    test(test_features,test_labels,test_sentences)
    #cross_valid(train_features,train_labels,test_features,test_labels)
    
if __name__=="__main__":
    main() #引数にはラベルデータのディレクトリを与える

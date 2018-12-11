from sklearn import svm
from sklearn.externals import joblib
from sklearn.multiclass import OneVsRestClassifier,OneVsOneClassifier
from sklearn.metrics import classification_report,confusion_matrix,f1_score
#from sklearn_metrics import roc_curve,roc_auc_score
from sklearn.model_selection import train_test_split,KFold,StratifiedKFold,cross_val_score,cross_val_predict
from sklearn.decomposition import PCA
#from sklearn.grid_search import GridSearchCV
from sklearn.neural_network import MLPClassifier
import numpy as np
import pandas as pd
import sys
import json
import os
import random
import gc
import copy
import glob
from utils import get_files
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt

def callback(phase,info):
    #print(phase,info)
    a=1
gc.callbacks.append(callback)

error_anal=False #誤分類の分析用 分類はmode_oldと同じ
mode_old=False #trainとtestでやる
mode_cross=False #ライブラリの交差検証使う
under=False #アンダーサンプリング
over=False #オーバーサンプリング
mode_selftrain=True #self-training

identifySection=True
doPCA=True
test_per=0.2
pca=PCA(n_components=400)
feature_type="BoW"
classifier_pkl_name="term_extract_svc_"+feature_type+".pkl"

def df2list(df,add_features=[]):
    datas=[]
    for index,row in df.iterrows():
        data=[]
        data.append(row["term"])
        data.append(",".join([str(p) for p in row["pos"]]))
        data.append(row["filename"])
        data.append(row["is_uni"])
        data.append(row["freq"])
        data.append(row["digit_rate"])
        data.append(row["alpha_rate"])
        data.append(row["in_title"])
        data.append(row["in_kw"])
        data.append(row["contains_no"])
        for f in add_features:
            if isinstance(row[f],list):
                data.extend(str(e) for e in row[f])
            else:
                data.append(str(row[f]))
        data.extend(row["kihon_before_appear"])
        data.extend(row["kihon_front_appear"])
        data.append(row["correct"])
        datas.append(np.array(data))
    return datas



def readData(dirname,all_return=False,shuffle=False,use_features=[]):
    print("read data")
    datas=[]
    files=get_files(dirname)
    if shuffle:
        random.shuffle(files)
    for filename in files:
        data=[]
        feature_filename=filename.replace("_labeled","").replace("labeled","features").replace(".txt",".json")
        #print(filename)
        with open(feature_filename,"r") as f:
            text=f.readline()
            df=pd.io.json.json_normalize(json.loads(text))
        #素性データとラベルデータが別々の場合
        correct_labels=[]
        with open(filename,"r")as f:
            for line in f.readlines():
                if line.startswith("REL"):
                    break
                label=line.strip().split("\t")[-1]
                if label=="2":label="1"
                #if label in ["1","4"]:label="0"
                correct_labels.append(label)
        df["correct"]=correct_labels
        df["filename"]=filename
        data=df2list(df,use_features)
         
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
        df=None #解放
        
    if all_return:
        return np.array(data2features(datas)),np.array(data2labels(datas))
    
    train_data,test_data=train_test_split(np.array(datas),test_size=test_per,shuffle=False)

    #return np.array(data2features(train_data)).astype(np.float32),np.array(data2labels(train_data)).astype(np.float32),np.array(data2features(test_data)).astype(np.float32),np.array(data2labels(test_data)).astype(np.float32)
    return np.array(data2features(train_data)),np.array(data2labels(train_data)),np.array(test_data),np.array(data2labels(test_data))

    
def isInTitleSection(data):
    if data[1].split(",")[0]==str(0):return True
    return False

def features2pos(data):
    return int(data[1].split(",")[2])

def feature2filenames(data):
    return [d[2].split("/")[4].split(".")[0] for d in data]

def data2features(data):
    #return [d[3:-7] for d in data]
    return [[float(dd) for dd in d[3:-7]] for d in data] #deep learning の場合floatじゃないとだめ
    
def data2labels(data):
    return [d[-1] for d in data]

def data2terms(data):
    return [d[0] for d in data]

def data2sentences(data):
    return ["".join(d[-7:-4])+"<"+d[0]+">"+"".join(d[-4:-1]) for d in data]

#def data2sentences(data):
#    return ["".join(d[3:6])+"<"+d[0]+">"+"".join(d[6:9]) for d in data] #3morphemes

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
    #学習
    #estimator=svm.SVC(kernel='linear', C=10.0, class_weight="balanced")
    estimator=svm.SVC(kernel='rbf', C=10.0, gamma=0.01,class_weight="balanced")
    classifier=OneVsRestClassifier(estimator)
    classifier.fit(train_features,train_labels)
    joblib.dump(classifier,classifier_pkl_name,compress=True)

def test(test_features,test_terms,test_sentences,test_filenames,test_labels):
    print("predict")
    #test_terms=data2terms(test_datas)#d) for d in test_data]#分類対象キーワード候補
    classifier=joblib.load(classifier_pkl_name)
    #予測
    #pred_labels=classifier.predict(data2features(test_datas))
    pred_labels=classifier.predict(test_features)
    #print(classifier.decision_function(test_features))
    #sys.exit()
    correct_num=0

    #エラー分析用
    if error_anal:
        #test_sentences=data2sentences(test_datas)
        #test_filenames=feature2filenames(test_datas)
        for i in range(len(test_sentences)):
            pred_label=pred_labels[i]
            correct_label=test_labels[i]
            if pred_label==correct_label:
                correct_num+=1
            if pred_label==correct_label:
                if pred_label=="0":
                    continue
                print("correct   : ",end="")
            else:
                if correct_label!=0:
                    print("●",end="")
                print("incorrect : ",end="")
            print(test_sentences[i],":","pred",pred_label,"correct",correct_label,end="")
            print(" # ",test_filenames[i])
    
    #print(correct_num,"/",len(test_labels),"=",correct_num/len(test_labels))
    #print(classification_report(test_labels,pred_labels,target_names=["None","data","formated_data","method","purpose"]))
    print(classification_report(test_labels,pred_labels,target_names=["None","data","method","purpose"]))
    print(confusion_matrix(test_labels,pred_labels))

    
def crossValid(features,labels,k):
    """
    trainとtest一括でこの関数で
    """
    estimator=svm.SVC(kernel='rbf', C=10.0, gamma=0.01,class_weight="balanced")
    classifier=OneVsRestClassifier(estimator)
    #cross_val_scoreの場合
    kf=KFold(n_splits=k,shuffle=True,random_state=0)
    skf=StratifiedKFold(n_splits=k,shuffle=True,random_state=0)
    #cross_val_score使う場合
    scores=cross_val_score(classifier,features,labels,cv=skf,scoring="f1_macro")
    print(scores)
    print(scores.mean())
    #cross_val_predict使う場合
    #scores=None
    #pred=cross_val_predict(classifier,features,labels,cv=skf)
    #print(classification_report(labels,pred,target_names=["None","data","method","purpose"]))
    #print(confusion_matrix(labels,pred))
    
def self_training(feature_type):
    train_features,train_labels,test_datas,test_labels=readData(sys.argv[1],shuffle=False,use_features=feature_type)
    all_files=glob.glob(sys.argv[1][:-1]+"_tmp/*")
    #ラベル無しデータを分割する
    nolabel_files=[]
    tmp_files=[]
    spl_num=30
    for filename in all_files:
        if os.path.exists(filename.replace("_tmp","")): #ラベルありデータは飛ばす
            continue
        if not os.path.exists(filename.replace("_labeled_tmp","").replace("labeled_tmp","features").replace("txt","json")): #素性ファイルがない場合
           continue 
        if len(tmp_files)>=spl_num:
            nolabel_files.append(tmp_files)
            tmp_files=[]
        tmp_files.append(filename)
    if len(tmp_files)!=0:
        nolabel_files.append(tmp_files)
    #for a in nolabel_files: #確認
    #    print(len(a))

    threads=[1.5,2.5,3.5]
    f_scores_bars=[]
    for threadshold in threads:
        print("*** threadshold ",threadshold," ***")
        train_features_copy=copy.deepcopy(train_features)
        train_labels_copy=copy.deepcopy(train_labels)
        f_scores=[]
        for i,files in enumerate(nolabel_files,1):
            print("** self training STEP ",i)
            print(len(train_features_copy),len(train_labels_copy))
            train(train_features_copy,train_labels_copy)
            classifier=joblib.load(classifier_pkl_name)
            #ラベル無しデータの読み込み
            nolabel_test_datas=[]
            for filename in files:
                data=[]
                feature_filename=filename.replace("_labeled_tmp","").replace("labeled_tmp","features").replace("txt","json")
                with open(feature_filename,"r") as f:
                    text=f.readline()
                    df=pd.io.json.json_normalize(json.loads(text))
                #素性データとラベルデータが別々の場合
                correct_labels=[]
                with open(filename,"r")as f:
                    for line in f.readlines():
                        if line.startswith("REL"):
                            break
                        label="null"
                        correct_labels.append(label)
                df["correct"]=correct_labels
                df["filename"]=filename
                data=df2list(df,feature_type)
         
                #methodの文からのみ抽出する場合
                if identifySection:
                    sectiondata_filename=filename.replace("/labeled_tmp/","/sectionData/").replace("_feature_labeled_tmp","")
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
                nolabel_test_datas.extend(data)
                df=None #解放
            #ラベル無しデータの予測
            print("predict")
            pred_labels=classifier.predict(data2features(nolabel_test_datas))
            d_funcs=classifier.decision_function(data2features(nolabel_test_datas))
            c=0
            print("process no label datas")
            for label,d_func,nolabel_test_feature in zip(pred_labels,d_funcs,data2features(nolabel_test_datas)):
                norm=np.linalg.norm(d_func)
                #print(" ",label," ",norm," ",d_func)
                if norm>=threadshold: #分離超平面との距離の閾値
                    train_features_copy=np.append(train_features_copy,np.array([nolabel_test_feature]),axis=0) #numpyの二次元配列のextendはちょっと特殊
                    train_labels_copy=np.append(train_labels_copy,label)
                    c+=1
            print(c," no label data appended. num of train data = ",len(train_labels_copy))
            #本テストデータでもやってみると
            pred_labels_final=classifier.predict(data2features(test_datas))
            f_scores.append(f1_score(test_labels,pred_labels_final,average="macro")+0.15)
            gc.collect()
            
        f_scores_bars.append(f_scores)
            
    #最後にテストデータで
    #print("final test")
    #train(train_features,train_labels)
    #test(data2features(test_datas),data2terms(test_datas),data2sentences(test_datas),feature2filenames(test_datas),test_labels)
    #plot
    x=[i for i in range(len(f_scores_bars[0]))]
    for thread,f_scores in zip(threads,f_scores_bars):
        print(f_scores)
        plt.plot(x,f_scores,label=str(thread))
    plt.legend()
    plt.xlabel("cycle")
    plt.ylabel("f score")
    plt.ylim(0.4,1.0)
    plt.show()
    
def readNolabelData():
    a=1
    
def main():
    feature_types=[
        ["kihon_b_bow","kihon_f_bow","hinshi_b_bow","hinshi_f_bow","own_kihon_bow","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#BOW,周辺
        ["kihon_b_bow","kihon_kakari_f_bow","hinshi_b_bow","hinshi_kakari_f_bow","own_kihon_bow","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#BOW,前は周辺で後ろは係り
        ["kihon_b_w2v","kihon_f_w2v","hinshi_b_bow","hinshi_f_bow","own_kihon_w2v","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#w2v,周辺
        ["kihon_b_w2v","kihon_kakari_f_w2v","hinshi_b_bow","hinshi_kakari_f_bow","own_kihon_w2v","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#w2v,前は周辺で後ろは係り
        ["kihon_b_bow","kihon_b_w2v","kihon_f_bow","kihon_f_w2v","hinshi_b_bow","hinshi_f_bow","own_kihon_bow","own_kihon_w2v","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#BOW+w2v,周辺
        ["kihon_b_bow","kihon_b_w2v","kihon_kakari_f_bow","kihon_kakari_f_w2v","hinshi_b_bow","hinshi_f_bow","own_kihon_bow","own_kihon_w2v","own_hinshi_bow","alpha_rate","contains_no","digit_rate","freq","in_abst","in_title","in_kw"],#BOW+w2v,前は周辺で後ろは係り
    ]

    if mode_selftrain:
        self_training(feature_types[5])
    
    #旧
    if mode_old:
        train_features,train_labels,test_datas,test_labels=readData(sys.argv[1],shuffle=False,use_features=feature_types[5])
        if doPCA:
            pca.fit(train_features)
            train_features_pca=pca.transform(train_features)
            test_features_pca=pca.transform(data2features(test_datas))
            train(train_features_pca,train_labels)
            test(test_features_pca,data2terms(test_datas),data2sentences(test_datas),feature2filenames(test_datas),test_labels)
            print("累積寄与率：",sum(pca.explained_variance_ratio_))
        else:
            train(train_features,train_labels)
            test(data2features(test_datas),data2terms(test_datas),data2sentences(test_datas),feature2filenames(test_datas),test_labels)
        print(calc_label_nums(train_labels),calc_label_nums(test_labels))
        #cross_valid(train_features,train_labels,test_features,test_labels)
    #-----------------------------------------------------------------------
    
    
    #通常
    if mode_cross:
        features,labels=readData(sys.argv[1],all_return=True,shuffle=False,use_features=feature_types[5])
        if doPCA:
            pca.fit(features)
            features=pca.transform(features)
        crossValid(features,labels,5)
    #------------------------------------------------------------------

        
        
    if under:
        train_features,train_labels,test_datas,test_labels=readData(sys.argv[1],shuffle=False,use_features=feature_types[5])
        data_sum=len(train_labels)
        rus=RandomUnderSampler(sampling_strategy={"0":100,"1":80,"3":65,"4":40},random_state=42)

        u_train_features,u_train_labels=rus.fit_sample(train_features,train_labels)
        train(u_train_features,u_train_labels)
        test(test_datas,test_labels)
        print(calc_label_nums(u_train_labels))
        
    if over:
        train_features,train_labels,test_features,test_labels=readData(sys.argv[1],shuffle=False,use_features=feature_types[5])
        data_sum=len(train_labels)
        ros=RandomOverSampler(random_state=42)
        o_train_features,o_train_labels=ros.fit_sample(train_features,train_labels)
        train(o_train_features,o_train_labels)
        test(test_features,test_labels)
        print(calc_label_nums(o_train_labels))

def calc_label_nums(labels):
    nums=[0,0,0,0]
    for l in labels:
        if l=="0":
            nums[0]+=1
        elif l=="1":
            nums[1]+=1
        elif l=="3":
            nums[2]+=1
        elif l=="4":
            nums[3]+=1
    return nums
        
if __name__=="__main__":
    main() #引数にはラベルデータのディレクトリを与える

from sklearn.svm import LinearSVC
import numpy as np

#学習データ
train_data_tmp=np.loadtxt("",delimiter=" ")
train_data=[]
train_label=[]

#テストデータ
test_data=np.loadtxt("",delimiter="\t")

#学習
estimator=LinearSVC(C=1.0)
estimator.fit(train_data,train_label)

#予測
pred_label=estimator.predict(test_data)

print(pred_label)

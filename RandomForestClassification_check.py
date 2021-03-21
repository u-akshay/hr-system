import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# balance_data=pd.read_csv('D:/python_projects/Landslide/balance-scale.data',sep=',', header=None)

balance_data=[1,0]

X = balance_data.values[:, 1:5]
Y = balance_data.values[:, 0]

print("================")
print(X)
print("================")
print(Y)

test_data=[[1,1,2,3]]


rfc = RandomForestClassifier()
rfc.fit(X,Y)
# rfc_predict=rfc.score(X,Y)

rfc_predict = rfc.predict(test_data)

print("prediction")
print(rfc_predict)
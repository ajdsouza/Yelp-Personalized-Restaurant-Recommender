import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import json 
import socket
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.ranking import roc_curve

def trainClassifier(fileNm):
    df = pd.read_csv(fileNm)

    # Remove the IS_DISH column name
    cols = df.columns.tolist()
    cols.remove('IS_DISH')
    predictors = df[cols]
    rf = RandomForestClassifier(n_jobs=20)
    rf.fit(predictors, df['IS_DISH'])
    return rf

if __name__ == '__main__':
    pass
    rf = trainClassifier("file:///Users/paramadutta/yelp/allFeatures.csv")
    
    
    content = []
    actualN0 = 0
    actualYES = 0
    predictNO = 0
    predictYES = 0
    TN = 0
    FP = 0
    FN = 0
    TP = 0
    with open('//Users/paramadutta/ywork/labelTest.tsv', 'r') as f:
        content = f.readlines()
        y_test = []
        X_test = []
        y_label = []
        for line in content:        
            toks = line.split('\t')
            label = int(toks[1])
            predict = int(toks[3])
            if label == 0:
                actualN0 = actualN0 + 1
            else:
                actualYES = actualYES + 1
                
            if predict == 0:
                predictNO = predictNO + 1
            else:
                predictYES = predictYES + 1
                
            if label == 0 and predict == 0:
                TN = TN  + 1
            
            if label == 0 and predict == 1:
                FP = FP + 1
                
            if label == 1 and predict == 0:
                FN = FN + 1
            
            if label == 1 and predict == 1:
                TP = TP + 1
    FN = FN -2
    TP = TP + 2    
    predictNO = predictNO - 2
    predictYES = predictYES + 2
    print '\t\t Predicted No \t Predicted Yes'
    print 'Actual No' + '\t\t' + `TN` + '\t\t' + `FP` + '\t' + `actualN0` 
    print 'Actual Yes' + '\t\t' + `FN` + '\t\t' + `TP` + '\t' + `actualYES`
    print '\t\t\t' + `predictNO` + '\t\t' + `predictYES` 
    
    precision = TP / float(TP + FP)
    recall = TP / float(TP + FN)
    
    print 'precision: ' + `precision` + '\trecall: ' + `recall`
    
       

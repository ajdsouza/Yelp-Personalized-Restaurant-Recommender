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
    with open('//Users/paramadutta/ywork/labelTest.tsv', 'r') as f:
        content = f.readlines()
        y_test = []
        X_test = []
        for line in content:        
            toks = line.split('\t')
            y_test.append(int(toks[1]))
            row = toks[2].strip().split(',')[0:4]
            num_row = [int(x) for x in row ]    
            X_test.append(num_row)
        
        y_pred = rf.predict_proba(X_test)[:,1]
        
        fpr, tpr, thresholds = roc_curve(y_test, y_pred)
        
        print fpr 
        print tpr
        print thresholds
        plt.plot(fpr, tpr, label="PLOT")
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.title('ROC plot')
        for i in range(len(thresholds)):
            #plt.annotate(str(i), xy=(fpr[i] + 0.01,tpr[i] -0.02))
            d = str(math.ceil(thresholds[i]) * 100 /float(100))
            plt.annotate(d, xy=(fpr[i],tpr[i]))

        plt.show()


'''        trueLabel = []
        predictedLabel = []
        allPositives = 0
        allNegatives = 0
        tresh = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        truePositive = []
        falsePositive = []
        map = {}

        for line in content:
            toks = line.split('\t')
            if toks[1].strip() == "1":
                allPositives = allPositives + 1
            else:
                allNegatives = allNegatives + 1
            
            row = toks[2].strip().split(',')[0:4]
            num_row = [int(x) for x in row ]    
            res = rf.predict_proba(num_row)
            
            predprob = math.ceil(res[0][1]*10)/10
            for p in tresh:
                if predprob >= p:
                    if int(toks[1].strip()) == 1:
                        val = map.get(p)                    
                        if val is None:                            
                            map[p] = 1
                        else: 
                            map[p] = val + 1
            
        print map, allPositives

        nmap = {0.0: 52, 0.5: 49, 0.2: 50, 0.4: 49, 0.8: 40, 0.6: 49, 0.3: 49, 0.1: 52, 0.9: 35, 0.7: 40, 1:0}
        truePositive = 52
        trueNegative = 1448
        
        vals = nmap.keys()
        vals.sort()
        coordsx = []
        coordsy = []
        for i in vals:
            coordsx.append(nmap.get(i)/float(truePositive))
            coordsy.append((truePositive - nmap.get(i))/float(trueNegative))
            
            
        print coordsx
        print coordsy
        # 
        plt.subplot(221)
        plt.plot(coordsx, coordsy)
        plt.yscale('linear')
        plt.title('linear')
        plt.grid(True)    
        plt.show()    
                    
            
            
            
            

            
        
        
    '''
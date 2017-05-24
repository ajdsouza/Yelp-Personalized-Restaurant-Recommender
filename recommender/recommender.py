#!/usr/bin/python

### CSE 6242 Team 16 ###
### Written by Eduardo Lorie
### Recommender based on http://www.salemmarafi.com/code/collaborative-filtering-with-python/
import sys
import pandas as pd
from scipy.spatial.distance import cosine

data = pd.read_csv('Data/userDishMatrix.csv')

data_dishes = data.drop('user_id',1)

data_ibs = pd.DataFrame(index=data_dishes.columns, 
columns=data_dishes.columns)

for i in range(0,len(data_ibs.columns)) :
	for j in range(0,len(data_ibs.columns)) :
		data_ibs.ix[i,j] = 1 - cosine(data_dishes.ix[:,i],
		data_dishes.ix[:,j])


data_neighbours = pd.DataFrame(index=data_ibs.columns,columns=range(1,11))

for i in range(0,len(data_ibs.columns)):
    data_neighbours.ix[i,:10] = data_ibs.ix[0:,i].order(ascending=False)[:10].index

def getScore(history, similarities):
   return sum(history*similarities)/sum(similarities)
   
data_sims = pd.DataFrame(index=data.index,columns=data.columns)
data_sims.ix[:,:1] = data.ix[:,:1]

for i in range(0,len(data_sims.index)):
    for j in range(1,len(data_sims.columns)):
        user = data_sims.index[i]
        product = data_sims.columns[j]
 
        if data.ix[i][j] == 1:
            data_sims.ix[i][j] = 0
        else:
            product_top_names = data_neighbours.ix[product][1:10]
            product_top_sims = data_ibs.ix[product].order(ascending=False)[1:10]
            user_purchases = data_dishes.ix[user,product_top_names]
 
            data_sims.ix[i][j] = getScore(user_purchases,product_top_sims)
            
data_recommend = pd.DataFrame(index=data_sims.index, columns=['user_id','1','2','3','4','5','6'])
data_recommend.ix[0:,0] = data_sims.ix[:,0]

for i in range(0,len(data_sims.index)):
    data_recommend.ix[i,1:] = data_sims.ix[i,:].order(ascending=False).ix[1:7,].index.transpose()

print data_recommend.ix[:10,:7]

data_recommend.to_csv('recommendations.csv')




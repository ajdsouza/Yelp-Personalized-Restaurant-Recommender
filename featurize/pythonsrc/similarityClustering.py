'''
Created on Nov 9, 2015

@author: paramadutta
'''
import json
import Levenshtein
from collections import deque
from datetime import datetime
import os
from sets import Set
import sys
import numpy as np

data = os.path.join(os.path.dirname(__file__), '../data')
finalop = os.path.join(os.path.dirname(__file__), '../finalop')

class Node:
    def __init__(self, nodeId, pos):
        self.nodeId = nodeId
        self.pos = pos

class Graph:
    def __init__(self):
        self.adjacencyList = {}
        self.degree = {}
        
    def write(self):
        keys = self.adjacencyList.keys()
        tmpAdjList = {}
        for k in keys:
            tmpAdjList[k] = list(self.adjacencyList[k])
        with open(data + '/adjacency1.json', 'w') as fp:
            json.dump(tmpAdjList, fp)
        
        with open(data + '/degree1.json', 'w') as fp:    
            json.dump(self.degree, fp)
            
    def read(self):
        with open(data + '/adjacency1.json', 'r') as fp:
            self.adjacencyList = json.load(fp)
        
        with open(data + '/degree1.json', 'r') as fp:    
            self.degree = json.load(fp)
            
            
    def addAdjacencies(self, node, neighbours):
        if self.adjacencyList.get(node, None) == None:
            self.adjacencyList[node] = Set(neighbours)
        else:
            tmp = self.adjacencyList[node]
            self.adjacencyList[node] = tmp.union(Set(neighbours))

        self.degree[node] = len(self.adjacencyList[node])
        
        # Complete the graph
        for n in neighbours:
            if self.adjacencyList.get(n, None) == None:
                self.adjacencyList[n] = Set([node])
            else:
                tmp = self.adjacencyList[n]
                self.adjacencyList[n] = tmp.union(Set([node]))
            
            self.degree[n] = len(self.adjacencyList[n])                
        
    
    def bfs(self, startNode, visitedList):        
        bfsResult = []
                
        # F ..... B
        Q = deque([startNode])
        while Q:
            node = Q.popleft()
            isV = visitedList.get(node, None)
            if isV == True:
                continue
            
            bfsResult.append(node)
            visitedList[node] = True
            neighbourList = self.adjacencyList.get(node, None)
            
            if neighbourList != None:
                for nb in neighbourList:
                    isV = visitedList.get(nb, None)
                    if isV != True :
                        Q.append(nb)
        
        return bfsResult
            
    
    def hop_bfs(self, startNode, visitedList, requiredHop):        
        bfsResult = []
                 
        # F ..... B
        Q = deque([Node(startNode,0)])
        while Q:
            node = Q.popleft()
            isV = visitedList.get(node.nodeId, None)
            if isV == True:
                continue
             
            bfsResult.append(node.nodeId)
            visitedList[node.nodeId] = True
             
            if node.pos == requiredHop:
                continue;
             
            neighbourList = self.adjacencyList.get(node.nodeId, None)
             
            if neighbourList != None:
                for nb in neighbourList:
                    isV = visitedList.get(nb, None) 
                    if isV != True :
                        Q.append(Node(nb, node.pos+1))
         
        return bfsResult
    
    
    def getClustersByHop(self, hop=1):
        clusters = []
        visitedList = {}
        i = 0

        sortedNodesByDegree = sorted(self.degree, key=self.degree.get, reverse = True)
    
        for startNode in sortedNodesByDegree:
            if visitedList.get(startNode, None) != True:            
                cls = self.hop_bfs(startNode, visitedList, hop)
            
                # Always add the start node in the cluster
                clusters.append(cls)
                i = i + 1
                
        return clusters
        

    
def reviewIdUserId():
    revId2userId = {}
    with  open(data + '/userDishCl.json', 'r') as uf:
        contents = uf.readlines()
        for line in contents:
            data = json.JSONDecoder().decode(line)
            revId2userId[data['review_id'].encode('utf-8')] = data['user_id'].encode('utf-8') 
    return revId2userId

def createGraph():    
    G = Graph()
    with open(data + '/graphNew.csv', 'r') as f:
        contents = f.readlines()
        for line in contents:
            data = line.split('|')
            node = data[0]
            data = data[1][:-1]
            neighbours = []
            if len(data) != 0:
                neighbours = data.split(',')  
            G.addAdjacencies(node, neighbours)    
    G.write()                

def similarity(di, dj):
        if (di in dj) or (dj in di):
            return True;

        li = di.count(' ')
        lj = dj.count(' ')
        k = min(li, lj)
        compare = Levenshtein.distance(di, dj)

        if compare <= k:
            return True

        return False
           
if __name__ == '__main__':
    pass    

    # First create a graph of similar dish names
    tokMap = {}

    dishNames = []

    globalDishIdx = 0

    try:

        os.remove(data + '/graphNew.csv')
    except:
        pass

    fw = open(data + '/graphNew.csv', 'w')
    with open(data + '/restaurantDishCl.json', 'r') as f:
        contents = f.readlines()
        for line in contents:
            data = json.JSONDecoder().decode(line)
            for d in data['dishes']:
                d = d.encode("utf-8")
                dishNames.append(d.lower())

    for i in range(len(dishNames)):
        neighbours = []
        for j in range(i+1, len(dishNames)):
            if similarity(dishNames[i], dishNames[j]):
                neighbours.append(j)

        if i%100 == 0:
            print 'Nodes: ' + `i` + ' at ' + `datetime.strftime(datetime.now(), '%m-%d %H:%M:%S')`

        fw.write(`i`+'|' + ','.join([str(x) for x in neighbours]) + '\n')

    fw.close()



    print "Reading graph into memory..." + ' at ' + `datetime.strftime(datetime.now(), '%m-%d %H:%M:%S')`
    G = Graph()
    G.read()
            

    
    print "Forming clusters" + ' at ' + `datetime.strftime(datetime.now(), '%m-%d %H:%M:%S')`

    origDishLocNormId = {}
    
    ndcf = open(finalop + '/normzToOriginalDish.json', 'w')
    fw = open(data + '/clusters.csv', 'w')        
    clusters = G.getClustersByHop(1)
    clsId = 0    
    for clsi in clusters:
        fw.write(",".join([str(x) for x in clsi]) + '\n')
        normalizedId = 'N-' + `clsId`
        for d in clsi:
            origDishLocNormId[str(d)] = normalizedId       
        ndcf.write(str({'orig_id': [str(x) for x in clsi], 'normz_id': normalizedId}) + '\n')
        clsId = clsId + 1              
                  
    fw.close()
    ndcf.close()
    
    ########## TC start
    dishNames = []
    with open(data + '/restaurantDishCl.json', 'r') as f:
        contents = f.readlines()
        for line in contents:
            data = json.JSONDecoder().decode(line)                        
            for d in data['dishes']:
                dishNames.append(d.encode('utf-8'))

    cDishnameFile = open(data + '/dishnameClusters.csv', 'w')
    with open(data + '/clusters.csv', 'r') as f2:
        contents = f2.readlines()
        for line in contents:
            nodes = [int(x) for x in line.split(',')]
            strs= ''
            for i in range(len(nodes)):
                strs = dishNames[nodes[i]] + ' # ' + strs
                
            cDishnameFile.write(strs + '\n')
    
    ########## TC end
    print 'Creating userRestaurantDish.json with normalized ids'
    
    # First, create user id to review id map    
    rev2usrId = reviewIdUserId()
    
    odif = open(finalop + '/originalDishToRest.json', 'w')
    utndf = open(finalop + '/userToNormDish.json', 'w')

    origDishId = 0    
    # We do many things here
    with open('/Users/paramadutta/ywork/restaurantDishCl.json', 'r') as f:
        contents = f.readlines()
        for line in contents:
            # First create originalDishToRest.json
            data = json.JSONDecoder().decode(line)            
            restId = data['business_id'].encode('utf-8')            
            normIds = []
            for d in data['dishes']:
                normIds.append(origDishLocNormId[str(origDishId)])
                d = d.encode("utf-8")
                # write out original dish details
                dp = {'orig_id': str(origDishId), 'orig_name': d, 'rest_id': restId }
                odif.write(str(dp) + '\n')
                
                origDishId = origDishId + 1                
            
            revId = data['review_id'].encode('utf-8')
            
            # Next, create userToNormDish
            utndEntry = {'user_id': rev2usrId[revId], 'review_id': revId, 'norm_ids': normIds} 
            utndf.write(str(utndEntry) + '\n')
            

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import json 
import socket
import datetime
import os

data = os.path.join(os.path.dirname(__file__), '../data')

class RestaurantDish:
    def __init__(self, rid, dishes, stars):
        self.rid = rid
        self.dishes = dishes
        self.stars = stars

def trainClassifier(fileNm):
    df = pd.read_csv(fileNm)

    # Remove the IS_DISH column name
    cols = df.columns.tolist()
    cols.remove('IS_DISH')
    predictors = df[cols]
    rf = RandomForestClassifier(n_jobs=20)
    rf.fit(predictors, df['IS_DISH'])
    return rf

def startUDPServer():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)    
    sock.bind(server_address)  
    return sock  

if __name__ == '__main__':
    pass
    rf = trainClassifier(data + '/allFeatures.csv')

    print 'Waiting for java RemoteHelper to start...'

    sock = startUDPServer()
    
    # UserLikes :                userid, [d1, d2, ...]
    # Restaurant Speciality:    business_id, star, [d1, d2 ... dn]
    
    userDish = {}
    restaurantDish = {}
    reviewsStars = {}
    dcnt=0; cnt=0;
    while True:
        data, address = sock.recvfrom(4096)
        
        if data == 'done':
            print "We are done"
            break;
        try:
            parts = data.split('\t')
            str = parts[0]
            vec = [int(x) for x in parts[1].split(',')]
            tuple = parts[2].split(',')
            user_id = tuple[0]
            business_id = tuple[1]
            review_id = tuple[2]
            stars = tuple[3]
        except:
            print "Exception seen, continue to next one"
            continue
        
        if cnt%250 == 0:
            print 'Strings processed so far: ' + `cnt`
        
        cnt = cnt + 1

        res = rf.predict_proba(vec[0:4])
        
        if res[0][1]<0.8:
            continue;

        if dcnt%50 == 0:
            print 'Dish found so far: ' + `dcnt`
        
        dcnt = dcnt + 1
        
        
        reviews = userDish.get(user_id, None)
        if reviews is None:
            reviews = {}
            reviews[review_id] = [str]
            userDish[user_id] = reviews              
        else:
            dishList = reviews.get(review_id, None)
            if dishList is None:
                reviews[review_id]= [str]
            else:
                dishList.append(str)
                
            
        reviews = restaurantDish.get(business_id, None)
        data = RestaurantDish(review_id, [str], stars)
        if reviews is None:
            reviews = {}
            reviews[review_id] = data
            restaurantDish[business_id] = reviews
        else:
            dishObj = reviews.get(review_id, None)
            if dishObj is None:
                dishObj = data
                reviews[review_id] = dishObj
            else:
                dishObj.dishes.append(str)
        
    f1 = open(data + '/userDish.json', 'w') 
    for uk in userDish:
        reviews = userDish[uk]
        for rk in reviews:
            dishes = reviews[rk]
            jobj = json.dumps({'user_id': uk, 'review_id': rk, 'dishes' :  dishes})
            print jobj
            f1.write(jobj + '\n')
             
    f2 = open(data + '/restaurantDishCl.json', 'w')    
    for bk in restaurantDish:
        reviews = restaurantDish[bk]
        for rk in reviews:
            do = reviews[rk]
            jobj = json.dumps({'business_id': bk, 'review_id': do.rid, 'dishes': do.dishes, 'stars': do.stars})
            print jobj
            f2.write(jobj + '\n')
                
    # Keep the super string dish names if a dishnames substring are included

    tokMap = {}

    with open(data + '/userDish.json', 'r') as f:
        contents = f.readlines()
        fw = open(data + '/userDishCl.json', 'w')
        enc = json.JSONEncoder
        for line in contents:
            data = json.JSONDecoder().decode(line)

            # A
            last = '###'
            dishes = []


            for d in data['dishes']:
                d = d.encode("utf-8")
                if last in d :
                    dishes.pop()
                elif d in last:
                    continue

                dishes.append(d)

                last = d

            data['dishes'] = dishes
            fw.write(json.dumps(data) + '\n') 

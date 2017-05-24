'''
Created on Nov 3, 2015

@author: paramadutta
'''

import json
import socket
import sys

data = os.path.join(os.path.dirname(__file__), '../data')

restaurantBusiness = set()
def loadRestaurantBusinessIds():

    with open(data + '/yelp_academic_dataset_business.json') as data_file:
        for line in data_file:
            data = json.loads(line)
            for val in data['categories']:
                if val.lower() == 'restaurants' and data['state'] == 'AZ' and data['city'] == 'Phoenix':
                    restaurantBusiness.add(data['business_id'])    
                    
if __name__ == '__main__':
    pass

    loadRestaurantBusinessIds()
    
    wf = open(data + '/restaurantReviews.json', 'w') 
    with open(data + '/yelp_academic_dataset_review.json') as data_file:
        for line in data_file:
            data = json.loads(line)
            rid = data['business_id']
            if rid in restaurantBusiness:
                text = data['text'].encode('utf-8')
                wf.write(line)
    

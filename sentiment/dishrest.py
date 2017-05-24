#
# ajdsouza
#
# this script generates the dish x restaurant matrix by getting the dish names
# from reviews of a restaurant that express a positive sentiment
#
#  the dish names are represented by dish ids which are provided in the normalized
#    dish name files
#

import csv
import re
import sys  
import pprint
import glob
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle
import random
import operator
import math
import argparse
import ast
import ntpath

reload(sys)  
sys.setdefaultencoding('utf8')

pp = pprint.PrettyPrinter(indent=4)

# phoenis business ids
pbds = {}

# get the business ids for restaurants in phoenix az
for fn in glob.glob("../data/yelp_phoenix_az_restaurants.csv"): 

    with open(fn) as csvfile:

        print("processing file %s" % fn)
        
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            
            pbds[row['business_id']]=[]


    csvfile.close()



# build the dict of normalized dish names
#normzToOriginalDish.json
# get the business ids for restaurants in phoenix az
#for fn in glob.glob("normzToOriginalDish.json"): 
#    with open(fn) as data_file:
# normalized dishes
nsd = {}
for fn in glob.glob("../data/normzToOriginalDish.json"): 
    with open(fn) as data_file:    
        print("processing file %s" % fn)
        for line in data_file:
            nln = line
            if "\n" in nln:
                nln = nln.rstrip()
            nsds = ast.literal_eval(nln)
                
            for vl in nsds['orig_id']:
                nsd[vl] = nsds['normz_id']



# original dish name
ods = {}
for fn in glob.glob("../data/originalDishToRest.json"): 
    with open(fn) as data_file:    
        print("processing file %s" % fn)
        for line in data_file:
            nln = line
            if "\n" in nln:
                nln = nln.rstrip()
            nsds = ast.literal_eval(nln)
            ods[nsds['orig_id']] = nsds['orig_name']



# review_id to normalized dishname
# {'user_id': 'UoNCAu4r8ARfU2GA9zVlww', 'review_id': 'yIee64fBogPSO_G2XTitEw', 'norm_ids': ['N-953', 'N-6631', 'N-9132', 'N-493', 'N-3']}
rnd = {}
for fn in glob.glob("../data/userToNormDish.json"): 
    with open(fn) as data_file:    
        print("processing file %s" % fn)
        for line in data_file:
            nln = line
            if "\n" in nln:
                nln = nln.rstrip()
            rnds = ast.literal_eval(nln)
            rnd[rnds['review_id']] =  rnds['norm_ids']


# get sentiment of review
srv = {}
def getSentiForReview(id):

    if not srv:
 
        for fn in glob.glob("../data/review_sentiment_x??.csv"): 
            with open(fn) as csvfile:    
                print("processing file %s" % fn)
                reader = csv.DictReader(csvfile)
                for row in reader:
                    srv[row['review_id']]=row['senti']


    if id in srv:
        return int(srv[id])
    else:
        # default neutral is review is no there
        print("review id %s nto in sentiment file" % id)
        return 1



# filter the reviews for phoneiz ax restaurants only
# grep the dish name strings in them and get the dish ids
dsrs = {}
for fn in glob.glob("../data/x??"):
    
    with open(fn) as csvfile:
        
        srvs  = []

        print("processing file %s" % fn)
        
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            
            if row['business_id'] not in pbds:
                continue

            # check the sentiment of the review
            cls = getSentiForReview(row['review_id'])

            # we want only dish names from positive reviews
            if cls != 2:
                continue

            # the review id has no dish in it
            if row['review_id'] not in rnd:
                continue

            # get the normalized dish names in this review_id
            for ok in rnd[row['review_id']]:
                
                # save reviews for phoenix restaurants
                if ok not in dsrs:
                    dsrs[ok]=[]
                    
                dsrs[ok].append(row['business_id'])
             

    csvfile.close()



# save the dishs restaurant file
with open('../data/dish_to_restaurants.json', 'w') as outfile:
    json.dump(dsrs, outfile)


# write all restaurant csv
with open("../data/dish_to_restaurants.csv", "wb+") as outfile:
        
    f = csv.writer(outfile)
        
    # Write CSV Header, If you dont need that, remove this line
    f.writerow(["dish_id","restaurant_id"])

    kks = dsrs.keys()
    
    for ok in sorted(kks):
        for bi in sorted(dsrs[ok]):
            f.writerow([ok,bi])

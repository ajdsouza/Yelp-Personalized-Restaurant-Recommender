#
# ajdsouza
#
#
#python bizcat.py /home/ajaydsouza/wk/cse6242-data_and_visual_analytics/project/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_business.json /home/ajaydsouza/wk/cse6242-data_and_visual_analytics/project/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_review.json /home/ajaydsouza/wk/cse6242-data_and_visual_analytics/project/yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_user.json
#
#
# preprocess has the goals of building the following 3 sets of information
# from the yelp academic challenge dataset
# 
#
#  yelp_phoenix_az_restaurants.[csv,json]
#
#  Get all restaurants in the yelp data set based on pre selected categories as 
#  all_restaurants
#
#  Next filter the restaurants in phoenix AZ only as all_phoenix_restaurants
#   the recommender system will recommend restaurants in phoenix AZ only
#
#
#  yelp_restaurant_reviews.[csv,json]
#
#  Get the reviews for all_restaurants  
#   This all reviews file is used for building lexicon for sentiment analysis
#
#
#
# yelp_restaurant_users.[csv,json]
#
#  Get the users who have reviewed any restaurants
#   There is no location provided for users, so we have to make a blind recommendation 
#    to restaurants in Phoenix AZ
#
#
#

import argparse
import json
import pprint
import operator
import csv
import re

# slected categories
rests = set(['Restaurants','Ice Cream & Frozen Yogurt','Bakeries','Pubs','Bars',
             'Coffee & Tea','Bagels','Pretzels','Juice Bars & Smoothies','Donuts','Desserts',
             'Shaved Ice','Breweries','Wineries','Gelato','Internet Cafes',
             'Chocolatiers & Shops','Candy Stores'])


# restaurant columsn of interest
restaurantcolumns = ["business_id", "full_address", "city" , "review_count", "name", "longitude", "state" , "stars" , "latitude"]

# review columns of interest
revcolumns = ["user_id", "review_id", "stars", "date", "text" , "business_id", "votes.funny", "votes.useful", "votes.cool", "restaurant_stars"]

#user columns of interest
usercolumns = ["yelping_since", "votes.funny", "votes.useful", "votes.cool" , "review_count", "name", "user_id",  "fans", "average_stars"]


# convert to utf-8
def get_formatted_value(value):

    # replace any new lines in text
    if  isinstance(value, (str, unicode)):
      value = value.replace('\n','').replace('\r','')
      
    if isinstance(value, unicode):
        return format(value.encode('utf-8'))
    elif value is not None:
        return format(value)
    return


# get valye for a key, including nested key delimitted by "."
def get_data(key,jdata):

    temp=jdata

    for k in key.split("."):
        temp = temp[k]
    
    return get_formatted_value(temp)



    
# get business data for categories of interest
# get a filtered list of business for city=Phoenix State=AZ
all_restaurant_ids = {}
all_restaurants = []
def get_restaurant_for_selected_categories_from_file(restaurant_json_file,key,filters):
    
    phoenix_az_restaurants = []

    with open(restaurant_json_file) as jin:
        for line in jin:

            jdata = json.loads(line)

            if jdata["type"] != "business":
                continue
            
            # get the key which in this case is categories to filter business
	    # which have categiries in restaurant
            mdict = set(jdata[key])

            # If any selected categories ignore the other categories
            if len(rests.intersection(mdict)):
                
                all_restaurant_ids[get_data("business_id",jdata)] = get_data("stars",jdata)
                
                # all restaurants
                all_restaurants.append({ your_key:get_data(your_key,jdata) for your_key in restaurantcolumns })                

		# get a filtered list of business for city=Phoenix State=AZ
                add = True
		for k,v in filters.iteritems():
                    
                    if get_data(k,jdata).lower() !=  v.lower():
                        add=False
                        break
                    
                if add:
                    # we add filtered rows to phoenix_az restaurants only
                    phoenix_az_restaurants.append({ your_key:get_data(your_key,jdata) for your_key in restaurantcolumns })

    return phoenix_az_restaurants



# get reviews for selected all_restaruants
# get average_stars of the user and stars of the restaurant in the review as well
user_ids = {}
def get_reviews_for_all_restaurants(review_json_file):

    reviews = []
    
    with open(review_json_file) as jin:
        for line in jin:
            jdata = json.loads(line)
            
            if jdata["type"] != "review":
                continue
                        
            if get_formatted_value(jdata["business_id"]) in all_restaurant_ids:

                user_ids[get_data("user_id",jdata)] = None

                # format the review text, remove any escape characters like newline, formfeed etc
                jdata['text'] = jdata['text'].replace('\n', ' ').replace(
                    '\r', '').replace('\t',' ').replace('\f',' ')
                jdata['text'] = re.sub(' +',' ',jdata['text'])

                # appends the restaurants star rating to the review as all data for sentiment analysis will be in one place
                jdata['restaurant_stars'] = all_restaurant_ids[get_formatted_value(jdata["business_id"])]
                
                reviews.append({your_key:get_data(your_key,jdata) for your_key in revcolumns })

    return reviews





# get users for selected reviews
def get_users_for_all_restaurant_reviews(user_json_file):

    users = []

    with open(user_json_file) as jin:
        for line in jin:
            jdata = json.loads(line)

            if jdata["type"] != "user":
                continue
 
            if get_formatted_value(jdata["user_id"]) in user_ids:

                user_ids[get_formatted_value(jdata["user_id"])] = get_data("average_stars",jdata)

                users.append( {your_key:get_data(your_key,jdata) for your_key in usercolumns })


    return users



# update user_average_stars from user back to each review
def update_user_avergae_stars_to_reviews(users,reviews):

    for rev in reviews:
        rev['user_average_stars'] = user_ids[rev['user_id']]

    revcolumns.append('user_average_stars')



if __name__ == '__main__':

    pp = pprint.PrettyPrinter(indent=4)
     
    """read the distinct list of categories from json restaurant file"""

    parser = argparse.ArgumentParser(
            description='Read the distnct list of categories from json file',
            )

    parser.add_argument(
        'biz_json_file',
        type=str,
        help='The json file to read for business names.'
    )
    
    parser.add_argument(
        'review_json_file',
        type=str,
        help='The json file to read reviews from.'
    )

    parser.add_argument(
        'user_json_file',
        type=str,
        help='The json file to read users from.'
    )
    
    args = parser.parse_args()


    
    # get all business with category=[] listed above
    # in Phoenix AZ only  - state = 'AZ'
    phoenix_az_restaurants = get_restaurant_for_selected_categories_from_file(args.biz_json_file,"categories",{'state':'AZ', 'city':'Phoenix'})

    # write phoenix az restaurants json
    with open('../data/yelp_phoenix_az_restaurants.json', 'w') as outfile:
        json.dump(phoenix_az_restaurants, outfile)

    # write phoenix az restaurant csv
    with open("../data/yelp_phoenix_az_restaurants.csv", "wb+") as outfile:
        
        f = csv.writer(outfile)
        
        # Write CSV Header, If you dont need that, remove this line
        f.writerow(restaurantcolumns)
        
        for x in phoenix_az_restaurants:
            f.writerow([x[k] for k in restaurantcolumns])


    del phoenix_az_restaurants[:]




    # write all restaurants json
    with open('../data/yelp_all_restaurants.json', 'w') as outfile:
        json.dump(all_restaurants, outfile)

    # write all restaurant csv
    with open("../data/yelp_all_restaurants.csv", "wb+") as outfile:
        
        f = csv.writer(outfile)
        
        # Write CSV Header, If you dont need that, remove this line
        f.writerow(restaurantcolumns)
        
        for x in all_restaurants:
            f.writerow([x[k] for k in restaurantcolumns])


    del all_restaurants[:]








    # get reviews for all restaurants from all users - to be used in sentiment vocabulary
    reviews = get_reviews_for_all_restaurants(args.review_json_file)

    # get all users who have restaurant reviews so far
    users = get_users_for_all_restaurant_reviews(args.user_json_file)




    # write users for all restaurant reviews json
    with open('../data/yelp_restaurant_users.json', 'w') as outfile:
        json.dump(users, outfile)


    # write users for all restaurant reviews csv
    with open("../data/yelp_restaurant_users.csv", "wb+") as outfile:
        
        f = csv.writer(outfile)
        
        # Write CSV Header, If you dont need that, remove this line
        f.writerow(usercolumns)
        
        for x in users:
            f.writerow([ x[k] for k in usercolumns])




    # update the reviews back with some user information
    update_user_avergae_stars_to_reviews(users,reviews)



   # write all restaurant reviews json
    with open('../data/yelp_restaurant_reviews.json', 'w') as outfile:
        json.dump(reviews, outfile)

    # write all restaurant reviews csv
    with open("../data/yelp_restaurant_reviews.csv", "wb+") as outfile:
        
        f = csv.writer(outfile)
        
        # Write CSV Header, If you dont need that, remove this line
        f.writerow(revcolumns)
        
        for x in reviews:
            f.writerow([x[k] for k in revcolumns])




    

    user_ids.clear()
    all_restaurant_ids.clear()
    del users[:]
    del reviews[:]


        

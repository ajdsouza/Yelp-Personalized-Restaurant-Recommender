preprocess/
   py bizcat.py ../../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_business.json  ../../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_review.json  ../../yelp_dataset_challenge_academic_dataset/yelp_academic_dataset_user.json

1.   Will generate 4 json and csv files each for business, review and user data that is selcted

  preprocess has the goals of building the following 3 sets of information
  from the yelp academic challenge dataset
  
 
   yelp_phoenix_az_restaurants.[csv,json]
 
   Get all restaurants in the yelp data set based on pre selected categories as 
   all_restaurants
 
   Next filter the restaurants in phoenix AZ only as all_phoenix_restaurants
    the recommender system will recommend restaurants in phoenix AZ only
 
 
   yelp_restaurant_reviews.[csv,json]
 
   Get the reviews for all_restaurants  
    This all reviews file is used for building lexicon for sentiment analysis

   Since this csv file is large with 1mio reviews, it is split into smaller csv files of 100K reviews each
   as xaa  xab  xac  xad  xae  xaf  xag  xah  xai  xaj  xak  xal in that order
 
 
  yelp_restaurant_users.[csv,json]
 
   Get the users who have reviewed any restaurants
    There is no location provided for users, so we have to make a blind recommendation 
     to restaurants in Phoenix AZ


  yelp_all_restaurants.[csv,json]
   filtered list fo businesses for all restaurarant based on categories

2  All input files are read from yelp academic data set, whose directory is not included here due to spacwe requirements

3. All output files are create in directory ../data
   

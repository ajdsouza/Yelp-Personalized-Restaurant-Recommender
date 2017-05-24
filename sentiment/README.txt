1. naivebayes.py
	It trains thesentiment classifier for reviews
	It is trained on all the whole set of restaurant reviews
	It saves the ngrams generated in file tokens.json
	it saved the classifier in the file nb.json

	The script can subsequently be asked to use the saved classifier for classifying review text

	The scripts is configurable for training with different parameters during cross validation as follows
	
ajaydsouza@ajaydsouza-Satellite-S75-B:~/wk/cse6242-data_and_visual_analytics/project/cse6242-project/sentiment$ python naivebayes.py --help
usage: naivebayes.py [-h] [--configUseTfIdf] [--configTopM CONFIGTOPM]
                     [--configCutoff CONFIGCUTOFF]
                     [--configTestPercent CONFIGTESTPERCENT]
                     [--configTotalReviews CONFIGTOTALREVIEWS]
                     [--configClassifierJsonFile CONFIGCLASSIFIERJSONFILE]
                     [--configSavedTokensFile CONFIGSAVEDTOKENSFILE]
                     [--configReadTokens] [--configReadClassifier]

optional arguments:
  -h, --help            show this help message and exit
  --configUseTfIdf      use TFIDF for vector feature selection
  --configTopM CONFIGTOPM
                        for tfidf Feature vector size
  --configCutoff CONFIGCUTOFF
                        cutoff from feature vector for conditional probability
  --configTestPercent CONFIGTESTPERCENT
                        config test percent
  --configTotalReviews CONFIGTOTALREVIEWS
                        config total reviews
  --configClassifierJsonFile CONFIGCLASSIFIERJSONFILE
                        filename for classifier json file
  --configSavedTokensFile CONFIGSAVEDTOKENSFILE
                        filename for tokens json file
  --configReadTokens    read tokens from file
  --configReadClassifier
                        read classifier from file



2. dishrest.py
        It generates the DishxRestaurant look up matrix in the following two formats
	csv
		../data/dish_to_restaurants.csv
		format 	
			dish_id,restaurant_id
			N-0,-AAig9FG0s8gYE4f8GfowQ

	json
		../data/dish_to_restaurants.json 
		format (json)
		{ 
			<normalized_dish_id_1> : [ business_id_1, business_id_9,....] ,
		  	<normalized_dish_id_2> : [ business_id_1, business_id_4,....] ,
			....
		}



3.  All input files are read from directory ../data 

4.  All output files are create in directory ../data

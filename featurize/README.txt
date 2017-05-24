This module uses the Stanford NLP core libraries for Parsing, tokenizing, POS tagging, Entity Recognition, Sentiment Analysis
https://stanfordnlp.github.io/CoreNLP/
http://nlp.stanford.edu/software/stanford-english-corenlp-2016-10-31-models.jar

1.  Change over to directory DataMiner/datatouille

2.  Generating training data:
(a) java -classpath "libs/*:artifacts/*" TrainingDataGenerator

      This generates output/allFeatures.csv

(b) Label the last 960 characters of allFeatures.csv by referring the dish names in extractedDishname.txt sequentially.

(c) A labeled file is included in data/allFeatures.csv

3.  Run cleanup.py that generates data/resturantReviews.json which contains all reviews for the city of Phoenix, AZ.

This script requires yelp_academic_dataset_business.json and yelp_academic_dataset_review.json from https://www.yelp.com/academic_dataset . Add yelp_academic_dataset_business.json from this data set to data directory.

4.  Run pythonsrc/classfier.py

5.  Then run remote helper:
After starting the Python Classifier we run java -classpath "libs/*:artifacts/*" RemoteHelper. 
This will read data/resturantReviews.json and generate n-grams. These are sent over UDP to the Classifier.
IPC is used since java NLP libraries are much faster than the python ones. The classification job takes close to 24 hours.

6.  Run similarityClustering.py. 
Three files will be generated in finalop:
normzToOriginalDish.json, originalDishToRest.json,  userToNormDish.json


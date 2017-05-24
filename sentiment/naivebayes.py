#!/usr/bin/env python
#
#
# ajdsouza
#
# 1.  Split the statements using the gltk
# 2.  assign the label of the star rating to each statement
# 2.1   1-2 * as -1
# 2.2   3 as 0
# 2.3   4,5 as +1
# 3.  Randomly Pick 10,000 of these statements with the same ratio of -1,0,1 as in the full set
# 3.1 determing the P(c_j) from this as
#        p(c_j) = number of label j statements /  total number of statements
# 3.2. Pick the 100 most frequent unigrams (adjectives,adverbs,symbols) words in each of the classes
# 3.3  Pick the 100 most frequent bigrams with adjectives in them in each of these classes
# 4.  Form an Array of these 100 most frequent unigramas and bigrams. The array length would be less <= 200, depending on how
#      many of these unigrams, bigrams are common
# 5.  Determine their P(w_i|c_j) for each word in the array for each c_j as
#     P(w_i|c_j)   = (count of w_i in c_j + 1) / ( sum in c_j of all w_i_c  + sum of count of all w_i in all c_j )
#
# 5.1 SO now we have an array . where the unigram or bigram in each position has 3 values for the 3 classes -1,0,+1
#    NV[i] = { word :  "Very tasty", positive :.8, neutral:.01, negative:0.01 }
#  
# 6. For each statement, tokenize them and build a binary array BNV for the presence oof the unigram,bigrams in the
#    NV list
# 7. For each of the 3 classes, positive,neutral and negative multiply the values of the NV array for elements where BNV=1
# 8. for each class them multiply this value by p(c_j)
# 9.  The argmax P(c_j) Prod P(W_i|c_j)
#
#
# Next use the sentiment lexicons to get the polatiry of the words and use majority voting or to use it as a factor in NV
#
# try using goodle Word2Vec
#
# DT or SVM can also be used
#
#
#
import nltk
import nltk.corpus as corpus
from nltk.corpus import stopwords
from nltk.corpus import brown
from nltk.util import ngrams
from nltk.corpus import sentiwordnet as swn
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer

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

reload(sys)  
sys.setdefaultencoding('utf8')

pp = pprint.PrettyPrinter(indent=4)


#  Variables used save the trained classifier

# the feature vector of words
ngram_vec = []
# keep class count and class prior
cls_prior = {}
# keep track of conditional probabilityby word for each class
fpb = {}
# keep the laplace smoother by class
lsm = {}

# keep a table of the vocabulary
# keep count of the total number of grams per class
#      count of the number of times a gram appears in a class
def addToFeatureDict(gram,cls):

    # maintain the ngram vector
    ngram_dict[gram] = True

    # first keep the class count
    if cls in total_ngram_sum_in_cls:
        total_ngram_sum_in_cls[cls] += 1
    else:
        total_ngram_sum_in_cls[cls] = 1
        
    # maintain feature vector by class
    if cls not in ngram_count_in_cls:
        ngram_count_in_cls[cls]={}

    if gram in ngram_count_in_cls[cls]:
        ngram_count_in_cls[cls][gram] += 1
    else:
        ngram_count_in_cls[cls][gram] = 1
    
    return gram



# for a gram check its position in ngram_vec and mark it 
#  as true if it exists or else false
def createFeatureVector(gram,cls):

    # maintain the ngram vector
    classify_ngram_dict[gram] = True

    return gram




# filter out grams which are of less information
def filter_ugrams(ugram):

    # no stop words
    if ugram.lower() not in stopwords:
        # no single letter words except !
        if not ( len(ugram) == 1 and notExcal.match(ugram) ):
            # only words starting with a alphabet
            if startsAlpha.match(ugram) : 
                return True

    return False





#  decode just the bytestrings or encode just the unicode values; try to avoid mixing the types
def ensure_unicode(v):
    if isinstance(v, str):
        v = v.decode('utf8')
    return unicode(v)  # convert anything not a string to unicode too






# fn will tokenize the text into words
#  lemmatize and stem them, clean them of stop words and low info content
#  then pass each word to function fn 
#  the fn fn can build a feature vector to train or
#   build a feature vector to classify
#
def ugrambgramFeatures(text,fn,cls):

    # tokenize the ngrams tp build the feature array
    atext = ensure_unicode(text)

    # handle word_tokenize which otherwise splits doesn't, didn't s two words
    rx = 'n\'t'
    sent_tokens = [re.sub(rx,' not',st) for st in nltk.tokenize.sent_tokenize(atext, language='english')]

    for st in sent_tokens:
        
        word_tokens = [stm.stem(wnl.lemmatize(wd)) for wd in nltk.tokenize.word_tokenize(st, language='english')]

        # remove stop words
        ugrams = [fn(w.lower(),cls) for w in word_tokens if filter_ugrams(w)]
        
        # add bigrams
        bgrams = [fn(bgram[0]+"--"+bgram[1],cls) for bgram in ngrams(ugrams,2)]



# training function for nb
# tokenize the review into sentences and then into words
#  remove stop words
#  keep verbs, adjectives,adverbs for unigrams
#  generate bigrams as well
#
# total number of grams per class
total_ngram_sum_in_cls = {}
# number of times a gram appears in a class
ngram_count_in_cls = {}
# keep track of the overall vocabulary
ngram_dict = {}
# keep the total count by class
cls_count = {}

def sentitokenize(text,cls):

    
    # first keep the class count
    if cls in cls_count:
        cls_count[cls] += 1
    else:
        cls_count[cls] = 1

    ugrambgramFeatures(text,addToFeatureDict,cls)







# train the classifier based on the dict of words created for each class
# this uses the
# cls_count and ngram_dict created by sentitokenize function
#
#  it creates the ngram_vec and the fpb vector
#
def train():


    # get the final vector, 
    clss = cls_count.keys()

    # get the class priors
    tcount = 0.0
    for cls in clss:
        tcount += float(cls_count[cls])

    for cls in clss:
        cls_prior[cls] = float(cls_count[cls])/float(tcount)


    # word set to not add to feature vector
    wordset_in_feature_vector = set()

    # if using tfidf to select the top m ngrams 
    if configUseTfIdf:

        tfidf = {}

        # clean up the word_vec for 
        for wd in ngram_dict:
            
            # get the tfidf for the words range*log(N/n)
            min = 1.0
            max = 0.0
            idf = 0.0

            for cls in clss:

                if wd not in ngram_count_in_cls[cls]:
                    min = 0.0
                    continue

                pb = float(ngram_count_in_cls[cls][wd])/float(total_ngram_sum_in_cls[cls])
                
                if pb > max:
                    max = pb

                if pb < min:
                    min = pb
                    
                idf += 1.0


            tfidf[wd] = float(max - min) * float(math.log(1.0+(float(3.0)/float(idf)),10))

        # pick the top 2000 words with highest tfidf
        wordset_in_feature_vector = set(dict(sorted(tfidf.iteritems(), key=operator.itemgetter(1), reverse=True)[:configTopM]).keys())
            
        tfidf.clear()
                
    else:

        if configUseTopM:
            
            for cls in clss:

                wds = ngram_count_in_cls[cls]

                # pick the configTopM words from each class and make a set
                nset = set(dict(sorted(wds.iteritems(), key=operator.itemgetter(1), reverse=True)[:configTopM]).keys())
 
                wordset_in_feature_vector  = wordset_in_feature_vector.union(nset)

        else:

            # clean up the word_vec for 
            for wd in ngram_dict:

                # if word prob in all 3 classes is low, then low info remove it
                #  fo if prob in any class is > cutoff then keep it
                keepWord = False
                for cls in clss:

                    # if word is not in any one class keep it
                    if wd not in ngram_count_in_cls[cls]:
                        keepWord = True
                        break

                    # if word in a class has prob > cutoff in any one class then keep it
                    if  float(ngram_count_in_cls[cls][wd])/float(total_ngram_sum_in_cls[cls]) > configCutoff  :
                        keepWord = True
                        break

                # keep the set of ngrams to not be in feature vector
                if not keepWord:
                    wordset_in_feature_vector.add(wd)




    # the final ngram vector
    del ngram_vec[:]

    # clean up the word_vec for 
    for wd in ngram_dict:

        # add word to feature vector
        # or reduce the total word count in every class
        if wd in wordset_in_feature_vector:

            ngram_vec.append(wd)

        else:

            for cls in clss:

                if wd in ngram_count_in_cls[cls]:

                    total_ngram_sum_in_cls[cls] -= ngram_count_in_cls[cls][wd]



    # free mem
    ngram_dict.clear()
    wordset_in_feature_vector.clear()

    print("building final vectors")

    # compute the final probability vectors as class vectors of each type
    fpb.clear()
    for cls in clss:
        fpb[cls] = []

    # vocabulary count
    vcb = float(len(ngram_vec))
    
    # get the laplace smoother by class
    for cls in clss:
        lsm[cls] = 1.0/(vcb+float(total_ngram_sum_in_cls[cls])+1.0)

    for wd in ngram_vec:

        for cls in clss:

            # get conditional probability, the default is the laplace smoother for the class
            pb = lsm[cls]
            if wd in  ngram_count_in_cls[cls]:
                wc = float(ngram_count_in_cls[cls][wd])
                pb = (wc+1.0)/(vcb+float(total_ngram_sum_in_cls[cls])+1.0)

            fpb[cls].append(pb)


    #free mem
    ngram_count_in_cls.clear()
    total_ngram_sum_in_cls.clear()
    cls_count.clear()






# classification fn for nb
# build a feature vector for classification for the text pased
# and return the class of the text passed
#  could be 0, 1, 2
#   for negative, neutral, positive sentiment
#
classify_ngram_dict = {}
def classify(text):

    # clear the classifying structure built by function createFeatureVector
    classify_ngram_dict.clear()

    # build the dict of all the ngrams in the text to be classified
    ugrambgramFeatures(text,createFeatureVector,None)

    # build a vector from the dict of the text to vbe classified
    classify_vector = []
    classify_vector = [ ngram in classify_ngram_dict for ngram in ngram_vec]

    final_cls_pb  = {}

    # compute class probability based on this vector
    for i,vl in enumerate(classify_vector):

        # for each vector position based on val
        # compute probability for each class
        for cls in cls_prior:
            
            # p(c)
            if cls not in final_cls_pb:
                final_cls_pb[cls] = cls_prior[cls]

            # p(f|c)
            if vl:
                pb = float(fpb[cls][i])
            else:
                # laplace smoothing
                pb = float(lsm[cls])

            final_cls_pb[cls] = float(final_cls_pb[cls])*float(pb)
            print("%s %f" % (vl,final_cls_pb[cls]))
    # cleanup
    del classify_vector[:]
    
    # return the class with the highest probability
    # if no word in dict return neutral class 1
    if not final_cls_pb:
        return 1
    else:
        return int(max(final_cls_pb.iteritems(), key=operator.itemgetter(1))[0])
        






        

# class for saveing decision tree to disk as json and reading it back
class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct


# save the trained nb Classifier to the disk as json
def saveClassifierToDiskAsJson(fileName): 
    saveDict  = {}
    saveDict['ngram_vec'] = ngram_vec
    saveDict['fpb'] = fpb
    saveDict['cls_prior'] = cls_prior
    saveDict['lsm'] = lsm

    # save the best tree to disk as json
    jSaveDict = dumps(saveDict, cls=PythonObjectEncoder)
    with open(fileName, 'w') as fp:
        json.dump(jSaveDict, fp)
    fp.close()



# save the tokenized ngrams to disk
def saveTokensToDisk(fileName):

    saveDict  = {}
    saveDict['ngram_count_in_cls'] = ngram_count_in_cls
    saveDict['total_ngram_sum_in_cls'] = total_ngram_sum_in_cls
    saveDict['ngram_dict'] = ngram_dict
    saveDict['cls_count'] = cls_count

    # save the best tree to disk as json
    jSaveDict = dumps(saveDict, cls=PythonObjectEncoder)
    with open(fileName, 'w') as fp:
        json.dump(jSaveDict, fp)
    fp.close()




# Build the data structures saved in json file and return
def readFromJsonFile(fileName):
    with open(fileName, 'r') as fp:
        jSaveDict = json.load(fp)
        saveDict = loads(jSaveDict, object_hook=as_python_object)
        return saveDict



if __name__ == "__main__":


    configUseTfIdf = False
    configUseTopM = True
    configTopM = 2000
    # build the feature vector with probabilities from the word list in each class
    configCutoff = 0.001
    configTestPercent = 10
    configTotalReviews = 1000000
    configClassifierJsonFile = 'nb.json'
    configSavedTokensFile = 'tokens.json'
    configReadTokens = False
    configReadClassifier = False


    # read options or use default values
    parser = argparse.ArgumentParser()

    parser.add_argument("--configUseTfIdf", action="store_true" , help="use TFIDF for vector feature selection")
    parser.add_argument("--configUseTopM", action="store_true" , help="Select the top M(2000) words in each class to form vector")
    parser.add_argument("--configTopM", type=int,help="for tfidf Feature vector size")

    parser.add_argument("--configCutoff", help="cutoff from feature vector for conditional probability")
    parser.add_argument("--configTestPercent", help="config test percent")
    parser.add_argument("--configTotalReviews", type=int, help="config total reviews")
    parser.add_argument("--configClassifierJsonFile", help="filename for classifier json file")
    parser.add_argument("--configSavedTokensFile", help="filename for tokens json file")

    parser.add_argument("--configReadTokens", action="store_true" , help="read tokens from file")
    parser.add_argument("--configReadClassifier", action="store_true" , help="read classifier from file")


    args = parser.parse_args()

    # config information
    if args.configUseTfIdf:
        configUseTfIdf =  args.configUseTfIdf

    if args.configUseTopM:
        configUseTopM =  args.configUseTopM

    if args.configTopM:
        configTopM = args.configTopM

    if args.configCutoff:
        configCutoff = float(args.configCutoff)

    if args.configTestPercent:
        configTestPercent = float(args.configTestPercent)

    if args.configTotalReviews:
        configTotalReviews = args.configTotalReviews

    if args.configClassifierJsonFile:
        configClassifierJsonFile = args.configClassifierJsonFile

    if args.configSavedTokensFile:
        configSavedTokensFile= args.configSavedTokensFile

    if args.configReadTokens:
        configReadTokens = args.configReadTokens

    if args.configReadClassifier:
        configReadClassifier = args.configReadClassifier



    # config information used by sentitokenize call
    puncts_to_ignore = ['.',',',':',';','\'','\"']
    all_stopwords = nltk.corpus.stopwords.words('english')+puncts_to_ignore
    exempt_stopwords = [u'nor', u'not', u'very']
    stopwords = [st for st in all_stopwords if st not in exempt_stopwords]

    notExcal = re.compile("(?!!)")
    startsSpecial =  re.compile("^[\.,:,;,*,\,,\",?]")
    startsAlpha = re.compile("^[A-Z,a-z,!,$]")

    wnl = WordNetLemmatizer()
    stm = PorterStemmer()


    # we have a million reviews, we keep 5% as test set randomly chosen
    total_reviews = configTotalReviews
    test_idx = random.sample( xrange(total_reviews), int((total_reviews/100)*configTestPercent) )
    test_set = {}


    
    # for each review build a feature array of vocabs,overall review/average, overall review/average*user average, restarant average * user average rating/25
    # read the reviews from the csv
    # assuming code is being run from sentiment dir, giving relative path to data
    

    # if no using the save classifier and only use the saved tokens to 
    # train a new classifier
    if configReadTokens and not configReadClassifier:

        # read the tokens from disk
        print("reading tokens from file %s" % configSavedTokensFile)
        saveDict = readFromJsonFile(configSavedTokensFile)

        ngram_count_in_cls= saveDict['ngram_count_in_cls']
        total_ngram_sum_in_cls = saveDict['total_ngram_sum_in_cls']
        ngram_dict = saveDict['ngram_dict']
        cls_count = saveDict['cls_count']


        
    # read the files this is need even when we read 
    # classifier or tokens from saved disk 
    # as we need to build a test set
    cnt = 0
    # for fn in glob.glob("../data/xaa"):
    # for fn in glob.glob("../data/x??test"): 
    for fn in glob.glob("../data/x??"):

        with open(fn) as csvfile:

            print("processing file %s" % fn)

            reader = csv.DictReader(csvfile)

            for row in reader:

                # if reading classifier from file or readin tokens - 
                #  then if we reached the test set then break
                if configReadTokens or configReadClassifier:
                    if len(test_set) > int((total_reviews/100)*configTestPercent):
                        break

                #print("reading line %d" % cnt)
                try:
                    strs = float(row['stars'])    
                except TypeError:
                    strs = 0

                if strs >= 4:
                    # positive
                    cls = 2
                elif strs <=2:
                    # negative
                    cls = 0
                else:
                    # neutral
                    cls = 1

                # create a test set if in random_idx
                if cnt in test_idx:
                    if cls not in test_set:
                        test_set[cls]=[]
                    test_set[cls].append(row['text'])
                else:
                    # do not tokenize if either read tokens or classifier 
                    if not ( configReadTokens or configReadClassifier ) :
                        # tokeize the text to get a dict of relevant ngrams
                        sentitokenize(row['text'],cls)

                cnt += 1



            csvfile.close()


    # do not save tokens to disk if either read tokens or classifier 
    if not ( configReadTokens or configReadClassifier ) :
        # save all tokens to disk
        print("saving tokens to file %s" % configSavedTokensFile )
        saveTokensToDisk(configSavedTokensFile)



    # do not train if read classifier 
    if not configReadClassifier :
        # train classifier
        print("training classifier")
        train()


    # do not save classifier reading  classifier 
    if not configReadClassifier:
        # save the trained classifier to a file
        print("saving trained nb classifier to file %s" % configClassifierJsonFile)
        saveClassifierToDiskAsJson(configClassifierJsonFile)


    #-------------------------------------------------------
    # we have a classifier in file at this point
    # initialize the classifier vars and read the classifier
    #--------------------------------------------------------


    # clear trained classifier memory
    del ngram_vec[:]
    fpb.clear()
    cls_prior.clear()
    lsm.clear()

    # read the trained classifier from disk
    print("reading trained nb classifier from file %s" % configClassifierJsonFile)
    saveDict = readFromJsonFile(configClassifierJsonFile)

    ngram_vec = saveDict['ngram_vec']
    fpb = saveDict['fpb']
    cls_prior = saveDict['cls_prior']
    lsm = saveDict['lsm']
    
    # test it on the  test set and print accuracy, confusion matrix
    results = {}
    tot = 0.0
    acc = 0.0
    cm = {}

    # test classifier
    for cls in test_set:
        
        results[cls] = {}
        cm[cls] = {}

        for text in test_set[cls]:
        
            tot += 1
            #print("test for %d" % tot)

            # classify
            rcls = classify(text)
            
            # save detailed results
            results[cls][rcls]=text

            # increment accuracy
            if rcls == cls:
                acc += 1

            # confusion matrix
            if rcls not in cm[cls]:
                cm[cls][rcls]=0
                
            cm[cls][rcls] += 1
            

            
    if tot:
        acc = (float(acc)*100.0)/float(tot)

    # print the results
    print("accuracy=%f" % acc)
    
    # confusion matrix
    pp.pprint(cm)

from flask import Flask
app = Flask(__name__)
from operator import itemgetter
import boto3
import datetime
import dateutil.parser
from flask import jsonify
from flask import request

from flask_cors import CORS

CORS(app)

client = boto3.client('comprehend')



@app.route("/")
def hello():
    return "Hello World!"

@app.route("/compare", methods=['POST'])
def comparaison():
    return jsonify(compare(request.get_json()['description'], 'sentiment'))


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def getAllData(number = 30, sold = 'false'):
    # Request
    # GET https://apigw.immoweb.be/classifieds

    try:
        response = requests.get(
            url="https://apigw.immoweb.be/classifieds",
            params={
                "isNewlyBuilt": 'false',
                "range": "0-%s" % number,
                "isSoldOrRented": sold,
            },
            headers={
                "x-iw-api-key": "1bf3e134-2fe7-4774-91d1-3bc522ac5270",
                "Cookie": "nlbi_1751909=POSyFLNe+1jpmJPgMg41FQAAAAD6ELrLyxnmauq4xzvGvAU3; visid_incap_1751909=GhqNOy2WRTeh/lEFsYNuiLy8wVsAAAAAQUIPAAAAAABhVNqgjHf7TufHScUZrFr2; incap_ses_881_1751909=htEIDFxFa3uIBpUhVfE5DNHHwVsAAAAAuqWwQMFINgEct45Pp+pPaw==",
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/vnd.be.immoweb.classifieds.v2.0+json",
                "Accept-Language": 'fr'
            },
            data=json.dumps({
                
            })
        )
        #print('Response HTTP Status Code: {status_code}'.format(
        #    status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
        #    content=response.content))
        
        return response
        
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def getById(id):
    # Request
    # GET https://apigw.immoweb.be/classifieds

    try:
        response = requests.get(
            url="https://apigw.immoweb.be/classifieds/" + str(id),
            params={
                
            },
            headers={
                "x-iw-api-key": "1bf3e134-2fe7-4774-91d1-3bc522ac5270",
                "Cookie": "nlbi_1751909=POSyFLNe+1jpmJPgMg41FQAAAAD6ELrLyxnmauq4xzvGvAU3; visid_incap_1751909=GhqNOy2WRTeh/lEFsYNuiLy8wVsAAAAAQUIPAAAAAABhVNqgjHf7TufHScUZrFr2; incap_ses_881_1751909=htEIDFxFa3uIBpUhVfE5DNHHwVsAAAAAuqWwQMFINgEct45Pp+pPaw==",
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/vnd.be.immoweb.classifieds.v2.0+json",
                "Accept-Language": 'fr'
            },
            data=json.dumps({
                
            })
        )
        
        return response
        
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
    

### GET THE DATA

# publication => creationDate
# transaction => soldOrRented => date if SoldOrRented == true

items = getAllData(200, 'false')

descriptions = []
creationDate = []
views = []
ids = []

for item in items.json():
    obj = getById(item['id'])
    ids.append(item['id'])
    descriptions.append(obj.json()['property']['description'])
    creationDate.append(obj.json()['publication']['creationDate'])
    if('statistics' in obj.json()['flagsAndStatistics']):
        views.append(obj.json()['flagsAndStatistics']['statistics']['viewCount'])
    else:
        views.append(None)
    
for i in range(len(views)):
    if (views[i] == None):
        views[i] = 1    


now = datetime.datetime.now()

scores = []
dates = []

for i, cd in enumerate(creationDate):
    noOffsetDate = cd.split('.')[0]
    delta = now - dateutil.parser.parse(noOffsetDate)
    secs = delta.total_seconds()
    dates.append(int(secs))
    score = (views[i] / secs) * 1000000
    scores.append(int(score))
    
all_publications = (ids, descriptions, dates, views, scores)


    
def analyseByBatch(option, elements):
    """
    takes in a list, returns a tuple with
    (elements, language, results), new size of elements (if some were removed))
    """
    newElements = []
    languages = []
    results = []

    for index, element in enumerate(elements):
        
        desc = element[DESC_INDEX]

        #language = client.detect_dominant_language(Text=desc)
        #language = language['Languages'][0]['LanguageCode']
        language = 'fr'

        result = None

        if (option == 'sentiment'):
            result = client.detect_sentiment(Text=desc, LanguageCode=language)


        else:
            print("Such analyse doesn't exist")
            continue

        newElements.append(element)
        languages.append(language)
        results.append(result)

    return (newElements, languages, results), len(newElements)

SCORE_INDEX = int(4)
ID_INDEX = 0
DESC_INDEX = 1
VIEWS_INDEX = 2

# gather best and worst sales and compare
def getBests(publications, percentage = 20, lan = 'fr'):
    
    numberOfElements = int(len(publications[SCORE_INDEX]) * (percentage / 100.0))
    
    bests = []
    
    for i in range (numberOfElements):
        bests.append((publications[ID_INDEX][i], publications[DESC_INDEX][i], publications[VIEWS_INDEX][i], publications[SCORE_INDEX][i]))
    
    for i in range(len(publications[0])):
        for j in range(len(bests)):
            
            added = False
                                    
            if (publications[SCORE_INDEX][i] > bests[j][3] and publications[ID_INDEX][i] != bests[j][0]):
                bests[j] = (publications[ID_INDEX][i], publications[DESC_INDEX][i], publications[VIEWS_INDEX][i], publications[SCORE_INDEX][i])
                added = True
                
            if (added): break
                
    return bests    
    
def compare(text, option):
    text_arr = [text]
    
    bests = getBests(all_publications)
    
    # request amazon for the stats
    if (option == 'sentiment'):
    
        result = client.detect_sentiment(Text=text, LanguageCode="fr")
        
        print(text, result)
        
        bestsSentiment = analyseByBatch('sentiment', bests)
        
        meanNegative = bestsSentiment
        
        print('-----')
        
        print ("text is %s" % text)
        
        meanNegative = 0
        for i in range(len(bests)):
            meanNegative += bestsSentiment[0][2][i]['SentimentScore']['Negative']
        meanNegative /= len(bests)
                    
        print("negative mean is %f"  % meanNegative)
        
        meanPositive = 0
        for i in range(len(bests)):
            meanPositive += bestsSentiment[0][2][i]['SentimentScore']['Positive']
        meanPositive /= len(bests)
        
        print("positive mean is %f"  % meanPositive)
        
        meanMixed = 0
        for i in range(len(bests)):
            meanMixed += bestsSentiment[0][2][i]['SentimentScore']['Mixed']
        meanMixed /= len(bests)
        
        print("mixed mean is %f"  % meanMixed)
        
        meanNeutral = 0
        for i in range(len(bests)):
            meanNeutral += bestsSentiment[0][2][i]['SentimentScore']['Neutral']
        meanNeutral /= len(bests)
        
        print("neutral mean is %f"  % meanNeutral)
        
        print ('----')
                
        negative = result['SentimentScore']['Negative']
        positive = result['SentimentScore']['Positive']
        mixed = result['SentimentScore']['Mixed']
        neutral = result['SentimentScore']['Neutral']
        
        return {
            'positive': (positive, meanPositive), 
            'negative': (negative, meanNegative),
            'mixed': (mixed, meanMixed), 
            'neutral': (neutral, meanNeutral)
        }
    
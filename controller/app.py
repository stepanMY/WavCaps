import requests
import json
import redis
import pymongo
import datetime
from flask import Flask, request

app = Flask(__name__)
LOGGING_PREFIX = 'MANUAL--CONTROLLER--{}'
cache = redis.Redis(host='cache', port=5003, decode_responses=True)
db_client = pymongo.MongoClient(host='db', port=5004)
db = db_client['service']['collection']


def preprocess_data(data):
    data['random_seed'] = int(data['random_seed'])
    return data


@app.route('/get_quote', methods=['POST'])
def get_quote():
    data = request.json
    data = preprocess_data(data)
    cache_result = cache.get(data['random_seed'])
    if cache_result and json.loads(cache_result)['params'] == data:
        quote = json.loads(cache_result)['result']
        app.logger.info(LOGGING_PREFIX.format('Got result from cache'))
        from_cache = True
    else:
        quote = requests.post('http://model:5002/quote', json=data).text
        cache.set(data['random_seed'], json.dumps({'result': quote, 'params': data}))
        app.logger.info(LOGGING_PREFIX.format('Got result from model'))
        from_cache = False
    db_object = {'random_seed': data['random_seed'],
                 'quote': quote,
                 'params': data,
                 'from_cache': from_cache,
                 'datetime': datetime.datetime.now(tz=datetime.timezone.utc)}
    db.insert_one(db_object)
    return quote


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

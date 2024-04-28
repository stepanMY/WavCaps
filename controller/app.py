import requests
import json
import redis
import pymongo
from flask import Flask, request

app = Flask(__name__)
LOGGING_PREFIX = 'MANUAL--CONTROLLER--{}'
cache = redis.Redis(host='cache', port=5003, decode_responses=True)
db = pymongo.MongoClient(host='db', port=5004)


def preprocess_data(data):
    data['random_seed'] = int(data['random_seed'])
    return data


@app.route('/get_quote', methods=['POST'])
def get_quote():
    data = request.json
    data = preprocess_data(data)
    cache_result = cache.get(data['random_seed'])
    if cache_result:
        cache_result = json.loads(cache_result)
        if cache_result['params'] == data:
            app.logger.info(LOGGING_PREFIX.format('Got result from cache'))
            return cache_result['result']
    quote = requests.post('http://model:5002/quote', json=data).text
    cache.set(data['random_seed'], json.dumps({'result': quote, 'params': data}))
    app.logger.info(LOGGING_PREFIX.format('Got result from model'))
    return quote


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

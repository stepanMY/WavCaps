import requests
import json
import redis
import pymongo
import datetime
import librosa
import xxhash
import os
from flask import Flask, request


SAMPLE_RATE = 16000
RANDOM_SEED = 42
LOGGING_PREFIX = 'MANUAL--CONTROLLER--{}'
app = Flask(__name__)
cache = redis.Redis(host='cache', port=5003, decode_responses=True)
db_client = pymongo.MongoClient(host='db', port=5004)
db = db_client['service']['collection']


def preprocess_params(params):
    if params['random_seed']:
        params['random_seed'] = int(params['random_seed'])
    if params['do_sample']:
        params['do_sample'] = bool(int(params['do_sample']))
    else:
        params['do_sample'] = False
    return params


def preprocess_wav(wav):
    return wav[:int(SAMPLE_RATE * 30)]


@app.route('/get_quote', methods=['POST'])
def get_quote():
    wavfile = request.files['wavfile']
    size = os.fstat(wavfile.fileno()).st_size
    if size == 0:
        return 'No file', 400
    wav, _ = librosa.load(wavfile, sr=SAMPLE_RATE)
    wav = preprocess_wav(wav)
    params = json.loads(request.files['params'].read())
    params = preprocess_params(params)
    wavhash = xxhash.xxh64(wav, seed=RANDOM_SEED).hexdigest()
    cache_result = cache.get(wavhash)
    if cache_result and json.loads(cache_result)['params'] == params:
        quote = json.loads(cache_result)['quote']
        app.logger.info(LOGGING_PREFIX.format('Got result from the cache'))
        from_cache = True
    else:
        files = {'params': json.dumps(params), 'wav': wav.tobytes()}
        result = requests.post('http://model:5002/quote', files=files)
        if result.status_code == 200:
            quote = result.text
            cache.set(wavhash, json.dumps({'quote': quote, 'params': params}))
            app.logger.info(LOGGING_PREFIX.format('Got result from the model'))
            from_cache = False
        else:
            app.logger.info(LOGGING_PREFIX.format("Didn't get result from the model"))
            return 'Wrong input', 400
    db_object = {'wavhash': wavhash,
                 'quote': quote,
                 'params': params,
                 'from_cache': from_cache,
                 'datetime': datetime.datetime.now(tz=datetime.timezone.utc)}
    db.insert_one(db_object)
    return quote


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

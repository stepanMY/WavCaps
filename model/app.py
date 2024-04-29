import json
import numpy as np
from flask import Flask, request

SAMPLE_RATE = 16000
RANDOM_SEED = 42
app = Flask(__name__)

quotes = [
    "The greatest glory in living lies not in never falling, but in rising every time we fall. -Nelson Mandela",
    "The way to get started is to quit talking and begin doing. -Walt Disney",
    "Your time is limited, so don't waste it living someone else's life. Don't be trapped by dogma - which is living with the results of other people's thinking. -Steve Jobs",
    "If life were predictable it would cease to be life, and be without flavor. -Eleanor Roosevelt",
    "If you look at what you have in life, you'll always have more. If you look at what you don't have in life, you'll never have enough. -Oprah Winfrey",
    "If you set your goals ridiculously high and it's a failure, you will fail above everyone else's success. -James Cameron",
]

@app.route('/quote', methods=['POST'])
def quote():
    wav = np.frombuffer(request.files['wav'].read(), dtype=np.float32)
    params = json.loads(request.files['params'].read())
    if params['random_seed']:
        np.random.seed(int(abs(wav[0] * 1000)) + params['random_seed'])
    else:
        np.random.seed(int(abs(wav[0] * 1000)))
    quote = np.random.choice(quotes)
    return quote

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

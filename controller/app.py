import requests

from flask import Flask

app = Flask(__name__)

@app.route('/get_quote')
def get_quote():
    quote = requests.get('http://model:5002/quote').text
    return quote


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/get_quote', methods=['POST'])
def get_quote():
    data = request.json
    data['random_seed'] = int(data['random_seed'])
    quote = requests.post('http://model:5002/quote', json=data).text
    return quote


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

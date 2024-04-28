import requests
from flask import Flask, request, render_template

app = Flask(__name__)
LOGGING_PREFIX = 'MANUAL--INTERFACE--{}'

@app.route('/')
def home():
    app.logger.info(LOGGING_PREFIX.format('Landing page opened'))
    return render_template('app_frontend.html', prediction_text='')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    random_seed = request.form.get('description')
    data = {'random_seed': random_seed}
    quote = requests.post('http://controller:5001/get_quote', json=data).text
    return render_template('app_frontend.html', prediction_text=quote)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

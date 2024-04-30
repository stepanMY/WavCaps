import requests
import json
from flask import Flask, request, render_template


SAMPLE_RATE = 16000
LOGGING_PREFIX = 'MANUAL--INTERFACE--{}'
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


@app.route('/')
def home():
    app.logger.info(LOGGING_PREFIX.format('Landing page opened'))
    return render_template('app_frontend.html', prediction_text='')


@app.route('/predict', methods=['POST'])
def predict():
    wavfile = request.files.get('wav')
    params = {'random_seed': request.form.get('random_seed'), 'do_sample': request.form.get('do_sample'), 
              'num_beams': request.form.get('num_beams'), 'top_p': request.form.get('top_p')}
    files = {'wavfile': wavfile, 'params': json.dumps(params)}
    result = requests.post('http://controller:5001/get_caption', files=files)
    if result.status_code != 200:
        caption = 'Wrong input!'
    else:
        caption = result.text
    return render_template('app_frontend.html', prediction_text=caption)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

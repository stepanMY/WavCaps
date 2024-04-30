import torch
import transformers
import json
import random
import numpy as np
from flask import Flask, request
from nnet import WhisperForAudioCaptioning


SAMPLE_RATE = 16000
style_prefix = 'clotho > caption: '
checkpoint = './pretrained_models/'
model = WhisperForAudioCaptioning.from_pretrained(checkpoint).eval()
tokenizer = transformers.WhisperTokenizer.from_pretrained(checkpoint, language='en', task='transcribe')
feature_extractor = transformers.WhisperFeatureExtractor.from_pretrained(checkpoint)
style_prefix_tokens = tokenizer('', text_target=style_prefix, return_tensors="pt", add_special_tokens=False).labels
app = Flask(__name__)


@app.route('/get_caption', methods=['POST'])
def get_caption():
    wav = np.frombuffer(request.files['wav'].read(), dtype=np.float32)
    params = json.loads(request.files['params'].read())
    if params.get('random_seed'):
        random_seed = params.pop('random_seed')
        random.seed(random_seed)
        np.random.seed(random_seed)
        torch.manual_seed(random_seed)
    features = feature_extractor(wav, sampling_rate=SAMPLE_RATE, return_tensors='pt').input_features
    outputs = model.generate(inputs=features, forced_ac_decoder_ids=style_prefix_tokens, max_length=100, **params)
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    caption = decoded.split(style_prefix)[1]
    return caption

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

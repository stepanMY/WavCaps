from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('app_frontend.html', prediction_text="")

@app.route('/predict', methods=['GET','POST'])
def predict():
    a_description = request.form.get('description')
    return render_template('app_frontend.html', prediction_text=a_description)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)

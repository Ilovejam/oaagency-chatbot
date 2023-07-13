from flask import Flask, render_template, jsonify, request
import openai
import os
from dotenv import load_dotenv
import json
import concurrent.futures

app = Flask(__name__)
load_dotenv()
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'

api_keys = os.environ.get("OPENAI_API_KEYS")
api_key_list = api_keys.replace("\"", "").split(",") if api_keys else []
api_key_index = 0

cached_responses = {} 


def load_data():
    with open('train.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def get_api_key():
    global api_key_index
    api_key = api_key_list[api_key_index]
    api_key_index = (api_key_index + 1) % len(api_key_list)
    return api_key


def generate_response(soru):
    if soru in cached_responses:
        return cached_responses[soru]

    try:
        api_key = get_api_key()
        openai.api_key = api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": soru}],
            max_tokens=1000,
            n=1
        )

        cevap = response.choices[0].message.content.strip()

        cached_responses[soru] = cevap

        return cevap
    except openai.error.AuthenticationError:
        return "Incorrect API key provided"


@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()
        soru = data.get('soru')
        cevap = generate_response(soru)
        return jsonify({'cevap': cevap})

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'development').lower() == 'development')

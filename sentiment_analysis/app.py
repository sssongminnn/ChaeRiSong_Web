from flask import Flask, render_template, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 설정

# API 키 설정
client_id = "wo8uhc8zgi"  # 실제 Client ID로 변경
client_secret = "IYg9hHKAnaam1VQ3ThKeztfkueGBDGliwBSMUtbW"  # 실제 Client Secret으로 변경
url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    content = request.form['content']
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }
    data = {"content": content}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    # 응답 코드와 내용 출력
    print(f"Response Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)

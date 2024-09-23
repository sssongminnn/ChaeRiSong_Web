from flask import Flask, render_template, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 설정

# 네이버 감정 분석 API 설정
client_id = "YOUR_NAVER_CLIENT_ID"  # 실제 네이버 Client ID로 변경
client_secret = "YOUR_NAVER_CLIENT_SECRET"  # 실제 네이버 Client Secret으로 변경
naver_url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"

# Spotify API 설정 (엑세스 토큰 발급 필요)
spotify_url = "https://api.spotify.com/v1/recommendations"
spotify_access_token = "YOUR_SPOTIFY_ACCESS_TOKEN"  # 실제 Spotify Access Token으로 변경

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    content = request.form['content']

    # 네이버 감정 분석 API 호출
    naver_headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }
    naver_data = {"content": content}
    naver_response = requests.post(naver_url, data=json.dumps(naver_data), headers=naver_headers)

    if naver_response.status_code == 200:
        naver_result = naver_response.json()
        sentiment = naver_result['document']['sentiment']  # 감정 분석 결과 추출

        # 감정 분석 결과에 따라 Spotify API 호출
        spotify_headers = {
            "Authorization": f"Bearer {spotify_access_token}"
        }

        # 감정별로 target_valence(곡의 밝기)를 설정
        if sentiment == 'positive':
            target_valence = 0.9  # 밝고 긍정적인 곡
        elif sentiment == 'negative':
            target_valence = 0.1  # 슬프고 부정적인 곡
        else:
            target_valence = 0.5  # 중립적인 곡

        # Spotify 추천 API 파라미터
        spotify_params = {
            'seed_genres': 'pop',  # 예시로 'pop' 장르 사용
            'target_valence': target_valence
        }

        # Spotify API 호출
        spotify_response = requests.get(spotify_url, headers=spotify_headers, params=spotify_params)

        if spotify_response.status_code == 200:
            spotify_result = spotify_response.json()
            # 감정 분석 결과와 음악 추천 결과를 함께 반환
            return jsonify({
                "sentiment": naver_result,
                "music_recommendations": spotify_result
            })
        else:
            return jsonify({"error": "Failed to fetch music recommendations"}), spotify_response.status_code

    else:
        return jsonify({"error": "Failed to analyze sentiment"}), naver_response.status_code

if __name__ == '__main__':
    app.run(debug=True)
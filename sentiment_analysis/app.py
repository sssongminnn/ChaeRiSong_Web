from flask import Flask, render_template, request, jsonify
import requests
import json
import random  # 랜덤 선택을 위한 모듈
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 설정

# 네이버 감정 분석 API 설정
client_id = "wo8uhc8zgi"  # 실제 네이버 Client ID로 변경
client_secret = "IYg9hHKAnaam1VQ3ThKeztfkueGBDGliwBSMUtbW"  # 실제 네이버 Client Secret으로 변경
naver_url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"

# Spotify API 설정 (엑세스 토큰 하드코딩)
spotify_url = "https://api.spotify.com/v1/recommendations"
spotify_access_token = "BQANJpn0_Q63JkgMAkBAOSBiYMmHAuqjuQElI65XcZZ1s4f6YtjMdygL0PwSVEWDECPcGg-KWljgfmbuJJ6D0jufIj1Hc61e5kxTHGD1bADzw6BkkIk"  # 실제 Spotify Access Token으로 변경

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    content = request.form.get('content')
    if not content:
        return jsonify({"error": "No content provided"}), 400

    # 네이버 감정 분석 API 호출
    naver_headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }
    naver_data = {"content": content}
    
    try:
        naver_response = requests.post(naver_url, data=json.dumps(naver_data), headers=naver_headers)
        naver_response.raise_for_status()  # 응답 오류 확인
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to analyze sentiment: {str(e)}"}), naver_response.status_code if naver_response else 500

    naver_result = naver_response.json()
    sentiment = naver_result.get('document', {}).get('sentiment')
    if not sentiment:
        return jsonify({"error": "Sentiment analysis failed"}), 500

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
        'target_valence': target_valence,
        'limit': 10  # 최대 10곡 추천
    }

    try:
        spotify_response = requests.get(spotify_url, headers=spotify_headers, params=spotify_params)
        spotify_response.raise_for_status()  # 응답 오류 확인
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch music recommendations: {str(e)}"}), spotify_response.status_code if spotify_response else 500

    spotify_result = spotify_response.json()

    # 랜덤으로 하나의 트랙 선택
    tracks = spotify_result.get('tracks', [])
    if not tracks:
        return jsonify({"error": "No music recommendations found"}), 500
    
    random_track = random.choice(tracks)  # 랜덤으로 하나의 트랙 선택

    # 감정 분석 결과와 음악 추천 결과를 함께 반환
    return jsonify({
        "sentiment": naver_result,
        "music_recommendation": random_track  # 랜덤으로 선택한 트랙만 반환
    })

if __name__ == '__main__':
    app.run(debug=True)

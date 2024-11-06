import requests
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

CLOVASTUDIO_API_KEY = "NTA0MjU2MWZlZTcxNDJiY6E6DoJjP+y3t+dreE2flVrWAGgtghU8gD17GHn/QLyW"
APIGW_API_KEY = "kiwKq0Ku69xEunR4KCwH2PWLDuFDeA1U6Uo5IoLh"
API_URL = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"

# Spotify API 설정 (엑세스 토큰 하드코딩)
spotify_url = "https://api.spotify.com/v1/recommendations"
spotify_access_token = "BQAYd8Q6jKeRP0j0eWhizfDdBIZbbfdF6aaA7nDFvPPhs3qsTEcuKbUjw53nSVgC4GXKK0C3P13vpyKK9amRpIHG5jMh3EA0wRweLuF8LSm-LKaop6g"

# TMDb API 설정 (영화 추천)
tmdb_api_key = "21b8fb87add288dc03ffdcc53bf151c2"  # 실제 TMDb API 키로 변경
tmdb_url = "https://api.themoviedb.org/3/discover/movie"

def analyze_sentiment(text):
    headers = {
        "X-NCP-CLOVASTUDIO-API-KEY": CLOVASTUDIO_API_KEY,
        "X-NCP-APIGW-API-KEY": APIGW_API_KEY,
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "이것은 문장 감정 분석기 입니다.\n\n문장: 기분 진짜 좋다\n감정: 긍정\n###\n문장: 아오 진짜 짜증나게 하네\n감정: 부정\n###\n문장: 이걸로 보내드릴게요\n감정: 중립\n###\n문장: 짜증나네\n감정: 부정\n###"
            },
            {
                "role": "user",
                "content": f"문장: {text}"
            }
        ],
        "topP": 0.6,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.1,
        "repeatPenalty": 1.2,
        "includeAiFilters": True,
        "seed": 0
    }

    response = requests.post(API_URL, headers=headers, json=data, stream=True)
    
    if response.status_code == 200:
        sentiment = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if "data:" in decoded_line:
                    try:
                        data_json = decoded_line.split("data:")[1].strip()
                        if '"content"' in data_json:
                            content = data_json.split('"content":"')[1].split('"')[0]
                            if "감정: " in content:
                                sentiment = content.split("감정: ")[-1].strip()
                                break
                    except (IndexError, ValueError):
                        continue

        return {"sentiment": sentiment}
    else:
        print(f"Error: {response.status_code}, Message: {response.text}")
        return {"error": f"API 호출 실패 - 상태 코드: {response.status_code}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    user_text = request.json['text']
    naver_result = analyze_sentiment(user_text)

    if "error" in naver_result:
        return jsonify(naver_result), 500

    sentiment = naver_result.get("sentiment", "중립")

    # 감정 분석 결과에 따라 Spotify API 호출
    spotify_headers = {
        "Authorization": f"Bearer {spotify_access_token}"
    }

    # 감정별로 target_valence(곡의 밝기)를 설정
    if "긍정" in sentiment:
        target_valence = 0.9  # 밝고 긍정적인 곡
    elif "부정" in sentiment:
        target_valence = 0.1  # 슬프고 부정적인 곡
    else:
        target_valence = 0.5  # 중립적인 곡

    # Spotify 추천 API 파라미터
    spotify_params = {
        'seed_genres': 'pop',
        'target_valence': target_valence,
        'limit': 10
    }

    try:
        spotify_response = requests.get(spotify_url, headers=spotify_headers, params=spotify_params)
        spotify_response.raise_for_status()  # 응답 오류 확인
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch music recommendations: {str(e)}"}), 500

    spotify_result = spotify_response.json()

    # 랜덤으로 하나의 트랙 선택
    tracks = spotify_result.get('tracks', [])
    if not tracks:
        return jsonify({"error": "No music recommendations found"}), 500
    
    random_track = random.choice(tracks)  # 랜덤으로 하나의 트랙 선택

    # 감정 분석 결과에 따라 TMDb API 호출 (영화 추천)
    if "긍정" in sentiment:
        genre = "35"  # Comedy
    elif "부정" in sentiment:
        genre = "18"  # Drama
    else:
        genre = "12"  # Adventure (중립적인 분위기)

    tmdb_params = {
        'api_key': tmdb_api_key,
        'with_genres': genre,
        'sort_by': 'popularity.desc',
        'language': 'ko-KR',
        'page': 1
    }

    try:
        tmdb_response = requests.get(tmdb_url, params=tmdb_params)
        tmdb_response.raise_for_status()  # 응답 오류 확인
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch movie recommendations: {str(e)}"}), 500

    tmdb_result = tmdb_response.json()

    # 랜덤으로 하나의 영화 선택
    movies = tmdb_result.get('results', [])
    if not movies:
        return jsonify({"error": "No movie recommendations found"}), 500

    random_movie = random.choice(movies)  # 랜덤으로 하나의 영화 선택

    # 감정 분석 결과와 음악 및 영화 추천 결과를 함께 반환
    return jsonify({
        "sentiment": sentiment,
        "music_recommendation": random_track,  # 랜덤으로 선택한 트랙 반환
        "movie_recommendation": random_movie  # 랜덤으로 선택한 영화 반환
    })

if __name__ == '__main__':
    app.run(debug=True)

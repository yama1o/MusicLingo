import os
import spotipy
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# .envファイルから環境変数を読み込む
load_dotenv()

# APIキーを環境変数から取得
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def test_all_apis():
    # Spotify APIのテスト
    try:
        auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        results = sp.search(q='artist:Ed Sheeran', type='artist')
        print("✅ Spotify API: 接続成功！")
        # print(results['artists']['items'][0]['name']) # Ed Sheeranと表示されればOK
    except Exception as e:
        print(f"❌ Spotify API: 接続失敗... {e}")

    # Genius APIのテスト
    try:
        headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
        response = requests.get('https://api.genius.com/songs/3039923', headers=headers) # Ed Sheeran - Shape of You
        if response.status_code == 200:
            print("✅ Genius API: 接続成功！")
        else:
            print(f"❌ Genius API: 接続失敗... Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Genius API: 接続失敗... {e}")

    # Gemini APIのテスト
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Pythonについて1文で教えて。")
        print("✅ Gemini API: 接続成功！")
        # print(response.text) # Geminiからの返信が表示されればOK
    except Exception as e:
        print(f"❌ Gemini API: 接続失敗... {e}")

# このファイルが直接実行された場合にのみテストを実行
if __name__ == '__main__':
    print("--- API接続テストを開始します ---")
    test_all_apis()
    print("--- テストを終了します ---")
import os
import re
import json
import spotipy
import datetime
import lyricsgenius
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

'''
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
'''

# Spotify API クライアント初期化
try:
    auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    sp = None
    print(f"Spotifyの初期化に失敗しました: {e}")

# --- Genius API クライアント初期化 (新規追加) ---
try:
    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN,
                                 remove_section_headers=False, # [Chorus]などのヘッダーを削除
                                 skip_non_songs=True,         # "Song"ではないページをスキップ
                                 excluded_terms=["(Remix)", "(Live)"], # 特定の単語を含む曲を除外
                                 timeout=15,
                                 retries=3)
except Exception as e:
    genius = None
    print(f"Geniusの初期化に失敗しました: {e}")
except Exception as e:
    genius = None
    print(f"Geniusの初期化に失敗しました: {e}")

#  Gemini API 設定-
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Geminiの初期化に失敗しました: {e}")

def search_tracks_by_artist(artist_name):
    if not sp:
        return []
        
    try:
        # アーティスト名で楽曲を検索
        results = sp.search(q=f'artist:{artist_name}', type='track', limit=10)
        
        tracks = []
        for item in results['tracks']['items']:
            track_info = {
                'id': item['id'],
                'title': item['name'],
                'artist': item['artists'][0]['name']
            }
            tracks.append(track_info)
        return tracks
    except Exception as e:
        print(f"Spotifyでの楽曲検索中にエラーが発生しました: {e}")
        return []
    
def get_lyrics(song_title, artist_name):
    if not genius:
        return "Geniusが初期化されていません。"
        
    try:
        song = genius.search_song(song_title, artist_name)
        if song:
            lyrics = song.lyrics
            
            # 最初のセクションヘッダーを見つける
            first_header_match = re.search(r'\[.*?\]', lyrics)
            
            if first_header_match:
                # ヘッダーの開始位置から後ろをすべて取得
                start_index = first_header_match.start()
                lyrics_body = lyrics[start_index:]
                
                # すべてのセクションヘッダー（例: [Verse]や[Chorus]）を削除して、歌詞だけを返す
                cleaned_lyrics = re.sub(r'\[.*?\]\n?', '', lyrics_body).strip()
                return cleaned_lyrics
            else:
                # もしヘッダーが見つからない場合は、そのまま返す
                return lyrics.strip()
        else:
            return "歌詞が見つかりませんでした。"
    except Exception as e:
        print(f"Geniusでの歌詞取得中にエラーが発生しました: {e}")
        return "エラーにより歌詞を取得できませんでした。"
    
def get_phrases_from_lyrics(lyrics, song_title, artist_name):
    # Geminiモデルの準備
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        return f"Geminiモデルの初期化に失敗: {e}"

    # プロンプトを作成(JSON形式で出力)
    prompt = f"""
あなたは優秀な英語学習の先生です。
以下の歌詞は、{artist_name}の「{song_title}」という曲のものです。

--- 歌詞 ---
{lyrics}
--- 歌詞終わり ---

この歌詞の中から、日常会話やビジネスで応用できる実用的な英語フレーズを3〜5個抽出してください。
そして、それぞれのフレーズについて、以下の情報をJSON形式のリストで返してください。

- "phrase": 抽出したフレーズ
- "difficulty": 難易度（"beginner", "intermediate", "advanced"のいずれか）
- "context": フレーズが使われる簡単な場面説明（例: "romantic expression", "making a suggestion"など）
- "conversation_example": そのフレーズを使った短い会話例（AとBの対話形式）

必ず、JSONのリスト形式（例: [{{...}}, {{...}}]）のみを出力してください。他の余計なテキストは含めないでください。
"""

    try:
        # AIにリクエストを送信
        response = model.generate_content(prompt)
        
        # AIの応答からJSON部分を抽出してパースする(```json ... ``` のようなマークダウンが含まれることがあるため、それを取り除く)
        json_text = re.sub(r'```json\n?|```', '', response.text).strip()
        
        phrases_data = json.loads(json_text)
        return phrases_data
    except Exception as e:
        print(f"Geminiでのフレーズ抽出中にエラーが発生しました: {e}")
        print(f"--- AIからの応答 ---\n{response.text if 'response' in locals() else 'N/A'}")
        return []
    
def save_learning_data(song_info, phrases):
    file_path = "learning_data.json"
    today_str = datetime.date.today().isoformat()

    # 既存のデータを読み込む
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルがない、または空の場合は新しい構造を作成
        data = {
            "songs": [],
            "phrases": [],
            "stats": {
                "total_phrases": 0,
                "songs_studied": 0,
                "last_study_date": None
            }
        }

    # 楽曲情報の追加
    new_song_record = {
        "id": song_info['id'],
        "title": song_info['title'],
        "artist": song_info['artist'],
        "studied_at": today_str
    }
    data["songs"].append(new_song_record)

    # フレーズ情報の追加
    for phrase in phrases:
        new_phrase_record = {
            "song_id": song_info['id'],
            "phrase": phrase.get("phrase"),
            "difficulty": phrase.get("difficulty"),
            "context": phrase.get("context"),
            "conversation": phrase.get("conversation_example"),
            "learned_at": datetime.datetime.now().isoformat()
        }
        data["phrases"].append(new_phrase_record)

    # 統計情報の更新
    data["stats"]["total_phrases"] = len(data["phrases"])
    data["stats"]["songs_studied"] = len(data["songs"])
    data["stats"]["last_study_date"] = today_str
    
    # ファイルに書き込む
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ 学習データを{file_path}に保存しました。")
    except Exception as e:
        print(f"JSONファイルへの保存中にエラーが発生しました: {e}")

if __name__ == '__main__':
    # Spotifyで楽曲検索
    artist_name = "Taylor Swift"
    print(f"--- 1. Spotifyで{artist_name}の曲を検索します ---")
    tracks = search_tracks_by_artist(artist_name)

    if tracks:
        # 最初の曲を選択
        target_song = tracks[0]
        print(f"\n--- 2. '{target_song['title']}'の歌詞をGeniusで検索します ---")
        
        # 歌詞を取得
        lyrics = get_lyrics(target_song['title'], target_song['artist'])
        
        if lyrics and "歌詞が見つかりませんでした" not in lyrics:
            print("✅ 歌詞の取得に成功しました。")
            
            # AIでフレーズを抽出
            print("\n--- 3. Gemini AIで実用的なフレーズを抽出します ---")
            phrases = get_phrases_from_lyrics(lyrics, target_song['title'], target_song['artist'])
            
            if phrases:
                print("✅ フレーズの抽出に成功しました。")
                for p in phrases:
                    print(f"  - {p.get('phrase')} ({p.get('difficulty')})")
                
                # 結果をJSONファイルに保存
                print("\n--- 4. 学習データをファイルに保存します ---")
                save_learning_data(target_song, phrases)
            else:
                print("フレーズの抽出に失敗しました。")
        else:
            print("歌詞が取得できなかったため、処理を中断します。")
    else:
        print("楽曲が見つかりませんでした。")
# 🎵 MusicLingo

MusicLingoは、Spotifyで好きな洋楽を検索し、その歌詞からAIが抽出した実用的な英語フレーズを文脈と共に学べるデスクトップアプリケーションです。

## 概要

このアプリは、音楽という身近な趣味を通して、より実践的で記憶に残りやすい英語学習体験を提供することを目的とし、ユーザーの好きな曲をパーソナライズされた学習教材へと変換します。

### 主な機能

* **楽曲検索**: Spotify APIを利用してアーティスト名から楽曲を検索します。
* **歌詞取得**: Genius APIを利用して選択した楽曲の歌詞を自動で取得します。
* **AIフレーズ抽出**: Gemini APIが歌詞を解析し、実用的な英語フレーズを3〜5個抽出します。
* **学習コンテンツ生成**: 抽出されたフレーズごとに、難易度、利用場面、そして具体的な会話例をAIが自動生成します。
* **学習記録**: 学習した楽曲やフレーズは`learning_data.json`に自動で記録・蓄積されます。

## 技術スタック

* **言語**: Python 3.8+
* **主要ライブラリ**:
    * `spotipy`: Spotify Web API連携
    * `lyricsgenius`: Genius API連携・歌詞取得
    * `google-generativeai`: Gemini API連携
    * `tkinter`: GUIフレームワーク
    * `requests`, `python-dotenv`
* **データ保存**: JSON

## セットアップとインストール

このアプリケーションをローカル環境で実行するための手順です。

### 1. 前提条件

* Python 3.8以上がインストールされていること。
* Gitがインストールされていること。

### 2. リポジトリのクローン

```bash
git clone [https://github.com/your-username/MusicLingo.git](https://github.com/your-username/MusicLingo.git)
cd MusicLingo
```
*(注意: `your-username`の部分はご自身のGitHubユーザー名に置き換えてください)*

### 3. 仮想環境の構築と有効化

```bash
# 仮想環境を作成
python -m venv venv

# Windowsの場合
venv\Scripts\activate

# Mac/Linuxの場合
source venv/bin/activate
```

### 4. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 5. APIキーの設定

プロジェクトを動作させるには、3つのサービスのAPIキーが必要です。

1.  まず、プロジェクトのルートにある`.env.example`ファイルをコピーし、ファイル名を`.env`に変更します。

    **Windows (コマンドプロンプト):**
    ```bash
    copy .env.example .env
    ```

    **Mac/Linux (ターミナル):**
    ```bash
    cp .env.example .env
    ```

2.  次に、必要なAPIキーを各サービスから取得します。
    * **Spotify**: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) でアプリを作成し、`Client ID`と`Client Secret`を取得。
    * **Genius**: [Genius API Clients](https://genius.com/api-clients) でクライアントを作成し、`Access Token`を取得。
    * **Google (Gemini)**: [Google AI Studio](https://aistudio.google.com/) で`API Key`を取得。

3.  作成した`.env`ファイルを開き、取得したキーの値をそれぞれの`""`の間に貼り付けて保存します。
```

## 使用方法

以下のコマンドでアプリケーションを起動します。

```bash
python main.py
```

1.  ウィンドウが表示されたら、好きなアーティスト名を入力して「検索」ボタンを押します。
2.  検索結果のリストから学習したい曲を選択します。
3.  「選択した楽曲で学習開始」ボタンを押します。
4.  学習画面が表示されたら、「次のフレーズ」ボタンで学習を進めます。
5.  学習が終わったら「学習完了」ボタンを押すと、内容が`learning_data.json`に保存され、検索画面に戻ります。

## プロジェクトファイル構成

```
MusicLingo/
│
├── .env                # APIキー（Git管理外）
├── .gitignore          # Gitの無視リスト
├── api_client.py       # 外部APIとの通信を担当するモジュール
├── learning_data.json  # 学習データが保存されるファイル
├── main.py             # メインアプリケーション（GUIとエントリーポイント）
├── README.md           # このファイル
└── requirements.txt    # 依存ライブラリリスト
```
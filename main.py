import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import api_client

class MusicLingoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        #ウィンドウとスタイルの設定
        self.title("🎵 MusicLingo")
        self.geometry("450x400")
        style = ttk.Style(self)
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))

        # 変数の初期化
        self.tracks_data = []
        self.learning_phrases = []
        self.current_phrase_index = 0
        self.current_song_info = None

        # フレームの作成
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # 検索画面、学習画面を作成
        for F in (SearchScreen, LearningScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # 初期画面を検索画面に設定
        self.show_frame("SearchScreen")

    def show_frame(self, page_name):
        """指定された名前のフレームを表示する"""
        frame = self.frames[page_name]
        frame.tkraise()


class SearchScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller

        # ウィジェットの作成
        search_label = ttk.Label(self, text="アーティスト名:")
        self.artist_entry = ttk.Entry(self, width=30)
        search_button = ttk.Button(self, text="🔍 検索", command=self.search_artist)
        result_label = ttk.Label(self, text="検索結果:")
        self.result_listbox = tk.Listbox(self, height=10)
        start_button = ttk.Button(self, text="選択した楽曲で学習開始", command=self.start_learning_flow)

        # 配置
        search_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.artist_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        search_button.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        result_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10,0))
        self.result_listbox.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.grid_rowconfigure(2, weight=1) # リストボックスが伸縮するように
        start_button.grid(row=3, column=0, columnspan=3, pady=10)

    def search_artist(self):
        artist_name = self.artist_entry.get()
        if not artist_name:
            messagebox.showwarning("入力エラー", "アーティスト名を入力してください。")
            return
        
        self.result_listbox.delete(0, tk.END)
        # controller経由でAppの変数を更新
        self.controller.tracks_data = api_client.search_tracks_by_artist(artist_name)
        
        if self.controller.tracks_data:
            for track in self.controller.tracks_data:
                self.result_listbox.insert(tk.END, f"{track['title']} - {track['artist']}")
        else:
            messagebox.showinfo("検索結果", "該当する楽曲が見つかりませんでした。")

    def start_learning_flow(self):
        selected_indices = self.result_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("選択エラー", "学習する楽曲をリストから選択してください。")
            return
        
        selected_index = selected_indices[0]
        self.controller.current_song_info = self.controller.tracks_data[selected_index]
        
        # バックエンド処理
        messagebox.showinfo("情報取得中", "歌詞とフレーズ情報を取得しています...")
        lyrics = api_client.get_lyrics(self.controller.current_song_info['title'], self.controller.current_song_info['artist'])
        if not lyrics or "歌詞が見つかりませんでした" in lyrics:
            messagebox.showerror("エラー", "歌詞が取得できませんでした。")
            return
            
        phrases = api_client.get_phrases_from_lyrics(lyrics, self.controller.current_song_info['title'], self.controller.current_song_info['artist'])
        if not phrases:
            messagebox.showerror("エラー", "AIからフレーズが取得できませんでした。")
            return
        
        self.controller.learning_phrases = phrases
        self.controller.current_phrase_index = 0
        
        # 学習画面にデータを渡して表示を更新
        learning_frame = self.controller.frames["LearningScreen"]
        learning_frame.update_display()
        self.controller.show_frame("LearningScreen")


class LearningScreen(ttk.Frame):
    """フレーズ学習画面"""
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller

        self.song_title_var = tk.StringVar()
        self.phrase_var = tk.StringVar()
        self.difficulty_var = tk.StringVar()
        self.context_var = tk.StringVar()

        # ウィジェットの作成
        song_title_label = ttk.Label(self, textvariable=self.song_title_var, style="Header.TLabel")
        
        phrase_header_label = ttk.Label(self, text="📝 学習フレーズ:")
        phrase_label = ttk.Label(self, textvariable=self.phrase_var, wraplength=400, font=("Helvetica", 11))
        difficulty_label = ttk.Label(self, textvariable=self.difficulty_var, foreground="gray")
        context_label = ttk.Label(self, textvariable=self.context_var, foreground="gray", wraplength=400)

        
        conv_header_label = ttk.Label(self, text="💬 会話例:")
        self.conv_text = tk.Text(self, height=5, wrap=tk.WORD, font=("Helvetica", 10))
        self.conv_text.config(state=tk.DISABLED)

        # ボタン
        button_frame = ttk.Frame(self)
        next_button = ttk.Button(button_frame, text="次のフレーズ", command=self.next_phrase)
        finish_button = ttk.Button(button_frame, text="学習完了", command=self.finish_learning)
        back_button = ttk.Button(button_frame, text="戻る", command=lambda: controller.show_frame("SearchScreen"))

        # 配置
        song_title_label.pack(pady=(0, 10))
        phrase_header_label.pack(anchor="w", pady=(10, 0))
        phrase_label.pack(anchor="w", padx=10, pady=5)
        difficulty_label.pack(anchor="w", padx=10)
        context_label.pack(anchor="w", padx=10)

        conv_header_label.pack(anchor="w", pady=(20, 0))
        self.conv_text.pack(fill="x", expand=True, padx=5, pady=5)
        
        button_frame.pack(pady=10)
        back_button.pack(side="left", padx=5)
        finish_button.pack(side="left", padx=5)
        next_button.pack(side="left", padx=5)

    def update_display(self):
        phrase_data = self.controller.learning_phrases[self.controller.current_phrase_index]
        song_info = self.controller.current_song_info

        self.song_title_var.set(f"📚 \"{song_info['title']}\" - {song_info['artist']}")
        self.phrase_var.set(phrase_data.get("phrase", "---"))

        self.difficulty_var.set(f"難易度: {phrase_data.get('difficulty', '-')}")
        self.context_var.set(f"場面: {phrase_data.get('context', '-')}")
        
        self.conv_text.config(state=tk.NORMAL)
        self.conv_text.delete("1.0", tk.END)

        conversation_data = phrase_data.get("conversation_example", "---")
        if isinstance(conversation_data, dict):
            # もしデータが辞書形式なら、AとBに分けて整形して表示
            formatted_conversation = f"A: {conversation_data.get('A', '')}\nB: {conversation_data.get('B', '')}"
            self.conv_text.insert(tk.END, formatted_conversation)
        else:
            # 文字列ならそのまま表示
            self.conv_text.insert(tk.END, str(conversation_data))

        self.conv_text.config(state=tk.DISABLED)

    def next_phrase(self):
        if self.controller.current_phrase_index < len(self.controller.learning_phrases) - 1:
            self.controller.current_phrase_index += 1
            self.update_display()
        else:
            messagebox.showinfo("完了", "最後のフレーズです。お疲れ様でした！")

    def finish_learning(self):
        api_client.save_learning_data(self.controller.current_song_info, self.controller.learning_phrases)
        messagebox.showinfo("保存完了", "学習内容を保存しました。")
        self.controller.show_frame("SearchScreen")

if __name__ == "__main__":
    app = MusicLingoApp()
    app.mainloop()
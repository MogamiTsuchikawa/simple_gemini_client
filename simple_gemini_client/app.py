import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import json
import os
from pathlib import Path
import threading

class GeminiChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chat")
        self.root.geometry("800x600")
        
        # APIキーの設定
        self.api_key = self.load_api_key()
        
        # チャット履歴
        self.chat_history = []
        
        # システムプロンプト
        self.system_prompt_path = None
        self.system_prompt = ""
        
        # モデル選択オプション
        self.models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-pro"
        ]
        
        self.selected_model = tk.StringVar(value=self.models[2])  # デフォルトはgemini-2.0-flash
        
        self.create_widgets()
        
        # デフォルトのシステムプロンプトを読み込む
        if os.path.exists("system_prompt.txt"):
            self.system_prompt_path = "system_prompt.txt"
            self.load_system_prompt()
    
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部フレーム（設定用）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # APIキー入力
        ttk.Label(top_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.api_key_entry = ttk.Entry(top_frame, width=30, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        
        ttk.Button(top_frame, text="保存", command=self.save_api_key).grid(row=0, column=2, padx=(0, 10))
        
        # モデル選択
        ttk.Label(top_frame, text="モデル:").grid(row=0, column=3, sticky=tk.W, padx=(10, 5))
        model_combo = ttk.Combobox(top_frame, textvariable=self.selected_model, values=self.models, state="readonly", width=15)
        model_combo.grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        
        # システムプロンプト選択
        ttk.Button(top_frame, text="システムプロンプト選択", command=self.select_system_prompt).grid(row=0, column=5, padx=(10, 0))
        
        # チャットエリア
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # チャット表示エリア
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=20, state="disabled")
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 入力エリア
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.user_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=3)
        self.user_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.user_input.bind("<Return>", self.on_enter_pressed)
        self.user_input.bind("<Shift-Return>", lambda e: None)  # Shift+Enterは改行
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="送信", command=self.send_message).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="リセット", command=self.reset_chat).pack(fill=tk.X)
    
    def on_enter_pressed(self, event):
        # Enterキーが押されたら送信（Shift+Enterは改行）
        self.send_message()
        return "break"  # イベントの伝播を停止
    
    def load_api_key(self):
        # APIキーをファイルから読み込む
        config_path = Path.home() / ".gemini_chat_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("api_key", "")
            except Exception as e:
                print(f"設定ファイルの読み込みエラー: {e}")
        return ""
    
    def save_api_key(self):
        # APIキーをファイルに保存
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("エラー", "APIキーを入力してください")
            return
        
        self.api_key = api_key
        config_path = Path.home() / ".gemini_chat_config.json"
        try:
            with open(config_path, "w") as f:
                json.dump({"api_key": api_key}, f)
            messagebox.showinfo("成功", "APIキーを保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"APIキーの保存に失敗しました: {e}")
    
    def select_system_prompt(self):
        # システムプロンプトファイルを選択
        file_path = filedialog.askopenfilename(
            title="システムプロンプトファイルを選択",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if file_path:
            self.system_prompt_path = file_path
            self.load_system_prompt()
    
    def load_system_prompt(self):
        # システムプロンプトをファイルから読み込む
        if not self.system_prompt_path:
            return
        
        try:
            with open(self.system_prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
            messagebox.showinfo("成功", f"システムプロンプトを読み込みました: {os.path.basename(self.system_prompt_path)}")
        except Exception as e:
            messagebox.showerror("エラー", f"システムプロンプトの読み込みに失敗しました: {e}")
    
    def update_chat_display(self):
        # チャット表示を更新
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        
        for message in self.chat_history:
            role = message["role"]
            text = message["text"]
            
            if role == "user":
                self.chat_display.insert(tk.END, "あなた: ", "user")
                self.chat_display.insert(tk.END, f"{text}\n\n")
            else:
                self.chat_display.insert(tk.END, "Gemini: ", "model")
                self.chat_display.insert(tk.END, f"{text}\n\n")
        
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)
        
        # タグの設定
        self.chat_display.tag_configure("user", foreground="blue")
        self.chat_display.tag_configure("model", foreground="green")
    
    def send_message(self):
        # ユーザーメッセージを送信
        user_message = self.user_input.get(1.0, tk.END).strip()
        if not user_message:
            return
        
        # APIキーの確認
        if not self.api_key:
            messagebox.showerror("エラー", "APIキーを設定してください")
            return
        
        # ユーザーメッセージをチャット履歴に追加
        self.chat_history.append({"role": "user", "text": user_message})
        self.update_chat_display()
        
        # 入力欄をクリア
        self.user_input.delete(1.0, tk.END)
        
        # 別スレッドでAPIリクエストを実行
        threading.Thread(target=self.request_gemini_response, args=(user_message,)).start()
    
    def request_gemini_response(self, user_message):
        # Gemini APIにリクエストを送信
        try:
            model = self.selected_model.get()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            # リクエストデータの作成
            request_data = {
                "contents": [
                ],
                "generationConfig": {
                    "temperature": 1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                    "responseMimeType": "text/plain"
                }
            }
            
            # チャット履歴を追加（最初のユーザーメッセージを除く）
            for message in self.chat_history[:-1]:
                request_data["contents"].append({
                    "role": message["role"],
                    "parts": [{"text": message["text"]}]
                })
            request_data["contents"].append({
                "role": "user",
                "parts": [{"text": user_message}]
            })
            
            # システムプロンプトがあれば追加
            if self.system_prompt:
                request_data["systemInstruction"] = {
                    "role": "user",
                    "parts": [{"text": self.system_prompt}]
                }
            print("r===============")
            print(request_data)
            print("================")
            # APIリクエスト
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=request_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(response_data)
                if "candidates" in response_data and len(response_data["candidates"]) > 0:
                    candidate = response_data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if parts and "text" in parts[0]:
                            assistant_message = parts[0]["text"]
                            
                            # アシスタントの応答をチャット履歴に追加
                            self.chat_history.append({"role": "model", "text": assistant_message})
                            
                            # UIスレッドで表示を更新
                            self.root.after(0, self.update_chat_display)
                            return
            
            # エラーメッセージ
            error_message = f"エラー: {response.status_code} - {response.text}"
            self.chat_history.append({"role": "model", "text": error_message})
            self.root.after(0, self.update_chat_display)
            
        except Exception as e:
            error_message = f"エラー: {str(e)}"
            self.chat_history.append({"role": "model", "text": error_message})
            self.root.after(0, self.update_chat_display)
    
    def reset_chat(self):
        # チャットをリセット
        self.chat_history = []
        self.update_chat_display()
        
        # システムプロンプトを再読み込み
        if self.system_prompt_path:
            self.load_system_prompt()

def main():
    root = tk.Tk()
    app = GeminiChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
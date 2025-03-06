# Simple Gemini Client

Google Gemini APIを使用したシンプルなチャットアプリケーションです。

## 機能

- Google Gemini APIを使用したチャット機能
- システムプロンプトのカスタマイズ
- 複数のGeminiモデル（gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash, gemini-2.0-pro）をサポート
- APIキーの保存機能

## 必要条件

- Python 3.12以上
- 必要なパッケージ: requests

## インストール方法

1. リポジトリをクローンまたはダウンロードします。

```bash
git clone https://github.com/yourusername/simple_gemini_client.git
cd simple_gemini_client
```

2. 仮想環境を作成し、依存関係をインストールします。

```bash
# uvを使用する場合
uv venv
source .venv/bin/activate
uv pip install -e .

# pipを使用する場合
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 使用方法

1. アプリケーションを起動します。

```bash
python run.py
```

2. 初回起動時にGoogle Gemini APIキーを入力します。
   - APIキーは [Google AI Studio](https://aistudio.google.com/) から取得できます。

3. チャットインターフェースでGeminiと会話を開始します。

## カスタマイズ

### システムプロンプト

デフォルトのシステムプロンプトは `system_prompt.txt` ファイルに保存されています。このファイルを編集するか、アプリケーション内の「システムプロンプト選択」ボタンから別のファイルを選択できます。

## ライセンス

MIT License

#!/usr/bin/env python3
"""
Simple Gemini Client - アプリケーション起動スクリプト
"""

import os
import sys
from pathlib import Path

# リソースパスの設定
if getattr(sys, 'frozen', False):
    # アプリケーションがバンドルされている場合
    bundle_dir = Path(sys._MEIPASS)
    os.chdir(bundle_dir)
else:
    # 開発環境の場合
    bundle_dir = Path(__file__).parent

# アプリケーションの起動
from simple_gemini_client.app import main

if __name__ == "__main__":
    main() 
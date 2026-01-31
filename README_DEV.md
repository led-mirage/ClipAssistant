# <img src="src/view/app.ico" width="36"> ClipAssistant AI 開発者向け環境構築ガイド

© 2026 led-mirage

## 💎 はじめに

このドキュメントでは、開発者向けの環境構築とビルド方法について説明します。

## 💎 開発環境

- Windows 11
- Python 3.10+
- Git

# ソースを取得
git clone https://github.com/led-mirage/ClipAssistant

# プロジェクトディレクトリに移動
cd ClipAssistant

# Python仮想環境を作る
python -m venv venv

# Python仮想環境をアクティベート
venv\scripts\activate

# 必要なライブラリのインストール
pip install -r requirements.txt
```

<div style="page-break-before:always"></div>

## 💎 ビルド

以下のコマンドを実行することで `ClipAssistant/dist` フォルダにEXEファイルが生成されます。

```powershell
# プロジェクトディレクトリに移動
cd ClipAssistant

# Python仮想環境をアクティベート
venv\scripts\activate

# ビルド用ライブラリのインストール（初回のみ）
pip install pyinstaller pyinstaller-versionfile

# ビルド実行
tools\build.bat
```

## 💎 Pythonでの実行方法

```powershell
# プロジェクトフォルダに移動
cd ClipAssistant

# Python仮想環境をアクティベート
venv\scripts\activate

# 実行
python src/main.py
```

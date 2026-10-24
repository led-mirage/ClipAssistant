# <img src="src/view/app.ico" width="36"> ClipAssistant AI 開発者向け環境構築ガイド

© 2026 led-mirage

## 💎 はじめに

このドキュメントでは、開発者向けの環境構築・ビルド方法・実APIの接続テストについて説明します。

## 💎 開発環境

- Windows 11
- Python 3.11以上（Pillow 13.0.0の要件。今回の動作確認環境はPython 3.13.12）
- Git

## 💎 ソースを取得

```powershell
git clone https://github.com/led-mirage/ClipAssistant

# プロジェクトディレクトリに移動
cd ClipAssistant

# Python仮想環境を作る
python -m venv venv

# Python仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# 必要なライブラリのインストール
python -m pip install -r requirements.txt
```

<div style="page-break-before:always"></div>

## 💎 ビルド

以下のコマンドを実行することで `ClipAssistant/dist` フォルダにEXEファイルが生成されます。

```powershell
# プロジェクトディレクトリに移動
cd ClipAssistant

# Python仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# ビルド用ライブラリのインストール（初回のみ）
python -m pip install pyinstaller pyinstaller-versionfile

# ビルド実行
.\tools\build.bat

# スプラッシュ画面なしのバージョンをビルドする場合
.\tools\build_nosplash.bat
```

## 💎 Pythonでの実行方法

```powershell
# プロジェクトフォルダに移動
cd ClipAssistant

# Python仮想環境をアクティベート
.\venv\Scripts\Activate.ps1

# 実行
python src/main.py
```

## 💎 実APIの接続テスト

モデルやAIライブラリを更新した際は、既存の `Agent.generate_text()` を実APIに接続して検証できます。
Python標準の `unittest` を使うため、アプリの依存関係以外のテスト用ライブラリは不要です。

`tests/models.yaml` の対象モデルと、APIキーなどの環境変数を設定してから実行してください。
Azure OpenAIはデプロイ名と、キー・エンドポイントの環境変数名をセットで指定します。

```powershell
# 全サービスのモデル一覧を一括実行（API利用料金が発生します）
.\tests\run_tests.bat all

# サービスを絞って一括実行
.\tests\run_tests.bat openai

# モデル単体を実行
.\venv\Scripts\python.exe tests/test_agent_live.py --run-live-api --api OpenAI --model gpt-5.1
```

バッチの引数は `all`、`openai`、`claude`、`gemini`、`azureopenai` のいずれか1つです。
結果は画面と `tests/results` のログに出力し、モデル別結果とサービス別集計、実行日時、SDKバージョンを記録します。
いずれかのテストが失敗した場合は、終了コードが非ゼロになります。

APIに接続しない通常のテスト探索も実行できます。この場合は全件スキップされ、接続確認にはなりません。

```powershell
python -m unittest discover -s tests -v
```

詳しい設定・引数・ログの説明は [実APIの接続テスト](tests/README.md) を参照してください。

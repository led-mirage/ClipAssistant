# 実APIの接続テスト

Python標準の `unittest` で、既存の `Agent.generate_text()` を実行します。
クライアント生成、リクエスト送信、応答本文の取得までを確認し、空でない文字列が返れば成功です。
回答の文言や品質、GUIの動作は検証しません。

追加ライブラリは不要です。アプリ用の `requirements.txt` をインストールしたPython環境を使用してください。
以下はプロジェクトのルートで、仮想環境を有効にして実行するPowerShellの例です。

テスト結果の冒頭に、実行環境にインストールされている `openai`・`anthropic`・`google-genai` の
バージョンを表示します。`requirements.txt` の指定値ではなく、実際のインストール済みバージョンです。
未インストールの場合は `not installed` と表示します。

`python tests/test_agent_live.py ...` で実行すると、画面への表示と同時に
`tests/results/agent_live_YYYYMMDD_HHMMSS_ffffff.log` へUTF-8で結果を保存します。
実行開始・終了日時（日本時間、`+09:00`）、SDKバージョン、モデルごとの成否、
エラーのトレースバック、最終集計が含まれます。ログはGitの管理対象外です。
Ctrl+Cで中断した場合も、それまでのログと中断・終了日時を保存します。
`--help` や引数・一覧の設定エラーでは結果ファイルを作りません。
`python -m unittest discover ...` では日時とバージョンを画面に表示し、ファイル保存は行いません。

## バッチファイルでの一括実行

プロジェクトのルートで、サービス名を1つ指定します。モデル一覧は `tests/models.yaml` を使います。

```powershell
.\tests\run_tests.bat all
.\tests\run_tests.bat openai
.\tests\run_tests.bat claude
.\tests\run_tests.bat gemini
.\tests\run_tests.bat azureopenai
```

`all` は全サービスを対象にします。引数は大文字・小文字を区別しません。
毎回実APIを呼び出すため、API利用料金が発生します。
プロジェクト内の `venv`、`.venv`、PATH上の `python` の順にPythonを選びます。
別の作業ディレクトリからバッチのパスを指定して実行することもできます。
結果は画面と `tests/results` のログに出力します。
テストの終了コードをそのまま返します。引数不足・不正な引数・複数指定は終了コード2です。

## モデル一覧の一括テスト

サービスごとのモデル一覧は `tests/models.yaml` で編集します。
YAMLのコメントでメモを残したり、モデルを一時的にテスト対象から外したりできます。

```yaml
Gemini:
  - gemini-2.5-flash
  - gemini-3.8-flash
  # - 別のモデルID
```

Azure OpenAIの一覧には設定例を記載しています。利用している環境のデプロイ名と環境変数名に合わせて編集してください。
Azureではデプロイ名・APIキーの環境変数名・エンドポイントの環境変数名をセットで指定できます。
キーやURLそのものはYAMLに記載せず、既存の環境変数から取得します。

```yaml
AzureOpenAI:
  - model: your-deployment-name
    api_key_envvar: AZURE_OPENAI_EUS_API_KEY
    endpoint_envvar: AZURE_OPENAI_EUS_ENDPOINT
```

複数のセットを並べれば、異なるAzureリソースのデプロイも一括テストできます。
ログにはデプロイ名と環境変数名を表示します。
同じデプロイ名でも環境変数名が異なれば別のテストとして扱います。
従来のデプロイ名だけの文字列形式も利用でき、その場合は標準の環境変数名を使います。

モデル名は動作を保証する一覧ではなく、テストしたい対象として管理します。

```powershell
# Geminiのモデル一覧を実行
python tests/test_agent_live.py --run-live-api --api Gemini --all-models

# 複数サービスのモデル一覧を実行
python tests/test_agent_live.py --run-live-api --api OpenAI --api Claude --api Gemini --all-models

# 全サービスの一覧を実行（AzureOpenAIの一覧にも設定が必要）
python tests/test_agent_live.py --run-live-api --all-models
```

`--all-models` ではモデル名の環境変数を使わず、一覧ファイルのモデルを順番に実行します。
選択したサービスの一覧が未定義・空・不正な場合は、接続前に設定エラーで終了します。
同じサービス内の重複モデルは1回だけ実行します。

モデルごとに結果を表示し、途中で失敗しても残りのモデルを実行します。表示例：

```text
Gemini / gemini-2.5-flash ... ok
Gemini / gemini-3.8-flash ... ERROR
Gemini summary: total=2, succeeded=1, failed=1 (failures=0, errors=1), skipped=0
```

各サービスの実行直後に、実行件数・成功件数・失敗件数とその内訳・スキップ件数を表示します。
`failures` は検証条件の不成立、`errors` はAPIエラーなどの例外で、`failed` はその合計です。
集計後に空行を挟んで次のサービスを実行します。この集計も結果ログに保存されます。

最後に件数と全体の成否を表示します。1件でも失敗・エラーがあれば終了コードは非ゼロです。
選択していないサービスはテストに含めず、結果にも表示しません。各モデルの実行にAPI利用料金が発生します。

## モデル単体のテスト

`--model` でモデルIDを直接指定できます。Azure以外では、モデル一覧にないIDも実行できます。
`--api` は1サービスだけ指定し、`--all-models` とは同時に使わないでください。

```powershell
python tests/test_agent_live.py --run-live-api --api Gemini --model gemini-2.5-flash
python tests/test_agent_live.py --run-live-api --api Claude --model claude-haiku-5-5
```

Azureの単体実行では、`--model` に一致するデプロイをYAMLから選び、セットの環境変数名を使います。
一覧に一致するデプロイがなければ設定エラーです。同名が複数あれば一致するすべてのセットを実行します。

```powershell
python tests/test_agent_live.py --run-live-api --api AzureOpenAI --model your-deployment-name
```

`--model` と `--all-models` のどちらも指定しない場合は、従来どおりモデル名の環境変数を使います。

## APIに接続しない通常実行

```powershell
python -m unittest discover -s tests -v
```

4件すべてスキップされ、APIには接続しません。
実APIへの接続は、次のコマンドで `--run-live-api` を指定した場合だけ有効になります。

## 環境変数

テストするサービスのAPIキーを環境変数に設定します。
モデル名の環境変数は、`--model` と `--all-models` のどちらも指定しない場合だけ必要です。
APIキーの変数名はアプリの標準設定と同じです。Azureの一覧では上記のセット形式で変更できます。
テストは `config.yaml` を読み書きしません。

| `--api` の値 | 必要な環境変数 | モデル名の環境変数 |
|---|---|---|
| `OpenAI` | `OPENAI_API_KEY` | `OPENAI_MODEL` |
| `AzureOpenAI` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | `AZURE_OPENAI_MODEL` |
| `Claude` | `ANTHROPIC_API_KEY` | `CLAUDE_MODEL` |
| `Gemini` | `GEMINI_API_KEY` | `GEMINI_MODEL` |

Azure OpenAIの `AZURE_OPENAI_MODEL` にはモデル名ではなくデプロイ名を指定します。
`--model`・`--all-models` を指定しない従来の環境変数による実行では、Azureも上記の標準名を使います。
ほかのサービスのAPIキーの環境変数名は上記の標準名を使います。

## 実APIに接続する

実行するとAPI利用料金が発生します。各モデルに短い生成リクエストを1回送信します。

```powershell
# APIキーは登録済みの環境変数を使用。未登録なら先に設定してください。
$env:OPENAI_MODEL = "gpt-5.1"  # 確認したいモデル名に変更
python tests/test_agent_live.py --run-live-api --api OpenAI

# 複数サービスを選択する場合（各サービスの環境変数設定が必要）
python tests/test_agent_live.py --run-live-api --api OpenAI --api Gemini

# 全4サービスを実行する場合
python tests/test_agent_live.py --run-live-api
```

選択していないサービスはテストに含めず、結果にも表示しません。
選択したサービスの環境変数が未設定または空の場合は、接続前にそのテストが失敗します。
APIエラーやSDKの不整合、空の回答も失敗になり、終了コードは非ゼロになります。
テストはモデル名を自動で補完しません。

GeminiのテストではHTTPタイムアウトを60秒に設定し、SDKのリトライを無効にします。
応答待ちがタイムアウトするとエラーとして終了します。これはHTTP通信のタイムアウトであり、
テスト全体が厳密に60秒以内に終了することを保証するものではありません。
テスト内で実SDKクライアントの生成時の設定だけを上書きし、既存の `Agent.generate_text()` を呼び出します。
アプリ本体の通信設定には影響しません。
他のサービスのタイムアウトとリトライは各SDKの標準設定に従います。
テスト側では追加のリトライを行いません。
このテストが成功しても、長文入力や全モードの動作まで保証するものではありません。

## 更新時の使い方

SDK更新前後で同じモデルを指定して実行します。
モデル更新時はモデル名の環境変数を変更して、同じテストを実行します。
Python環境の依存関係を更新していなければ、新しいSDKでの検証にはなりません。

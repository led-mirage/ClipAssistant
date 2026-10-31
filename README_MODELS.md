# ClipAssistant AI 対応モデル一覧

v1.3.1で実APIへの接続を確認したモデルと、確認時の注意点をまとめます。
確認日は **2026年10月31日** です。各モデルに短い入力を送り、空でない回答が取得できることを検証しています。
全モード・長文入力・回答品質の評価ではありません。モデルの提供状況や利用権限は、利用するアカウントによって異なります。

確認環境：Python 3.14.10、openai 3.37.0、anthropic 2.3.0、google-genai 2.33.0。
Gemini 3.8 Flashは、下記のとおり更新前のSDKでの成功結果も併記しています。

## 設定方法

`config.yaml` の `ai.api` と `ai.model` に、下記のAPI名とモデルIDを指定します。

```yaml
ai:
  api: OpenAI
  model: gpt-5.1
```

APIキーなどの設定は [設定ガイド](README_CONFIG.md) を参照してください。
アプリにはモデルIDの固定リストによる制限はありません。一覧外のモデルも、呼び出し先APIとリクエスト形式に対応していれば指定できます。

## OpenAI

`ai.api: OpenAI`。以下の20モデルは、上記の確認環境ですべて接続に成功しました。
現在のアプリはChat Completions API（`/chat/completions`）を使用します。

| モデル名 | `ai.model` |
|---|---|
| GPT-6 Astra | `gpt-6-astra` |
| GPT-6.1 Sol | `gpt-6.1-sol` |
| GPT-6 Luna | `gpt-6-luna` |
| GPT-6 Sol | `gpt-6-sol` |
| GPT-5.6 Luna | `gpt-5.6-luna` |
| GPT-5.6 Terra | `gpt-5.6-terra` |
| GPT-5.6 Sol | `gpt-5.6-sol` |
| GPT-5.5 | `gpt-5.5` |
| GPT-5.4 | `gpt-5.4` |
| GPT-5.4 mini | `gpt-5.4-mini` |
| GPT-5.4 nano | `gpt-5.4-nano` |
| GPT-5.2 | `gpt-5.2` |
| GPT-5.1 | `gpt-5.1` |
| GPT-5 | `gpt-5` |
| GPT-5 mini | `gpt-5-mini` |
| GPT-5 nano | `gpt-5-nano` |
| GPT-4.1 | `gpt-4.1` |
| GPT-4.1 mini | `gpt-4.1-mini` |
| GPT-4o | `gpt-4o` |
| GPT-4o mini | `gpt-4o-mini` |

テスト時にChat Completions API非対応の応答があった次の5モデルは、現在のアプリの対象から外しています。

- `gpt-5.5-pro`
- `gpt-5.4-pro`
- `gpt-5.3-codex`
- `gpt-5.2-pro`
- `gpt-5-pro`

`gpt-4.1-nano` と `gpt-3.5-turbo` は、テスト時に廃止済みとの応答があったため対象から外しています。

## Azure OpenAI

`ai.api: AzureOpenAI`。確認環境では、GPT-5.6 Solを利用するデプロイ `gpt-5.6-sol` で接続に成功しました。
Azureの場合、`ai.model` には利用するAzureリソース上の **デプロイ名** を指定します。
モデルIDとデプロイ名が一致するとは限りません。また、OpenAI側の確認結果がそのままAzureの全デプロイに適用されるわけではありません。

```yaml
ai:
  api: AzureOpenAI
  model: your-deployment-name
  azure_api_key_envvar: AZURE_OPENAI_API_KEY
  azure_endpoint_envvar: AZURE_OPENAI_ENDPOINT
```

環境変数には実際のAPIキーとエンドポイントを登録してください。

## Anthropic Claude

`ai.api: Claude`。以下の12モデルは、上記の確認環境ですべて接続に成功しました。

| モデル名 | `ai.model` | テスト時の補足 |
|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | |
| Claude Fable 5 | `claude-fable-5` | |
| Claude Opus 5.5 | `claude-opus-5-5` | |
| Claude Opus 4.8 | `claude-opus-4-8` | |
| Claude Opus 4.7 | `claude-opus-4-7` | |
| Claude Opus 4.6 | `claude-opus-4-6` | |
| Claude Opus 4.5 | `claude-opus-4-5` | |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | SDKから2026年11月30日提供終了予定の警告あり |
| Claude Haiku 5.5 | `claude-haiku-5-5` | |
| Claude Haiku 4.5 | `claude-haiku-4-5` | |

## Google Gemini

`ai.api: Gemini`。以下の8モデルをテストしています。

| モデル名 | `ai.model` | 確認結果 |
|---|---|---|
| Gemini 3.8 Flash | `gemini-3.8-flash` | SDK 2.10.0で成功実績あり。2.33.0での確認時は504 `DEADLINE_EXCEEDED` |
| Gemini 3.6 Flash | `gemini-3.6-flash` | SDK 2.33.0で成功 |
| Gemini 3.5 Flash | `gemini-3.5-flash` | SDK 2.33.0で成功 |
| Gemini 3.5 Flash Lite | `gemini-3.5-flash-lite` | SDK 2.33.0で成功 |
| Gemini 3.1 Flash Lite | `gemini-3.1-flash-lite` | SDK 2.33.0で成功 |
| Gemini 3 Flash Preview | `gemini-3-flash-preview` | SDK 2.33.0で成功 |
| Gemini 2.5 Flash | `gemini-2.5-flash` | SDK 2.33.0で成功 |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` | SDK 2.33.0で成功 |

上記の504は、APIから応答期限切れと通知されたものです。この結果だけでモデル非対応やSDKの不整合とは判断していません。
実APIテストではGeminiのHTTPタイムアウトを60秒に設定し、リトライを無効にしています。アプリ本体はSDKの標準設定を使用します。

## 開発者向け：再確認する場合

テスト対象は [tests/models.yaml](tests/models.yaml) で管理します。これはテスト用の一覧で、アプリの設定は `config.yaml` で行います。
実行手順とログの説明は [実APIの接続テスト](tests/README.md) を参照してください。

```powershell
# 全サービスのモデル一覧を実行（API利用料金が発生します）
.\tests\run_tests.bat all
```

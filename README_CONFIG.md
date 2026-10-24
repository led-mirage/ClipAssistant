# <img src="src/view/app.ico" width="36"> ClipAssistant AI 設定ガイド

© 2026 led-mirage

## 🔑 APIキーの登録

APIキーは Windows の環境変数に登録します。  
Windows の検索窓で`環境変数を編集`と入力すると、環境変数の編集画面が開きます。  
`ユーザー環境変数` に以下の変数を追加してください。

### 📌 OpenAI

| 変数名 | 変数値 |
|-|-|
| OPENAI_API_KEY | OpenAI のAPIキー |

### 📌 Azure OpenAI

| 変数名 | 変数値 |
|-|-|
| AZURE_OPENAI_API_KEY | Azure OpenAI のAPIキー |
| AZURE_OPENAI_ENDPOINT | Azure OpenAI のエンドポイント |

### 📌 Claude

| 変数名 | 変数値 |
|-|-|
| ANTHROPIC_API_KEY | Anthropic Claude のAPIキー |

### 📌 Gemini

| 変数名 | 変数値 |
|-|-|
| GEMINI_API_KEY | Google Gemini のAPIキー |

### 📌 変数名について

参照する変数名は設定ファイル（`config.yaml`）で変更することができます。

<div style="page-break-before:always"></div>

## ⚙️ 設定ガイド (`config.yaml`)

`config.yaml` を編集することで、使用するAIモデルや動作を自分好みに変更できます。

保存後はシステムトレイの「設定の再読み込み」で、API・モデル・モード・フォントサイズを反映できます。
ウィンドウの幅・高さ・`start_hidden` の変更は、アプリの再起動時に反映されます。
Windowsの設定画面で環境変数を追加・変更した場合は、アプリも再起動してください。

### 📌 ai セクション

テキスト処理に使用するAIサービス・モデルと、認証情報を取得する環境変数名を設定します。
プロンプトは後述の `modes` セクションで設定します。

- `api`  
  使用する API を指定します。
  - `OpenAI`
  - `AzureOpenAI`
  - `Claude`
  - `Gemini`

- `model`  
  使用するモデル名を指定します。（例: `gpt-5.1`）
  Azure OpenAIの場合は、Azure側で設定したデプロイ名を指定します。
  現在のOpenAI・Azure OpenAIへの呼び出しはChat Completions APIを使うため、そのAPIに対応するモデルを指定してください。

  モデルIDと接続確認結果は [対応モデル一覧](README_MODELS.md) を参照してください。

- `openai_api_key_envvar`  
  OpenAI 用の API キーを格納している **環境変数名** を指定します。

- `azure_api_key_envvar`  
  Azure OpenAI 用の API キーを格納している **環境変数名** を指定します。

- `azure_endpoint_envvar`  
  Azure OpenAI のエンドポイント URL を格納している **環境変数名** を指定します。

- `claude_api_key_envvar`
  Anthropic Claude の API キーを格納している **環境変数名** を指定します。

- `gemini_api_key_envvar`
  Google Gemini の API キーを格納している **環境変数名** を指定します。

> 💡 環境変数名は、ここで指定した名前が実際に OS に設定されているものと一致している必要があります。

Azure OpenAIで環境ごとに異なる変数名を使う場合の例です。APIキーやURLの実値は環境変数に登録します。

```yaml
ai:
  api: AzureOpenAI
  model: your-deployment-name
  azure_api_key_envvar: AZURE_OPENAI_API_KEY
  azure_endpoint_envvar: AZURE_OPENAI_ENDPOINT
```

現在のAPIとモデル名は、タイトルバーの `バージョン番号   [ API / モデル名 ]` で確認できます。
Azure OpenAIの場合、モデル名の位置にはデプロイ名を表示します。

<div style="page-break-before:always"></div>

### 📌 modes セクション

AIの「振る舞い」を定義するモードをリスト形式で設定します。用途に合わせて自由に定義を追加・削除できます。

* **`label`** アプリ画面左上のドロップダウンメニューに表示される名前です。
* **`system_prompt`** AIに与える役割や制約条件（システムプロンプト）を指定します。ここで「あなたは優秀な翻訳者です」といった指示を出すことで、生成される回答の質をコントロールします。
* **`user_prompt`** ユーザーがコピーしたテキストの直前に挿入される命令文です。
* **`usage_message`** そのモードを選択した際、テキストエリアに初期表示される説明文です。使い方のヒントを記載しておくと便利です。
* **`display_original_text`** 生成結果の後に、コピーした元の文章を表示するかどうかを `true` または `false` で指定します。

#### 💡 モードのカスタマイズ例

例えば、コピーした文章を関西弁のお姉さんに要約してもらいたい場合は、以下のように設定を追加します。

```yaml
  - label: "関西弁要約"
    system_prompt: "あなたは陽気な関西人の女性です。入力された文章を、親しみやすい関西弁で分かりやすく要約してください。"
    user_prompt: "以下の文章を関西弁で要約してや："
    usage_message: "テキストをコピーしてCtrl+Cを2回押すと、関西弁のお姉さんが要約してくれるで！"
    display_original_text: true
```

### 📌 window セクション

生成結果を表示するウィンドウの見た目を設定します。

- `width`  
  ウィンドウの幅（ピクセル）

- `height`  
  ウィンドウの高さ（ピクセル）

- `font_size`  
  フォントサイズ（ピクセル）

- `start_hidden`  
  `true` に設定すると、アプリ起動時にウィンドウを表示せず、タスクトレイに最小化された状態で起動します。（デフォルト: `false`）

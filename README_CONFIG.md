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

## ⚙️ 設定ガイド (`config.yaml`)

`config.yaml` を編集することで、使用するAIモデルや動作を自分好みに変更できます。

### 📌 ai セクション

翻訳に使用する AI サービスやプロンプトを設定します。

- `api`  
  使用する API を指定します。
  - `OpenAI`
  - `AzureOpenAI`
  - `Claude`
  - `Gemini`

- `model`  
  使用するモデル名を指定します。（例: `gpt-5.1`）

- `openai_api_key_envvar`  
  OpenAI 用の API キーを格納している **環境変数名** を指定します。

- `azure_api_key_envvar`  
  Azure OpenAI 用の API キーを格納している **環境変数名** を指定します。

- `azure_endpoint_envvar`  
  Azure OpenAI のエンドポイント URL を格納している **環境変数名** を指定します。

- `claude_endpoint_envvar`  
  Anthropic Claude のエンドポイント URL を格納している **環境変数名** を指定します。

- `gemini_endpoint_envvar`  
  Google Gemini のエンドポイント URL を格納している **環境変数名** を指定します。

> 💡 環境変数名は、ここで指定した名前が実際に OS に設定されているものと一致している必要があります。

### 📌 modes セクション

AIの「振る舞い」を定義するモードをリスト形式で設定します。用途に合わせて自由に定義を追加・削除できます。

* **`label`** アプリ画面左上のドロップダウンメニューに表示される名前です。
* **`system_prompt`** AIに与える役割や制約条件（システムプロンプト）を指定します。ここで「あなたは優秀な翻訳者です」といった指示を出すことで、生成される回答の質をコントロールします。
* **`user_prompt`** ユーザーがコピーしたテキストの直前に挿入される命令文です。
* **`usage_message`** そのモードを選択した際、テキストエリアに初期表示される説明文です。使い方のヒントを記載しておくと便利です。
* **`display_original_text`** 生成結果の後に、コピーした元の文章を表示するかどうかを `true` または `false` で指定します。

 ####💡 モードのカスタマイズ例

例えば、コピーした文章を関西弁のお姉さんに要約してもらいたい場合は、以下のように設定を追加します。

```yaml
  - label: "関西弁要約"
    system_prompt: "あなたは陽気な関西人の女性です。入力された文章を、親しみやすい関西弁で分かりやすく要約してください。"
    user_prompt: "以下の文章を関西弁で要約してや："
    usage_message: "テキストをコピーしてCtrl+Cを2回押すと、関西弁のお姉さんが要約してくれるで！"
    display_original_text: true
```

### 📌 window セクション

翻訳結果を表示するウィンドウの見た目を設定します。

- `width`  
  ウィンドウの幅（ピクセル）

- `height`  
  ウィンドウの高さ（ピクセル）

- `font_size`  
  フォントサイズ（ポイント）

- `start_hidden`  
  `true` に設定すると、アプリ起動時にウィンドウを表示せず、タスクトレイに最小化された状態で起動します。（デフォルト: `false`）

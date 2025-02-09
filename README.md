# 解釈君 (Kaishyakukun) 🤖

> 複数のWebサイトを同時にクロールし、ChatGPTで解析する高性能な分析ツール 🚀

## ✨ 主な機能

- 🌐 複数URLの同時クローリング（最大10サイト）
- 🔄 非同期処理による高速な並行処理
- 🧠 ChatGPTによるコンテンツ分析
- ⚙️ 柔軟な設定管理（INIファイル対応）
- 🛡️ エラーハンドリングと適切なバリデーション

## 🔧 必要条件

- 📌 Python 3.8+
- 📌 FastAPI
- 📌 OpenAI API キー

## 🚀 クイックスタート

### 1️⃣ インストール

```bash
git clone https://github.com/dendencat/kaishyakukun.git
cd kaishyakukun
pip install -r requirements.txt
```

### 2️⃣ 環境設定

`.env`ファイルを作成して必要な環境変数を設定:

```env
OPENAI_API_KEY=your_api_key_here
LOG_LEVEL=INFO
RATE_LIMIT=60
```

### 3️⃣ クロール設定

`config.ini`でクロール対象のURLを設定:

```ini
[crawler]
max_urls = 10
urls = 
    https://example1.com
    https://example2.com
```

## 💻 使用方法

### APIサーバーの起動

```bash
uvicorn src.main:app --reload
```

### 📝 API エンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/analyze`   | POST    | URLの分析実行 |
| `/health`    | GET     | 死活監視 |

### 🔍 APIリクエスト例

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

## ⚠️ エラーハンドリング

| エラー | 説明 |
|-------|------|
| 🚫 設定ファイルなし | FileNotFoundError |
| 📊 URL制限超過 | ValueError (max: 10) |
| 🔥 実行時エラー | 500 Internal Server Error |

## 📚 プロジェクト構造

```
kaishyakukun/
├── 📁 src/
│   ├── 📄 main.py          # FastAPI アプリケーション
│   ├── 📄 crawler.py       # クローリングロジック
│   └── 📄 config.py        # 設定管理
├── 📄 config.ini           # クロール設定
├── 📄 .env                 # 環境変数
└── 📄 README.md           # このファイル
```

## 🤝 コントリビューション

1. Forkする 🍴
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをPush (`git push origin feature/amazing-feature`)
5. Pull Requestを作成 📮

## 📜 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

---
Made with ❤️ by [@dendencat](https://github.com/dendencat)

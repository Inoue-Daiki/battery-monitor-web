# Battery Monitor Web

デバイスのバッテリー残量を監視・記録するWebアプリケーション

## 機能

- 複数デバイスのバッテリー残量監視
- 履歴データの可視化（グラフ表示）
- Apple風UI
- REST API（Swagger仕様書付き）

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定（任意）
cp .env.example .env

# アプリ起動
python app.py
```

## 使い方

1. ブラウザで `http://localhost:5001` を開く
2. 端末から以下でデータ送信：
   ```bash
   python battery_post.py
   ```

## API

- `GET /api/summary` - 各デバイスの最新状態
- `POST /api/post` - バッテリーデータ送信
- `GET /api/history/<device_name>` - 履歴取得
- `GET /apidocs/` - Swagger UI

## 技術スタック

- Backend: Flask, SQLAlchemy, SQLite
- Frontend: HTML, CSS, Chart.js
- Architecture: Service Layer Pattern
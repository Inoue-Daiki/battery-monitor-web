from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from models.battery_log import db, BatteryLog
from services.battery_service import BatteryService
from config import Config
from utils.logger import setup_logger
import os

def create_app():
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(Config)
    
    # 拡張機能初期化
    db.init_app(app)
    CORS(app)
    swagger = Swagger(app)
    
    # ログ設定
    logger = setup_logger('battery_app', app.config['LOG_LEVEL'])
    
    # サービス初期化
    battery_service = BatteryService(db)
    
    # DB作成
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

    @app.route("/")
    def index():
        """
        トップページ
        ---
        responses:
          200:
            description: トップページHTML
        """
        return app.send_static_file("index.html")

    @app.route("/api/summary")
    def api_summary():
        """
        各デバイスの最新状態を取得
        ---
        responses:
          200:
            description: デバイス一覧
            schema:
              type: array
              items:
                type: object
                properties:
                  device_name:
                    type: string
                  level:
                    type: number
                  charging:
                    type: boolean
                  timestamp:
                    type: string
        """
        try:
            result = battery_service.get_latest_by_device()
            logger.info(f"Summary requested, returned {len(result)} devices")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in api_summary: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/post", methods=["POST"])
    def api_post():
        """
        バッテリー情報を保存
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                device_name:
                  type: string
                level:
                  type: number
                charging:
                  type: boolean
        responses:
          200:
            description: 保存成功
        """
        try:
            device_data = request.json
            logger.info(f"Battery data received for {device_data.get('device_name')}")
            result = battery_service.save_battery_log(device_data)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in api_post: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/history/<device_name>")
    def api_history(device_name):
        """
        指定デバイスの履歴を取得
        ---
        parameters:
          - name: device_name
            in: path
            type: string
            required: true
        responses:
          200:
            description: デバイス履歴
        """
        try:
            result = battery_service.get_device_history(device_name)
            logger.info(f"History requested for {device_name}, returned {len(result)} records")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in api_history: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/device/<device_name>")
    def detail(device_name):
        """
        デバイス詳細ページ
        ---
        parameters:
          - name: device_name
            in: path
            type: string
            required: true
        responses:
          200:
            description: 詳細ページHTML
        """
        return app.send_static_file("detail.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])

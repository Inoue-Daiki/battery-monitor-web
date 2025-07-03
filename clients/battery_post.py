import requests
import json
import subprocess
import platform

def get_battery_info():
    # macOSの場合
    if platform.system() == "Darwin":
        try:
            output = subprocess.check_output(["pmset", "-g", "batt"]).decode()
            print(f"Debug: pmset output: {output}")  # デバッグ用
            
            # バッテリー残量を取得
            lines = output.split('\n')
            battery_line = None
            for line in lines:
                if 'InternalBattery' in line or '%' in line:
                    battery_line = line
                    break
            
            if not battery_line:
                print("バッテリー情報が見つかりません")
                return None, None
            
            print(f"Debug: battery_line: {battery_line}")  # デバッグ用
            
            # パーセンテージを取得
            percent_parts = battery_line.split('\t')[1] if '\t' in battery_line else battery_line
            percent = int(percent_parts.split('%')[0].strip())
            
            # 充電状態を判定（より広範囲に）
            charging = False
            
            # battery_lineの中身をチェック
            battery_lower = battery_line.lower()
            output_lower = output.lower()
            
            if "charging" in battery_lower:
                charging = True
            elif "ac power" in battery_lower:
                charging = True
            elif "finishing charge" in battery_lower:
                charging = True
            elif "charged" in battery_lower:
                # 満充電でも電源接続中なら充電状態とする
                charging = True
            elif "discharging" in battery_lower:
                charging = False
            elif "battery power" in battery_lower:
                charging = False
            else:
                # 判定できない場合はAC電源の状態を確認
                if "ac power" in output_lower:
                    charging = True
                else:
                    charging = False
            
            print(f"Debug: percent={percent}, charging={charging}")  # デバッグ用
            return percent / 100, charging
            
        except Exception as e:
            print("バッテリー情報取得失敗:", e)
            return None, None
    
    # Linuxの場合
    elif platform.system() == "Linux":
        try:
            with open("/sys/class/power_supply/BAT0/capacity") as f:
                percent = int(f.read().strip())
            with open("/sys/class/power_supply/BAT0/status") as f:
                status = f.read().strip()
                charging = status in ["Charging", "Full"]
            return percent / 100, charging
        except Exception as e:
            print("バッテリー情報取得失敗:", e)
            return None, None
    else:
        print("未対応OSです")
        return None, None

def get_battery_info_ioreg():
    """ioregを使用してより正確な充電状態を取得"""
    if platform.system() == "Darwin":
        try:
            ioreg_output = subprocess.check_output([
                "ioreg", "-rc", "AppleSmartBattery"
            ]).decode()
            
            print(f"Debug ioreg output: {ioreg_output}")  # デバッグ用
            
            # IsChargingフラグを確認（複数のパターンに対応）
            is_charging = (
                '"IsCharging" = Yes' in ioreg_output or
                '"IsCharging"=Yes' in ioreg_output or
                '"IsCharging" = true' in ioreg_output
            )
            
            external_connected = (
                '"ExternalConnected" = Yes' in ioreg_output or
                '"ExternalConnected"=Yes' in ioreg_output or
                '"ExternalConnected" = true' in ioreg_output
            )
            
            # AdapterInfoも確認
            adapter_info = '"AdapterInfo"' in ioreg_output
            
            print(f"Debug ioreg: IsCharging={is_charging}, ExternalConnected={external_connected}, AdapterInfo={adapter_info}")
            
            # 充電中または外部電源接続中の場合はTrue
            return is_charging or external_connected
            
        except Exception as e:
            print(f"ioreg取得失敗: {e}")
            return None
    return None

# メイン処理
level, charging = get_battery_info()

# より正確な充電状態を取得
if level is not None:
    accurate_charging = get_battery_info_ioreg()
    if accurate_charging is not None:
        if accurate_charging != charging:
            print(f"充電状態を修正: {charging} -> {accurate_charging}")
            charging = accurate_charging
        else:
            print(f"充電状態は一致: {charging}")

if level is None:
    exit(1)

payload = {
    "device_name": platform.node(),
    "level": level,
    "charging": charging
}

print(f"送信データ: {payload}")  # デバッグ用

url = "http://localhost:5001/api/post"
headers = {"Content-Type": "application/json"}

try:
    res = requests.post(url, json=payload, headers=headers)
    print(f"レスポンス: {res.status_code} - {res.text}")
except Exception as e:
    print(f"送信エラー: {e}")
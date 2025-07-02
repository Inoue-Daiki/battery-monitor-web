# 端末側: battery_post.py
import requests
import json
import subprocess
import platform

def get_battery_info():
    # macOSの場合
    if platform.system() == "Darwin":
        try:
            output = subprocess.check_output(["pmset", "-g", "batt"]).decode()
            # 例: 'Now drawing from ...; 95%; charging; ...'
            percent = int(output.split('\t')[1].split(';')[0].replace('%','').strip())
            charging = "charging" in output or "AC Power" in output
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
                charging = "Charging" in f.read()
            return percent / 100, charging
        except Exception as e:
            print("バッテリー情報取得失敗:", e)
            return None, None
    else:
        print("未対応OSです")
        return None, None

level, charging = get_battery_info()
if level is None:
    exit(1)

payload = {
    "device_name": platform.node(),
    "level": level,
    "charging": charging
}

url = "http://localhost:5001/api/post"
headers = {"Content-Type": "application/json"}
res = requests.post(url, json=payload, headers=headers)
print(res.status_code, res.text)
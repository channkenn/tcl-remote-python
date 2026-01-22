from flask import Flask, render_template, request, jsonify
import subprocess
import os
import platform  # 追加：OS判別用
import urllib.parse  # 冒頭に追加
import time

app = Flask(__name__)

# --- 設定項目 ---
TV_IP = "192.168.10.102"

# OSを判別してADBのパスを自動切り替え
if platform.system() == "Windows":
    # Windows（PC）環境
    ADB_PATH = r"C:\pg\platform-tools\adb.exe"
else:
    # Termux (Android/Linux) 環境
    ADB_PATH = "adb"

# --- 以下、send_adb_command などの関数は変更なし ---
# 汎用的なURL起動用
@app.route('/open_url')
def open_url():
    url = request.args.get('url', '')
    if not url:
        return jsonify({"success": False})
    try:
        cmd = [
            ADB_PATH, "shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", url, "com.google.android.youtube.tv"
        ]
        subprocess.run(cmd, capture_output=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/delete_history/<int:count>')
def delete_history(count):
    DEV = "/dev/input/event0"
    try:
        for i in range(count):
            # 1. 決定ボタン長押し（メニュー表示）
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "1"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"])
            time.sleep(1.2) # 長押しの判定待ち
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "0"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"])
            
            time.sleep(0.5) # メニューが出るのを待つ

            # 2. 「履歴から削除」を選択（下1回）
            subprocess.run([ADB_PATH, "shell", "input", "keyevent", "20"])
            time.sleep(0.2)

            # 3. 決定
            subprocess.run([ADB_PATH, "shell", "input", "keyevent", "66"])
            
            # 連続で消す場合、次の動画にフォーカスが移るのを待つ
            time.sleep(0.8)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/clean_channels/<int:count>')
def clean_channels(count):
    DEV = "/dev/input/event0"
    try:
        # JSから送られた回数分ループ
        for i in range(count):
            # 1. 物理長押し
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "1"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"])
            time.sleep(1.2)
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "0"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"])
            
            time.sleep(0.1) 

            # 2. 「チャンネルを非表示」を選択（下4回）
            for _ in range(4):
                subprocess.run([ADB_PATH, "shell", "input", "keyevent", "20"])
                time.sleep(0.1)

            # 3. 決定
            for _ in range(2):
                subprocess.run([ADB_PATH, "shell", "input", "keyevent", "66"])
                time.sleep(0.1)
            time.sleep(0.2)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/clean_shorts')
def clean_shorts():
    # デバイスパスを特定した event0 に設定
    DEV = "/dev/input/event0"
    
    try:
        for i in range(7):  # 5回繰り返す
            # --- 物理OKボタンの長押し再現 ---
            # 1. DOWN (押し下げ) : 1(キー) 28(OKキー) 1(ON)
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "1"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"]) # 同期信号
            
            time.sleep(1.2) # ここが長押しの「長さ」になります
            
            # 2. UP (離す) : 1(キー) 28(OKキー) 0(OFF)
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "1", "28", "0"])
            subprocess.run([ADB_PATH, "shell", "sendevent", DEV, "0", "0", "0"]) # 同期信号
            
            # --- メニューが出た後の操作 ---
            time.sleep(0.1) # メニューアニメーション待ち

            for _ in range(3):
                subprocess.run([ADB_PATH, "shell", "input", "keyevent", "20"])
                time.sleep(0.1)

            # 決定（ここは通常のkeyeventでOK）
            subprocess.run([ADB_PATH, "shell", "input", "keyevent", "66"])
            
            time.sleep(0.1) # 次の動画へのスライド待ち
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/open_search')
def open_search():
    try:
        # キーコード 84 は Android の標準検索ボタン（KEYCODE_SEARCH）です
        subprocess.run([ADB_PATH, "shell", "input", "keyevent", "84"], capture_output=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.route('/send_text')
def send_text():
    text = request.args.get('text', '')
    if not text:
        return jsonify({"success": False})
    
    # スペースをエスケープ（ADBの仕様上、スペースは%sに変換する必要がある場合があります）
    encoded_text = text.replace(" ", "%s")
    
    try:
        # ADBでテキストを送信
        subprocess.run([ADB_PATH, "shell", "input", "text", encoded_text], capture_output=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
def send_adb_command(key_code):
    try:
        # 1. 接続を確認
        subprocess.run([ADB_PATH, "connect", f"{TV_IP}:5555"], capture_output=True)
        # 2. キーイベントを送信
        subprocess.run([ADB_PATH, "shell", "input", "keyevent", str(key_code)], capture_output=True)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def launch_app(package_name):
    """パッケージ名を指定してアプリを起動する"""
    try:
        subprocess.run([ADB_PATH, "connect", f"{TV_IP}:5555"], capture_output=True)
        
        if "amazonvideo" in package_name:
            # Prime Videoはam startコマンドの方が確実
            cmd = [ADB_PATH, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-n", f"{package_name}/com.amazon.ignition.IgnitionActivity"]
        else:
            # YouTubeなどはmonkeyコマンドで起動
            cmd = [ADB_PATH, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        
        subprocess.run(cmd, capture_output=True)
        return True
    except Exception as e:
        print(f"Error launching app: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_key/<int:key_code>')
def send_key(key_code):
    print(f"Sending Key: {key_code}")
    success = send_adb_command(key_code)
    return jsonify({"success": success})

@app.route('/launch/<app_name>')
def launch(app_name):
    packages = {
        "youtube": "com.google.android.youtube.tv",
        "prime_video": "com.amazon.amazonvideo.livingroom"
    }
    pkg = packages.get(app_name)
    if pkg:
        success = launch_app(pkg)
        return jsonify({"success": success})
    return jsonify({"success": False}), 404

if __name__ == '__main__':
    # Flaskサーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5000)
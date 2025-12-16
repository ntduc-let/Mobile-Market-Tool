import subprocess
import json
import sqlite3
import pandas as pd
import datetime
import os

# --- CẤU HÌNH ---
NODE_SCRIPT = "scraper.js"
JSON_FILE = "data/raw_data.json"
DB_PATH = "data/market_data.db"

def run_node_scraper():
    print("🔄 Python đang gọi Node.js...")
    # Gọi lệnh 'node scraper.js' từ Python
    try:
        subprocess.run(["node", NODE_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy Node.js: {e}")
        exit()
    except FileNotFoundError:
        print("❌ Không tìm thấy lệnh 'node'. Hãy cài Node.js trước!")
        exit()

def load_json_to_db():
    if not os.path.exists(JSON_FILE):
        print("❌ Không tìm thấy file JSON. Node.js chạy thất bại?")
        return

    print("📥 Đang đọc dữ liệu JSON...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("⚠️ File JSON rỗng.")
        return

    # Chuẩn hóa dữ liệu
    clean_data = []
    for item in data:
        clean_data.append({
            'scraped_at': datetime.datetime.now(),
            'category': item.get('category'),
            'collection_type': item.get('collection_type'),
            'rank': item.get('rank'),
            'app_id': item.get('appId'),
            'title': item.get('title'),
            'developer': item.get('developer'),
            'score': item.get('score', 0),
            'installs': item.get('installs', 'N/A'),
            'reviews': 0, # Node lib basic list ko trả về review count, cần detail nếu muốn
            'price': item.get('price', 0),
            'currency': 'VND'
        })

    # Lưu vào DB
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame(clean_data)
    
    # Tạo bảng nếu chưa có
    conn.execute('''
        CREATE TABLE IF NOT EXISTS app_history (
            scraped_at TIMESTAMP, category TEXT, collection_type TEXT, rank INT,
            app_id TEXT, title TEXT, developer TEXT, score REAL,
            installs TEXT, reviews INT, price REAL, currency TEXT
        )
    ''')
    
    df.to_sql('app_history', conn, if_exists='append', index=False)
    conn.close()
    print(f"💾 Đã nạp thành công {len(clean_data)} dòng vào Database SQLite.")

if __name__ == "__main__":
    run_node_scraper()
    load_json_to_db()
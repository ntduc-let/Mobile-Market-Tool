import os
import shutil
import subprocess
import time
import json
import sqlite3
import datetime
import pandas as pd
import streamlit as st
from .config import DB_PATH, NODE_SCRIPT

def init_environment():
    if not os.path.exists('data'): os.makedirs('data')
    install_flag = "install_v10_final.lock"
    
    if not os.path.exists(install_flag):
        st.toast("♻️ Đang khởi tạo hệ thống...", icon="🚀")
        if os.path.exists('node_modules'): shutil.rmtree('node_modules', ignore_errors=True)
        if os.path.exists('package-lock.json'): os.remove('package-lock.json')

        try:
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
            with open(install_flag, 'w') as f: f.write("ok")
            st.toast("✅ Cài đặt xong!", icon="🎉")
            time.sleep(1)
            st.rerun()
        except subprocess.CalledProcessError:
            st.error("❌ Lỗi cài đặt Node.js.")
            st.stop()

def run_node_safe(mode, target, country, output_file, token=None, limit=None):
    file_path = f"data/{output_file}"
    if os.path.exists(file_path): 
        try: os.remove(file_path)
        except: pass
    
    cmd = ["node", NODE_SCRIPT, mode, target, country]
    
    # Quan trọng: Nếu token có giá trị, thêm vào args. Nếu không thì KHÔNG thêm (tránh lỗi undefined string)
    if token: 
        cmd.append(str(token))
    
    # Limit chỉ dùng cho list/search, Detail không dùng limit kiểu này
    if limit:
        cmd.append(str(limit))
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception as e:
        print(f"Error Node: {e}")
        return None
    return None

def run_node_safe_custom(mode, target, country, output_file, *extra_args):
    file_path = f"data/{output_file}"
    if os.path.exists(file_path): 
        try: os.remove(file_path)
        except: pass
    try:
        cmd = ["node", NODE_SCRIPT, mode, target, country] + list(extra_args)
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=90)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
    return []
# -----------------------------------------

def save_data_to_db(category_id, country_code):
    try:
        with open("data/raw_data.json", 'r', encoding='utf-8') as f: data = json.load(f)
    except: return False
    
    if not data: return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS app_history (
            scraped_at TIMESTAMP, category TEXT, country TEXT, collection_type TEXT,
            rank INT, app_id TEXT, title TEXT, developer TEXT, score REAL,
            installs TEXT, price REAL, currency TEXT, icon TEXT, reviews INT)''')
    
    today = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
    cursor.execute("DELETE FROM app_history WHERE category=? AND country=? AND scraped_at>=?", (category_id, country_code, today))
    
    clean = []
    ts = datetime.datetime.now()
    for i in data:
        clean.append((
            ts, i.get('category'), i.get('country'), i.get('collection_type'), i.get('rank'),
            i.get('appId') or i.get('app_id'), i.get('title'), i.get('developer'), i.get('score', 0), 
            i.get('installs', 'N/A'), i.get('price', 0), 'VND', i.get('icon', ''), 0
        ))
    cursor.executemany('INSERT INTO app_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', clean)
    conn.commit(); conn.close()
    return True

def load_data_today(cat, country):
    conn = sqlite3.connect(DB_PATH)
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        df = pd.read_sql(f"SELECT * FROM app_history WHERE category='{cat}' AND country='{country}' AND strftime('%Y-%m-%d', scraped_at)='{today}'", conn)
        conn.close(); return df
    except: conn.close(); return pd.DataFrame()
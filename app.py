import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import os
import json
import datetime
import plotly.graph_objects as go
import plotly.express as px
import re
import time
import shutil

st.set_page_config(page_title="Mobile Market Analyzer", layout="wide", page_icon="📱")
DB_PATH = 'data/market_data.db'
NODE_SCRIPT = 'scraper.js'

# --- 1. SETUP NODE ENVIRONMENT (FIX: FORCE DOWNGRADE TO V9) ---
def setup_node_env():
    current_dir = os.getcwd()
    node_modules = os.path.join(current_dir, "node_modules")
    lib_check = os.path.join(node_modules, "google-play-scraper")
    
    # Set biến môi trường
    os.environ["NODE_PATH"] = node_modules

    # Nội dung package.json BẮT BUỘC cho bản v9 (không dùng type: module)
    pkg_config = {
        "name": "market-tool",
        "version": "1.0.0",
        "description": "Scraper V9",
        "dependencies": {
            "google-play-scraper": "^9.1.1"  # <--- BẢN 9.1.1 LÀ CHÌA KHÓA
        }
    }
    
    # Logic kiểm tra: Nếu đang dùng bản cũ/sai config thì phải xóa đi làm lại
    need_reinstall = False
    
    if os.path.exists("package.json"):
        try:
            with open("package.json", "r") as f:
                existing = json.load(f)
                # Nếu file config có dòng "type": "module" -> Đó là bản v10 gây lỗi -> Cài lại
                if existing.get("type") == "module":
                    need_reinstall = True
        except:
            need_reinstall = True
    else:
        need_reinstall = True

    # Thực hiện cài đặt
    if need_reinstall or not os.path.exists(lib_check):
        placeholder = st.empty()
        with placeholder.status("🧹 Đang hạ cấp xuống bản ổn định (v9)...", expanded=True) as status:
            try:
                # 1. Xóa sạch thư mục cũ
                if os.path.exists("node_modules"):
                    shutil.rmtree("node_modules", ignore_errors=True)
                if os.path.exists("package-lock.json"):
                    os.remove("package-lock.json")
                
                # 2. Tạo file package.json mới
                with open("package.json", "w") as f:
                    json.dump(pkg_config, f, indent=2)
                
                status.write("⬇️ Đang chạy `npm install`...")
                subprocess.run("npm install", shell=True, check=True, cwd=current_dir)
                
                status.update(label="✅ Đã xong! Hệ thống đang khởi động lại...", state="complete")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi cài đặt: {e}")
                st.stop()

setup_node_env()

# --- 2. RUN NODE SCRAPER (GIỮ NGUYÊN) ---
def run_node_scraper(mode, target, country, output_file, token=None):
    file_path = f"data/{output_file}"
    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass
    
    args = ["node", NODE_SCRIPT, mode, target, country]
    if token: args.append(token)
    
    current_dir = os.getcwd()
    env_vars = os.environ.copy()
    env_vars["NODE_PATH"] = os.path.join(current_dir, "node_modules")
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=current_dir,
            env=env_vars
        )
        
        if result.returncode != 0:
            return None, result.stderr
            
        json_str = result.stdout.strip()
        if not json_str: return None, "Empty response"
            
        data = json.loads(json_str)
        return data, None

    except Exception as e:
        return None, str(e)

# --- 3. DATABASE & UI FUNCTIONS (GIỮ NGUYÊN NHƯ CŨ) ---
def save_chart_data(data, category_id, country_code):
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
    for i, app in enumerate(data):
        clean.append((
            ts, category_id, country_code, app.get('collection_type', 'unknown'),
            i + 1, app.get('appId'), app.get('title'), app.get('developer'),
            app.get('score', 0), app.get('installs', 'N/A'), 
            app.get('price', 0), 'VND', app.get('icon', ''), 0
        ))
        
    cursor.executemany('INSERT INTO app_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', clean)
    conn.commit()
    conn.close()
    return True

def load_data_today(cat, country):
    conn = sqlite3.connect(DB_PATH)
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        df = pd.read_sql(f"SELECT * FROM app_history WHERE category='{cat}' AND country='{country}' AND strftime('%Y-%m-%d', scraped_at)='{today}'", conn)
        conn.close(); return df
    except: return pd.DataFrame()

def load_app_history(app_id, country):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(f"SELECT scraped_at, rank, collection_type FROM app_history WHERE app_id='{app_id}' AND country='{country}' ORDER BY scraped_at ASC", conn)
        conn.close(); return df
    except: return pd.DataFrame()

def estimate_revenue(d, country):
    if not d: return "N/A"
    tier_multiplier = 5.0 if country in ['us', 'jp', 'kr', 'uk', 'au', 'ca', 'de'] else 1.0
    is_game = "GAME" in str(d.get('genreId', '')).upper()
    installs = int(re.sub(r'[^\d]', '', str(d.get('installs', '0')))) if d.get('installs') else 0
    est = installs * 0.05 * 0.02 * (15.0 if is_game else 5.0) * tier_multiplier
    if est > 1000000: return f"${est/1000000:.1f}M / tháng"
    return f"${est/1000:.1f}K / tháng" if est > 1000 else "< $1K / tháng"

def render_mini_card(app, country, rank_idx, key_prefix):
    icon = app.get('icon') or 'https://via.placeholder.com/72'
    title = app.get('title', 'Unknown')
    dev = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    rank = rank_idx + 1
    aid = app.get('appId') or f"u_{rank}"
    
    st.markdown(f"""
    <div class="app-card-modern">
        <div class="card-content-flex">
            <div class="rank-number">#{rank}</div>
            <img src="{icon}" class="app-icon-img">
            <div class="app-info-box">
                <div class="app-title-modern" title="{title}">{title}</div>
                <div class="app-publisher-modern">{dev}</div>
                <div class="metric-score">⭐ {score:.1f}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    if st.button("🔍 Xem chi tiết", key=f"{key_prefix}_{rank}_{aid}", use_container_width=True):
        st.session_state.selected_app = {'app_id': aid, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()

# --- CONFIG & STATE ---
CATEGORIES_LIST = {
    "🎮 Game: Giải đố (Puzzle)": "GAME_PUZZLE",
    "🎮 Game: Hành động (Action)": "GAME_ACTION",
    "🎮 Game: Chiến thuật (Strategy)": "GAME_STRATEGY",
    "🎮 Game: Nhập vai (RPG)": "GAME_ROLE_PLAYING",
    "🎮 Game: Mô phỏng (Simulation)": "GAME_SIMULATION",
    "🎓 Giáo dục (Education)": "EDUCATION",
    "💰 Tài chính (Finance)": "FINANCE",
    "✅ Năng suất (Productivity)": "PRODUCTIVITY",
    "🛠 Công cụ (Tools)": "TOOLS",
    "🏥 Sức khỏe (Health & Fitness)": "HEALTH_AND_FITNESS"
}
COUNTRIES_LIST = { "🇻🇳 Việt Nam": "vn", "🇺🇸 Hoa Kỳ": "us", "🇯🇵 Nhật Bản": "jp", "🇰🇷 Hàn Quốc": "kr", "🇨🇳 Trung Quốc": "cn" }

if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
if 'selected_app' not in st.session_state: st.session_state.selected_app = None
if 'search_results' not in st.session_state: st.session_state.search_results = []
if 'detail_id' not in st.session_state: st.session_state.detail_id = None
if 'detail_country' not in st.session_state: st.session_state.detail_country = None
if 'detail_data' not in st.session_state: st.session_state.detail_data = None
if 'current_reviews' not in st.session_state: st.session_state.current_reviews = []
if 'next_token' not in st.session_state: st.session_state.next_token = None
if 'similar_apps' not in st.session_state: st.session_state.similar_apps = []
if 'dev_apps' not in st.session_state: st.session_state.dev_apps = []

# --- CSS ---
st.markdown("""<style>
.app-card-modern {background: linear-gradient(145deg, #1e2028, #23252e); border-radius: 16px; padding: 16px; margin-bottom: 16px; border: 1px solid #2c303a;}
.rank-number {font-size: 1.4em; font-weight: 900; color: #64b5f6; min-width: 30px;}
.app-icon-img {width: 72px; height: 72px; border-radius: 14px; object-fit: cover; border: 1px solid #333;}
.app-info-box {flex-grow: 1; overflow: hidden; margin-left: 15px;}
.app-title-modern {font-size: 1.15em; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.app-publisher-modern {font-size: 0.9em; color: #b0b3b8;}
.metric-score {color: #ffbd45; font-weight: 700;}
.card-content-flex {display: flex; align-items: flex-start;}
.hero-header {display: flex; gap: 25px; padding: 25px; background: linear-gradient(135deg, #2a2d3a 0%, #1e2028 100%); border-radius: 20px; align-items: center;}
.hero-icon-big {width: 120px; height: 120px; border-radius: 20px; border: 2px solid #444;}
.metric-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;}
.metric-card-custom {background: #23252e; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #333;}
.metric-value {font-size: 1.6em; font-weight: 800; color: #fff; display: block;}
.metric-label {font-size: 0.9em; color: #aaa; text-transform: uppercase;}
div.stButton > button {width: 100%; border-radius: 12px; font-weight: 600;}
</style>""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🚀 Super Tool")
st.sidebar.subheader("🔍 Tìm kiếm")
search_term = st.sidebar.text_input("Nhập Từ khóa / App ID:")
search_country_label = st.sidebar.selectbox("Quốc gia tìm kiếm", list(COUNTRIES_LIST.keys()))
if st.sidebar.button("🔎 Tìm ngay"):
    s_country = COUNTRIES_LIST[search_country_label]
    if "." in search_term and " " not in search_term:
        st.session_state.selected_app = {'app_id': search_term.strip(), 'title': search_term, 'country_override': s_country}
        st.session_state.view_mode = 'detail'
        st.rerun()
    else:
        with st.spinner("Searching..."):
            data, err = run_node_scraper("SEARCH", search_term, s_country, "res.json")
            if err: st.error(f"Lỗi tìm kiếm: {err}")
            elif data:
                st.session_state.search_results = data
                st.session_state.view_mode = 'search_results'
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Top Charts")
sel_country_lbl = st.sidebar.selectbox("Quốc Gia", list(COUNTRIES_LIST.keys()))
sel_cat_lbl = st.sidebar.selectbox("Thể Loại", list(CATEGORIES_LIST.keys()))
target_country = COUNTRIES_LIST[sel_country_lbl]
target_cat = CATEGORIES_LIST[sel_cat_lbl]

if st.sidebar.button("🚀 Quét Chart", type="primary"):
    with st.status("Đang quét Top Chart..."):
        data, err = run_node_scraper("LIST", target_cat, target_country, "chart.json")
        if err:
            st.error("❌ Lỗi Scraper:")
            st.code(err)
        elif data:
            if save_chart_data(data, target_cat, target_country):
                st.success("Xong!")
                st.session_state.view_mode = 'list'
                st.rerun()
            else: st.error("Lỗi lưu Database.")
        else: st.warning("Không có dữ liệu.")

# --- MAIN VIEWS ---
if st.session_state.view_mode == 'list':
    st.title(f"📊 Market: {sel_cat_lbl} ({sel_country_lbl})")
    df = load_data_today(target_cat, target_country)
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.subheader("🔥 Top Free")
            for i, (_, r) in enumerate(df[df['collection_type']=='top_free'].sort_values('rank').head(20).iterrows()): render_mini_card(r, target_country, i, "tf")
        with c2: 
            st.subheader("💸 Top Paid")
            for i, (_, r) in enumerate(df[df['collection_type']=='top_paid'].sort_values('rank').head(20).iterrows()): render_mini_card(r, target_country, i, "tp")
        with c3: 
            st.subheader("💰 Grossing")
            for i, (_, r) in enumerate(df[df['collection_type']=='top_grossing'].sort_values('rank').head(20).iterrows()): render_mini_card(r, target_country, i, "tg")
    else: st.info("👋 Chưa có data. Hãy bấm Quét Chart.")

elif st.session_state.view_mode == 'search_results':
    st.button("⬅️ Back", on_click=lambda: st.session_state.update(view_mode='list'))
    st.title("🔎 Kết quả")
    results = st.session_state.search_results
    cols = st.columns(3)
    for i, app in enumerate(results):
        with cols[i % 3]: render_mini_card(app, COUNTRIES_LIST[search_country_label], i, "sr")

elif st.session_state.view_mode == 'detail' and st.session_state.selected_app:
    app = st.session_state.selected_app
    curr_country = app.get('country_override', target_country)
    aid = app['app_id']
    st.button("⬅️ Back", on_click=lambda: st.session_state.update(view_mode='list'))

    if st.session_state.detail_id != aid or st.session_state.detail_country != curr_country:
        with st.spinner(f"Analyzing {aid}..."):
            st.session_state.detail_data = None
            st.session_state.similar_apps = []
            st.session_state.dev_apps = []
            
            d, err = run_node_scraper("DETAIL", aid, curr_country, "d.json")
            if err: st.error(f"Lỗi Detail: {err}")
            elif d:
                st.session_state.detail_data = d
                st.session_state.current_reviews = d.get('comments', [])
                st.session_state.next_token = d.get('nextToken')
                st.session_state.detail_id = aid
                st.session_state.detail_country = curr_country
                
                sims, _ = run_node_scraper("SIMILAR", aid, curr_country, "s.json")
                if sims: st.session_state.similar_apps = sims
                
                if d.get('developerId'):
                    devs, _ = run_node_scraper("DEVELOPER", str(d['developerId']), curr_country, "dv.json")
                    if devs: st.session_state.dev_apps = devs

    d = st.session_state.detail_data
    if d:
        st.markdown(f"""<div class="hero-header"><img src="{d.get('icon')}" class="hero-icon-big"><div><h1 style='color:white;margin:0'>{d.get('title')}</h1><p style='color:#ccc'>{d.get('developer')}</p></div></div>""", unsafe_allow_html=True)
        col_m = st.columns(4)
        col_m[0].metric("Score", f"{d.get('score', 0):.1f} ⭐")
        col_m[1].metric("Reviews", f"{d.get('ratings', 0):,}")
        col_m[2].metric("Installs", d.get('installs', 'N/A'))
        col_m[3].metric("Revenue Est.", estimate_revenue(d, curr_country))
        
        tabs = st.tabs(["Chart", "Reviews", "Similar", "Dev", "Info"])
        with tabs[0]:
            dfh = load_app_history(d['appId'], curr_country)
            if len(dfh)>1: st.plotly_chart(px.line(dfh, x='scraped_at', y='rank', color='collection_type').update_yaxes(autorange="reversed"), use_container_width=True)
            else: st.info("Chưa đủ data lịch sử.")
            
        with tabs[1]:
            for r in st.session_state.current_reviews:
                st.markdown(f"> **{r['userName']}** ({r['score']}⭐): {r['text']}")
            if st.session_state.next_token and st.button("More Reviews"):
                more, _ = run_node_scraper("MORE_REVIEWS", d['appId'], curr_country, "m.json", st.session_state.next_token)
                if more:
                    st.session_state.current_reviews.extend(more.get('comments', []))
                    st.session_state.next_token = more.get('nextToken')
                    st.rerun()

        with tabs[2]:
            if st.session_state.similar_apps:
                c = st.columns(3)
                for i, s in enumerate(st.session_state.similar_apps[:9]): render_mini_card(s, curr_country, i, "sim")
            else: st.info("Không có dữ liệu.")
            
        with tabs[3]:
            if st.session_state.dev_apps:
                c = st.columns(3)
                for i, dv in enumerate(st.session_state.dev_apps[:9]): render_mini_card(dv, curr_country, i, "dev")
            else: st.info("Không có dữ liệu.")
            
        with tabs[4]:
            st.json(d)
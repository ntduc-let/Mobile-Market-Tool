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

# Hàm kiểm tra và cài đặt node_modules nếu chưa có
def install_npm_packages():
    if not os.path.exists('./node_modules'):
        st.write("Đang cài đặt thư viện Node.js... (Vui lòng đợi 1-2 phút)")
        # Chạy npm install
        subprocess.run(['npm', 'install'], check=True)
        # Hoặc cài cụ thể thư viện nếu không có package.json
        # subprocess.run(['npm', 'install', 'google-play-scraper'], check=True)
        st.success("Cài đặt xong!")

# Gọi hàm này trước khi chạy các logic khác
install_npm_packages()

st.set_page_config(page_title="Mobile Market Analyzer", layout="wide", page_icon="📱")
DB_PATH = 'data/market_data.db'
NODE_SCRIPT = 'scraper.js'

# --- DANH SÁCH THỂ LOẠI (FULL CATEGORIES) ---
CATEGORIES_LIST = {
    # ================= GAMES (TRÒ CHƠI) =================
    "🎮 Game: Hành động (Action)": "GAME_ACTION",
    "🎮 Game: Phiêu lưu (Adventure)": "GAME_ADVENTURE",
    "🎮 Game: Giải trí (Arcade)": "GAME_ARCADE",
    "🎮 Game: Dạng bảng (Board)": "GAME_BOARD",
    "🎮 Game: Bài (Card)": "GAME_CARD",
    "🎮 Game: Sòng bạc (Casino)": "GAME_CASINO",
    "🎮 Game: Phổ thông (Casual)": "GAME_CASUAL",
    "🎮 Game: Giáo dục (Educational)": "GAME_EDUCATIONAL",
    "🎮 Game: Nhạc (Music)": "GAME_MUSIC",
    "🎮 Game: Giải đố (Puzzle)": "GAME_PUZZLE",
    "🎮 Game: Đua xe (Racing)": "GAME_RACING",
    "🎮 Game: Nhập vai (Role Playing)": "GAME_ROLE_PLAYING",
    "🎮 Game: Mô phỏng (Simulation)": "GAME_SIMULATION",
    "🎮 Game: Thể thao (Sports)": "GAME_SPORTS",
    "🎮 Game: Chiến thuật (Strategy)": "GAME_STRATEGY",
    "🎮 Game: Đố vui (Trivia)": "GAME_TRIVIA",
    "🎮 Game: Từ vựng (Word)": "GAME_WORD",

    # ================= APPS (ỨNG DỤNG) =================
    "🎨 Nghệ thuật & Thiết kế (Art & Design)": "ART_AND_DESIGN",
    "🚗 Ô tô & Xe cộ (Auto & Vehicles)": "AUTO_AND_VEHICLES",
    "💄 Làm đẹp (Beauty)": "BEAUTY",
    "📚 Sách & Tài liệu (Books & Reference)": "BOOKS_AND_REFERENCE",
    "💼 Kinh doanh (Business)": "BUSINESS",
    "💬 Truyện tranh (Comics)": "COMICS",
    "🗣️ Liên lạc (Communication)": "COMMUNICATION",
    "💕 Hẹn hò (Dating)": "DATING",
    "🎓 Giáo dục (Education)": "EDUCATION",
    "🎬 Giải trí (Entertainment)": "ENTERTAINMENT",
    "🎉 Sự kiện (Events)": "EVENTS",
    "💰 Tài chính (Finance)": "FINANCE",
    "🍔 Ăn uống (Food & Drink)": "FOOD_AND_DRINK",
    "💪 Sức khỏe (Health & Fitness)": "HEALTH_AND_FITNESS",
    "🏠 Nhà cửa (House & Home)": "HOUSE_AND_HOME",
    "📖 Thư viện & Demo (Libraries & Demo)": "LIBRARIES_AND_DEMO",
    "✨ Phong cách sống (Lifestyle)": "LIFESTYLE",
    "📍 Bản đồ & Dẫn đường (Maps & Navigation)": "MAPS_AND_NAVIGATION",
    "🏥 Y tế (Medical)": "MEDICAL",
    "🎵 Nhạc & Âm thanh (Music & Audio)": "MUSIC_AND_AUDIO",
    "📰 Tin tức & Tạp chí (News & Magazines)": "NEWS_AND_MAGAZINES",
    "👶 Làm cha mẹ (Parenting)": "PARENTING",
    "🎨 Cá nhân hóa (Personalization)": "PERSONALIZATION",
    "📸 Nhiếp ảnh (Photography)": "PHOTOGRAPHY",
    "✅ Năng suất (Productivity)": "PRODUCTIVITY",
    "🛍️ Mua sắm (Shopping)": "SHOPPING",
    "🌐 Mạng xã hội (Social)": "SOCIAL",
    "⚽ Thể thao (Sports App)": "SPORTS",
    "🛠 Công cụ (Tools)": "TOOLS",
    "✈️ Du lịch & Địa phương (Travel & Local)": "TRAVEL_AND_LOCAL",
    "▶️ Xem và sửa Video (Video Players)": "VIDEO_PLAYERS",
    "⛅ Thời tiết (Weather)": "WEATHER"
}

# --- DANH SÁCH QUỐC GIA (FULL LIST) ---
COUNTRIES_LIST = {
    # --- CHÂU Á (ASIA) ---
    "🇻🇳 Việt Nam (VN)": "vn",
    "🇯🇵 Nhật Bản (Japan)": "jp",
    "🇰🇷 Hàn Quốc (Korea)": "kr",
    "🇨🇳 Trung Quốc (China - Limited)": "cn",
    "🇹🇼 Đài Loan (Taiwan)": "tw",
    "🇭🇰 Hồng Kông (Hong Kong)": "hk",
    "🇸🇬 Singapore": "sg",
    "🇹🇭 Thái Lan (Thailand)": "th",
    "🇮🇩 Indonesia": "id",
    "🇵🇭 Philippines": "ph",
    "🇲🇾 Malaysia": "my",
    "🇮🇳 Ấn Độ (India)": "in",
    "🇵🇰 Pakistan": "pk",
    "🇧🇩 Bangladesh": "bd",
    
    # --- BẮC MỸ (NORTH AMERICA) ---
    "🇺🇸 Hoa Kỳ (USA)": "us",
    "🇨🇦 Canada": "ca",
    
    # --- CHÂU ÂU (EUROPE) ---
    "🇬🇧 Anh Quốc (United Kingdom)": "gb",
    "🇩🇪 Đức (Germany)": "de",
    "🇫🇷 Pháp (France)": "fr",
    "🇮🇹 Ý (Italy)": "it",
    "🇪🇸 Tây Ban Nha (Spain)": "es",
    "🇷🇺 Nga (Russia)": "ru",
    "🇳🇱 Hà Lan (Netherlands)": "nl",
    "🇸🇪 Thụy Điển (Sweden)": "se",
    "🇨🇭 Thụy Sĩ (Switzerland)": "ch",
    "🇳🇴 Na Uy (Norway)": "no",
    "🇩🇰 Đan Mạch (Denmark)": "dk",
    "🇫🇮 Phần Lan (Finland)": "fi",
    "🇵🇱 Ba Lan (Poland)": "pl",
    "🇺🇦 Ukraine": "ua",
    "🇹🇷 Thổ Nhĩ Kỳ (Turkey)": "tr",
    "🇵🇹 Bồ Đào Nha (Portugal)": "pt",
    "🇷🇴 Romania": "ro",
    "🇨🇿 Cộng hòa Séc (Czechia)": "cz",
    "🇭🇺 Hungary": "hu",
    "🇧🇪 Bỉ (Belgium)": "be",
    "🇦🇹 Áo (Austria)": "at",
    "🇮🇪 Ireland": "ie",
    
    # --- CHÂU ĐẠI DƯƠNG (OCEANIA) ---
    "🇦🇺 Úc (Australia)": "au",
    "🇳🇿 New Zealand": "nz",
    
    # --- MỸ LATINH (LATAM) ---
    "🇧🇷 Brazil": "br",
    "🇲🇽 Mexico": "mx",
    "🇦🇷 Argentina": "ar",
    "🇨🇱 Chile": "cl",
    "🇨🇴 Colombia": "co",
    "🇵🇪 Peru": "pe",
    
    # --- TRUNG ĐÔNG & CHÂU PHI (MENA) ---
    "🇸🇦 Ả Rập Xê Út (Saudi Arabia)": "sa",
    "🇦🇪 UAE (Các Tiểu vương quốc Ả Rập)": "ae",
    "🇮🇱 Israel": "il",
    "🇪🇬 Ai Cập (Egypt)": "eg",
    "🇿🇦 Nam Phi (South Africa)": "za",
    "🇳🇬 Nigeria": "ng"
}

# --- STATE MANAGEMENT ---
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
if 'selected_app' not in st.session_state: st.session_state.selected_app = None
if 'search_results' not in st.session_state: st.session_state.search_results = []

# Detail States
if 'detail_id' not in st.session_state: st.session_state.detail_id = None
if 'detail_country' not in st.session_state: st.session_state.detail_country = None # <--- BIẾN MỚI ĐỂ CHECK QUỐC GIA
if 'detail_data' not in st.session_state: st.session_state.detail_data = None
if 'current_reviews' not in st.session_state: st.session_state.current_reviews = []
if 'next_token' not in st.session_state: st.session_state.next_token = None
if 'similar_apps' not in st.session_state: st.session_state.similar_apps = []
if 'dev_apps' not in st.session_state: st.session_state.dev_apps = []

# --- CSS ---
st.markdown("""
<style>
    /* --- Giao diện thẻ Mini (List View) --- */
    .app-card-modern {
        background: linear-gradient(145deg, #1e2028, #23252e);
        border-radius: 16px; padding: 16px; margin-bottom: 16px;
        border: 1px solid #2c303a; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.2s ease-in-out;
    }
    .app-card-modern:hover { transform: translateY(-3px); border-color: #64b5f6; box-shadow: 0 6px 16px rgba(100, 181, 246, 0.2); }
    .card-content-flex { display: flex; align-items: flex-start; gap: 15px; margin-bottom: 12px; }
    .rank-number { font-size: 1.4em; font-weight: 900; color: #64b5f6; min-width: 30px; }
    .app-icon-img { width: 72px; height: 72px; border-radius: 14px; object-fit: cover; border: 1px solid #333; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
    .app-info-box { flex-grow: 1; overflow: hidden; }
    .app-title-modern { font-size: 1.15em; font-weight: 700; color: #fff; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .app-publisher-modern { font-size: 0.9em; color: #b0b3b8; margin-bottom: 8px; }
    .metric-score { color: #ffbd45; font-weight: 700; font-size: 0.95em; display: flex; align-items: center; }

    /* --- Giao diện Detail (MỚI) --- */
    .hero-header {
        display: flex; gap: 25px; padding: 25px;
        background: linear-gradient(135deg, #2a2d3a 0%, #1e2028 100%);
        border-radius: 20px; border: 1px solid #3a3f4b;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4); margin-bottom: 25px;
        align-items: center;
    }
    .hero-icon-big { width: 120px; height: 120px; border-radius: 20px; border: 2px solid #444; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .hero-title-text { font-size: 2.2em; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }
    .hero-dev-text { font-size: 1.1em; color: #64b5f6; margin-bottom: 10px; }
    .hero-id-text { font-family: monospace; color: #888; font-size: 0.9em; background: #15171e; padding: 4px 8px; border-radius: 6px;}

    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
    .metric-card-custom {
        background: #23252e; padding: 20px 15px; border-radius: 16px; text-align: center;
        border: 1px solid #333; transition: transform 0.2s;
    }
    .metric-card-custom:hover { transform: translateY(-2px); border-color: #555; }
    .metric-icon { font-size: 1.8em; margin-bottom: 8px; display: block; }
    .metric-value { font-size: 1.6em; font-weight: 800; color: #fff; display: block; }
    .metric-label { font-size: 0.9em; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    
    .review-card-modern {
        background-color: #2a2d3a; padding: 15px; border-radius: 12px;
        margin-bottom: 12px; border-left: 4px solid #ffbd45;
    }
    .review-header { display: flex; justify-content: space-between; margin-bottom: 8px; color: #ccc; font-size: 0.9em;}
    .review-user { font-weight: 700; color: #fff; }
    .review-text { color: #e0e0e0; line-height: 1.5; font-style: italic;}

    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; margin-right: 6px; border: 1px solid rgba(255,255,255,0.1); display: inline-block;}
    .badge-ad { background-color: rgba(230, 81, 0, 0.2); color: #ff9800; }
    .badge-iap { background-color: rgba(27, 94, 32, 0.2); color: #4caf50; }
    .badge-free { background-color: rgba(13, 71, 161, 0.2); color: #64b5f6; }
    .perm-tag { background-color: #333; color: #ccc; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; margin: 3px; display: inline-block; border: 1px solid #444;}
    
    div.stButton > button { width: 100%; border-radius: 12px; font-weight: 600; }
    h4 { color: #64b5f6 !important; margin-top: 20px !important; }
    hr { border-color: #444; margin: 30px 0; }
</style>
""", unsafe_allow_html=True)

# --- BACKEND FUNCTIONS ---
def run_node_safe(mode, target, country, output_file, token=None):
    file_path = f"data/{output_file}"
    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass
    try:
        args = ["node", NODE_SCRIPT, mode, target, country]
        if token: args.append(token)
        subprocess.run(args, capture_output=True, text=True, check=True)
        time.sleep(0.5)
    except Exception as e: return None
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

def save_data_to_db(category_id, country_code):
    if not os.path.exists("data/raw_data.json"): return False
    with open("data/raw_data.json", 'r', encoding='utf-8') as f: data = json.load(f)
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
        clean.append((ts, i.get('category'), i.get('country'), i.get('collection_type'), i.get('rank'), i.get('appId'), i.get('title'), i.get('developer'), i.get('score', 0), i.get('installs', 'N/A'), i.get('price', 0), 'VND', i.get('icon', ''), 0))
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

def load_app_history(app_id, country):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(f"SELECT scraped_at, rank, collection_type FROM app_history WHERE app_id='{app_id}' AND country='{country}' ORDER BY scraped_at ASC", conn)
        conn.close(); return df
    except: return pd.DataFrame()

# --- CARD UI ---
def render_mini_card(app, country, rank_idx, key_prefix):
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/72?text=App'
    title = app.get('title', 'Unknown Title')
    publisher = app.get('developer', 'Unknown Dev')
    score = app.get('score', 0)
    rank = rank_idx + 1
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
    st.markdown(f"""
    <div class="app-card-modern">
        <div class="card-content-flex">
            <div class="rank-number">#{rank}</div>
            <img src="{icon_url}" class="app-icon-img">
            <div class="app-info-box">
                <div class="app-title-modern" title="{title}">{title}</div>
                <div class="app-publisher-modern">{publisher}</div>
                <div class="metric-score">⭐ {score:.1f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Xem chi tiết", key=unique_key, use_container_width=True):
        st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()

# --- SIDEBAR ---
st.sidebar.title("🚀 Super Tool")
st.sidebar.subheader("🔍 Tìm kiếm")
search_term = st.sidebar.text_input("Nhập Từ khóa hoặc App ID:", placeholder="VD: com.facebook.katana")
search_country_label = st.sidebar.selectbox("Quốc gia tìm kiếm", list(COUNTRIES_LIST.keys()), index=0)
if st.sidebar.button("🔎 Tìm ngay"):
    if search_term:
        s_country = COUNTRIES_LIST[search_country_label]
        # XỬ LÝ NẾU LÀ APP ID
        if "." in search_term and " " not in search_term:
            st.session_state.selected_app = {'app_id': search_term.strip(), 'title': search_term, 'country_override': s_country}
            st.session_state.view_mode = 'detail'
            st.rerun()
        # XỬ LÝ NẾU LÀ TỪ KHÓA
        else:
            with st.spinner("Đang tìm kiếm..."):
                res = run_node_safe("SEARCH", search_term, s_country, "search_results.json")
                if res:
                    st.session_state.search_results = res
                    st.session_state.view_mode = 'search_results'
                    st.rerun()
                else: st.error("Lỗi tìm kiếm (Backend Error).")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Top Charts")
sel_country_lbl = st.sidebar.selectbox("Quốc Gia", list(COUNTRIES_LIST.keys()))
sel_cat_lbl = st.sidebar.selectbox("Thể Loại", list(CATEGORIES_LIST.keys()))
target_country = COUNTRIES_LIST[sel_country_lbl]
target_cat = CATEGORIES_LIST[sel_cat_lbl]
if st.sidebar.button("🚀 Quét Chart", type="primary"):
    with st.status("Đang quét..."):
        try:
            # Thêm capture_output=True để bắt lấy nội dung lỗi từ Node.js
            result = subprocess.run(
                ["node", NODE_SCRIPT, "LIST", target_cat, target_country], 
                check=True, 
                text=True, 
                capture_output=True
            )
            
            if save_data_to_db(target_cat, target_country):
                st.session_state.view_mode = 'list'
                st.rerun()
            else: 
                st.error("Không lưu được vào Database.")
                
        except subprocess.CalledProcessError as e:
            # IN RA LỖI THỰC SỰ
            st.error(f"❌ Lỗi chạy Node.js (Exit Code {e.returncode})")
            st.code(e.stderr, language="bash") # Hiển thị thông báo lỗi từ Terminal lên Web
        except Exception as ex:
            st.error(f"❌ Lỗi không xác định: {str(ex)}")

# --- MAIN VIEW ---

# 1. LIST VIEW
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

# 2. SEARCH RESULTS
elif st.session_state.view_mode == 'search_results':
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))
    st.title("🔎 Kết quả tìm kiếm")
    results = st.session_state.search_results
    if results:
        cols = st.columns(3)
        for i, app in enumerate(results):
            with cols[i % 3]: render_mini_card(app, COUNTRIES_LIST[search_country_label], i, "sr")
    else: st.warning("Không tìm thấy kết quả nào.")

# 3. DETAIL VIEW (FIX LỖI ĐỔI COUNTRY)
elif st.session_state.view_mode == 'detail' and st.session_state.selected_app:
    app = st.session_state.selected_app
    curr_country = app.get('country_override', target_country)
    target_id = app['app_id']

    st.button("⬅️ Quay lại danh sách", on_click=lambda: st.session_state.update(view_mode='list'), use_container_width=False)

    # --- LOGIC TẢI DATA ---
    # Fix: Kiểm tra cả ID lẫn COUNTRY. Nếu 1 trong 2 khác thì tải lại.
    if st.session_state.detail_id != target_id or st.session_state.detail_country != curr_country:
        with st.spinner(f"Đang phân tích {target_id} ({curr_country})..."):
            st.session_state.detail_data = None
            st.session_state.similar_apps = []
            st.session_state.dev_apps = []
            
            d = run_node_safe("DETAIL", target_id, curr_country, "app_detail.json")
            if d:
                st.session_state.detail_data = d
                st.session_state.current_reviews = d.get('comments', [])
                st.session_state.next_token = d.get('nextToken', None)
                st.session_state.detail_id = target_id
                st.session_state.detail_country = curr_country # <--- CẬP NHẬT QUỐC GIA HIỆN TẠI
            
            sims = run_node_safe("SIMILAR", target_id, curr_country, "similar_apps.json")
            if sims: st.session_state.similar_apps = sims
            
            dev_id = d.get('developerId') if d else None
            if dev_id:
                devs = run_node_safe("DEVELOPER", str(dev_id), curr_country, "developer_apps.json")
                if devs: st.session_state.dev_apps = devs

    # --- UI RENDER ---
    d = st.session_state.detail_data
    if d:
        # Hero Header
        badges = ""
        if d.get('adSupported'): badges += "<span class='badge badge-ad'>Ads</span>"
        if d.get('offersIAP'): badges += "<span class='badge badge-iap'>IAP</span>"
        badges += f"<span class='badge badge-free'>{d.get('priceText')}</span>"
        
        st.markdown(f"""
        <div class="hero-header">
            <img src="{d.get('icon')}" class="hero-icon-big">
            <div>
                <h1 class="hero-title-text">{d.get('title')}</h1>
                <div class="hero-dev-text">by {d.get('developer')}</div>
                <div style="margin-bottom: 10px;">{badges}</div>
                <span class="hero-id-text">ID: {d.get('appId')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card-custom">
                <span class="metric-icon">⭐</span>
                <span class="metric-value">{d.get('score', 0):.2f}</span>
                <span class="metric-label">Rating</span>
            </div>
            <div class="metric-card-custom">
                <span class="metric-icon">💬</span>
                <span class="metric-value">{d.get('ratings', 0):,}</span>
                <span class="metric-label">Reviews</span>
            </div>
            <div class="metric-card-custom">
                <span class="metric-icon">📥</span>
                <span class="metric-value">{d.get('installs', 'N/A')}</span>
                <span class="metric-label">Installs</span>
            </div>
            <div class="metric-card-custom">
                <span class="metric-icon">🔄</span>
                <span class="metric-value">{d.get('updated', 'N/A')}</span>
                <span class="metric-label">Last Update</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📉 Retention", "📊 Reviews", "⚔️ Đối thủ", "🏢 Cùng Dev", "ℹ️ Thông tin"])

        with tab1:
            df_hist = load_app_history(d['appId'], curr_country)
            if len(df_hist) > 1:
                fig = px.line(df_hist, x='scraped_at', y='rank', color='collection_type', markers=True, title="Lịch sử thứ hạng")
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc')
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Cần quét thêm dữ liệu vào ngày mai để vẽ biểu đồ.")

        with tab2:
            c_filter, c_hist = st.columns([2, 3])
            with c_filter:
                rev_filter = st.selectbox("Lọc đánh giá:", ["Tất cả", "Tích cực (4-5 ⭐)", "Tiêu cực (1-3 ⭐)"])
                all_revs = st.session_state.current_reviews
                show_revs = all_revs
                if rev_filter == "Tích cực (4-5 ⭐)": show_revs = [r for r in all_revs if r['score'] >= 4]
                elif rev_filter == "Tiêu cực (1-3 ⭐)": show_revs = [r for r in all_revs if r['score'] <= 3]
                st.caption(f"Hiển thị {len(show_revs)} / {len(all_revs)} review.")
            with c_hist:
                hist = d.get('histogram')
                if hist:
                    h_df = pd.DataFrame({'Star':['1','2','3','4','5'], 'V': [hist.get('1'),hist.get('2'),hist.get('3'),hist.get('4'),hist.get('5')]})
                    fig = px.bar(h_df, x='Star', y='V', color='Star', color_discrete_sequence=['#e53935','#fb8c00','#fdd835','#7cb342','#43a047'])
                    fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            for r in show_revs:
                star_str = '⭐' * r['score']
                st.markdown(f"""
                <div class="review-card-modern">
                    <div class="review-header">
                        <span class="review-user">{r['userName']}</span>
                        <span>{r['date']}</span>
                    </div>
                    <div style="color: #ffbd45; margin-bottom: 8px;">{star_str}</div>
                    <div class="review-text">"{r['text']}"</div>
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.next_token:
                if st.button("⬇️ Tải thêm review"):
                    more = run_node_safe("MORE_REVIEWS", d['appId'], curr_country, "more_reviews.json", st.session_state.next_token)
                    if more:
                        st.session_state.current_reviews.extend(more.get('comments', []))
                        st.session_state.next_token = more.get('nextToken')
                        st.rerun()

        with tab3:
            sims = st.session_state.similar_apps
            if sims:
                filtered_sims = [s for s in sims if s['appId'] != d['appId']]
                if filtered_sims:
                    sc = st.columns(3)
                    for i, s in enumerate(filtered_sims[:9]): render_mini_card(s, curr_country, i, "sim")
                else: st.warning("Không có đối thủ khác.")
            else: st.info("Chưa tìm thấy dữ liệu.")

        with tab4:
            devs = st.session_state.dev_apps
            if devs:
                filtered_devs = [dv for dv in devs if dv['appId'] != d['appId']]
                if filtered_devs:
                    dc = st.columns(3)
                    for i, dv in enumerate(filtered_devs[:9]): render_mini_card(dv, curr_country, i, "dev")
                else: st.info("Dev này chỉ có 1 app này.")
            else: st.info("Chưa tìm thấy dữ liệu.")

        with tab5:
            c_tech, c_contact = st.columns(2)
            with c_tech:
                st.markdown("#### 📱 Kỹ thuật")
                st.write(f"📅 **Released:** {d.get('released')}")
                st.write(f"🔄 **Updated:** {d.get('updated')}")
                st.write(f"🏷️ **Version:** {d.get('version')}")
                st.write(f"💾 **Size:** {d.get('size')}")
                st.write(f"🤖 **Android:** {d.get('androidVersion')}")
                st.write(f"💰 **IAP:** {d.get('IAPRange')}")

            with c_contact:
                st.markdown("#### 📬 Liên hệ")
                st.write(f"🆔 **Dev ID:** {d.get('developerId')}")
                if d.get('developerEmail'): st.write(f"📧 **Email:** {d.get('developerEmail')}")
                if d.get('developerWebsite'): st.write(f"🌐 **Website:** [Link]({d.get('developerWebsite')})")
                if d.get('developerAddress'): st.write(f"🏢 **Address:** {d.get('developerAddress')}")
                if d.get('privacyPolicy'): st.write(f"🔒 **Privacy Policy:** [Link]({d.get('privacyPolicy')})")

            st.markdown("---")
            st.markdown("#### 🛡️ Quyền truy cập")
            perms = d.get('permissions', [])
            if perms:
                for p in perms:
                    perm_text = p.get('permission') if isinstance(p, dict) else str(p)
                    st.markdown(f"<span class='perm-tag'>{perm_text}</span>", unsafe_allow_html=True)
            else: st.info("App này không yêu cầu quyền đặc biệt.")

            st.markdown("---")
            if d.get('recentChanges'):
                st.markdown("#### 🆕 Có gì mới")
                st.info(d.get('recentChanges'))

            st.markdown("#### 📝 Mô tả")
            with st.expander("Xem toàn bộ", expanded=True):
                st.markdown(d.get('descriptionHTML', ''), unsafe_allow_html=True)
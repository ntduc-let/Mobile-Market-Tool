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

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mobile Market Analyzer", layout="wide", page_icon="📱")
DB_PATH = 'data/market_data.db'
NODE_SCRIPT = 'scraper.js'

# --- 2. [QUAN TRỌNG] TỰ ĐỘNG CÀI ĐẶT NODE.JS ---
def init_environment():
    # Tạo thư mục data
    if not os.path.exists('data'):
        os.makedirs('data')

    # File lock đánh dấu phiên bản v10
    install_flag = "install_v10_final.lock"

    if not os.path.exists(install_flag):
        st.toast("♻️ Đang khởi tạo hệ thống...", icon="🚀")
        
        # Xóa bản cũ để tránh xung đột
        if os.path.exists('node_modules'):
            try: shutil.rmtree('node_modules', ignore_errors=True)
            except: pass
        if os.path.exists('package-lock.json'):
            try: os.remove('package-lock.json')
            except: pass

        try:
            # Cài đặt thư viện npm
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
            
            # Đánh dấu thành công
            with open(install_flag, 'w') as f:
                f.write("ok")
            
            st.toast("✅ Cài đặt xong! App đang khởi động...", icon="🎉")
            time.sleep(1)
            st.rerun()
        except subprocess.CalledProcessError:
            st.error("❌ Lỗi cài đặt Node.js. Vui lòng kiểm tra file package.json")
            st.stop()

# Chạy khởi tạo ngay đầu file
init_environment()

# --- 3. DANH SÁCH HẰNG SỐ (FULL) ---
CATEGORIES_LIST = {
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

COUNTRIES_LIST = {
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
    "🇺🇸 Hoa Kỳ (USA)": "us",
    "🇨🇦 Canada": "ca",
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
    "🇦🇺 Úc (Australia)": "au",
    "🇳🇿 New Zealand": "nz",
    "🇧🇷 Brazil": "br",
    "🇲🇽 Mexico": "mx",
    "🇦🇷 Argentina": "ar",
    "🇨🇱 Chile": "cl",
    "🇨🇴 Colombia": "co",
    "🇵🇪 Peru": "pe",
    "🇸🇦 Ả Rập Xê Út (Saudi Arabia)": "sa",
    "🇦🇪 UAE (Các Tiểu vương quốc Ả Rập)": "ae",
    "🇮🇱 Israel": "il",
    "🇪🇬 Ai Cập (Egypt)": "eg",
    "🇿🇦 Nam Phi (South Africa)": "za",
    "🇳🇬 Nigeria": "ng"
}

# --- 4. STATE MANAGEMENT ---
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

# --- 5. CSS (GIAO DIỆN) ---
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

    /* --- Giao diện Detail MỚI --- */
    .hero-header {
        position: relative; overflow: hidden; /* Cập nhật để hỗ trợ ảnh nền */
        display: flex; gap: 25px; padding: 30px;
        background: linear-gradient(180deg, rgba(30,32,40,0.85) 0%, rgba(30,32,40,1) 100%);
        border-radius: 20px; border: 1px solid #3a3f4b;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4); margin-bottom: 25px;
        align-items: center;
        z-index: 1;
    }
    /* Lớp hiển thị ảnh nền Header */
    .hero-bg {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-size: cover; background-position: center; opacity: 0.2; z-index: -1; filter: blur(10px);
    }
    .hero-icon-big { width: 120px; height: 120px; border-radius: 24px; border: 2px solid #444; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 2; }
    .hero-title-text { font-size: 2.5em; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
    .metric-card-custom {
        background: #23252e; padding: 20px 15px; border-radius: 16px; text-align: center;
        border: 1px solid #333; transition: transform 0.2s;
    }
    
    /* Lớp hiển thị Screenshots (MỚI) */
    .screenshot-container { overflow-x: auto; white-space: nowrap; padding-bottom: 15px; scrollbar-width: thin; }
    .screenshot-img { height: 350px; border-radius: 12px; margin-right: 12px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 1px solid #444; }

    /* Lớp hiển thị Data Safety (MỚI) */
    .safety-item { 
        background: #252730; padding: 12px; margin-bottom: 8px; border-radius: 8px; 
        border-left: 3px solid #64b5f6; font-size: 0.95em;
    }

    .review-card-modern { background-color: #2a2d3a; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #ffbd45; }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; margin-right: 6px; border: 1px solid rgba(255,255,255,0.1); display: inline-block;}
    .badge-ad { background-color: rgba(230, 81, 0, 0.2); color: #ff9800; }
    .badge-iap { background-color: rgba(27, 94, 32, 0.2); color: #4caf50; }
            
    /* --- CSS CHO SCREENSHOTS (MỚI: CÓ ZOOM) --- */
    .screenshot-container { 
        overflow-x: auto; 
        white-space: nowrap; 
        padding-bottom: 15px; 
        scrollbar-width: thin; 
    }
    
    .screenshot-img { 
        height: 350px; 
        border-radius: 12px; 
        margin-right: 12px; 
        display: inline-block; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
        border: 1px solid #444; 
        transition: transform 0.3s ease;
        cursor: zoom-in; /* Con trỏ hình kính lúp */
    }

    /* Hiệu ứng Lightbox khi click (focus) vào ảnh */
    .screenshot-img:focus {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90vw;
        height: 90vh;
        object-fit: contain;
        z-index: 9999;
        background-color: rgba(0,0,0,0.95);
        border-radius: 4px;
        box-shadow: 0 0 50px rgba(0,0,0,0.8);
        cursor: zoom-out;
        outline: none;
        
        /* [QUAN TRỌNG] Dòng này giúp click vào ảnh sẽ tắt ảnh đi */
        /* Lý do: Nó làm chuột click "xuyên qua" ảnh trúng vào nền web, gây mất focus */
        pointer-events: none; 
    }
    * 1. Ẩn ô checkbox (chỉ dùng để lưu trạng thái đóng/mở) */
    .lightbox-toggle { display: none; }

    /* 2. Khung cuộn ngang chứa danh sách ảnh */
    .screenshot-scroll { 
        overflow-x: auto; 
        white-space: nowrap; 
        padding-bottom: 10px;
        scrollbar-width: thin;
    }

    /* 3. Style cho ảnh THUMBNAIL (Ảnh nhỏ hiển thị trên web) */
    .thumb-label {
        display: inline-block;
        margin-right: 12px;
        cursor: zoom-in;
        transition: transform 0.2s;
        border: 1px solid #444;
        border-radius: 8px;
    }
    .thumb-label:hover { transform: scale(1.02); border-color: #64b5f6; }
    
    .thumb-img {
        height: 200px; /* Chiều cao cố định */
        width: auto;
        display: block;
        border-radius: 8px;
    }

    /* 4. Màn hình đen phủ kín (OVERLAY) - Mặc định ẩn */
    .lightbox-overlay {
        display: none; /* Ẩn */
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: rgba(0, 0, 0, 0.95); /* Nền đen 95% */
        z-index: 999999; /* Luôn nằm trên cùng */
        justify-content: center;
        align-items: center;
        cursor: zoom-out;
        backdrop-filter: blur(5px);
    }

    /* 5. LOGIC KÍCH HOẠT: Khi checkbox được chọn -> Hiện Overlay */
    .lightbox-toggle:checked ~ .lightbox-overlay {
        display: flex;
        animation: fadeIn 0.2s ease-out;
    }

    /* 6. Ảnh phóng to bên trong */
    .full-img {
        max-width: 95%;
        max-height: 95%;
        object-fit: contain;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)
# --- 6. BACKEND FUNCTIONS ---
def run_node_safe(mode, target, country, output_file, token=None):
    file_path = f"data/{output_file}"
    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass
    try:
        args = ["node", NODE_SCRIPT, mode, target, country]
        if token: args.append(token)
        subprocess.run(args, capture_output=True, text=True, check=True, timeout=90)
    except subprocess.CalledProcessError as e:
        return None
    except Exception: return None

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

def save_data_to_db(category_id, country_code):
    if not os.path.exists("data/raw_data.json"): return False
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
            i.get('appId') or i.get('app_id'), # Fallback ID
            i.get('title'), i.get('developer'), i.get('score', 0), 
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

# --- 7. UI COMPONENTS ---
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

# --- 8. SIDEBAR ---
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
            subprocess.run(["node", NODE_SCRIPT, "LIST", target_cat, target_country], check=True, timeout=120)
            if save_data_to_db(target_cat, target_country):
                st.session_state.view_mode = 'list'
                st.rerun()
            else: st.error("Không lưu được DB.")
        except subprocess.TimeoutExpired:
             st.error("Timeout! Quá trình quét mất quá nhiều thời gian.")
        except Exception as e: 
             st.error(f"Lỗi: {e}")

# --- 9. MAIN VIEW ---

# A. LIST VIEW
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

# B. SEARCH RESULTS
elif st.session_state.view_mode == 'search_results':
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))
    st.title("🔎 Kết quả tìm kiếm")
    results = st.session_state.search_results
    if results:
        cols = st.columns(3)
        for i, app in enumerate(results):
            with cols[i % 3]: render_mini_card(app, COUNTRIES_LIST[search_country_label], i, "sr")
    else: st.warning("Không tìm thấy kết quả nào.")

# C. DETAIL VIEW
elif st.session_state.view_mode == 'detail' and st.session_state.selected_app:
    app = st.session_state.selected_app
    curr_country = app.get('country_override', target_country)
    target_id = app['app_id']

    st.button("⬅️ Quay lại danh sách", on_click=lambda: st.session_state.update(view_mode='list'), use_container_width=False)

    # Logic tải data
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
                st.session_state.detail_country = curr_country
                
                # Gọi async các API phụ (Similar/Dev)
                run_node_safe("SIMILAR", target_id, curr_country, "similar_apps.json")
                if d.get('developerId'):
                    run_node_safe("DEVELOPER", str(d.get('developerId')), curr_country, "developer_apps.json")

    # Render Detail UI
    d = st.session_state.detail_data
    
    # Load lại data phụ từ file (nếu có)
    if os.path.exists("data/similar_apps.json"):
        try:
            with open("data/similar_apps.json", "r") as f: st.session_state.similar_apps = json.load(f)
        except: pass
    if os.path.exists("data/developer_apps.json"):
        try:
            with open("data/developer_apps.json", "r") as f: st.session_state.dev_apps = json.load(f)
        except: pass

    if d:
        # --- 1. HEADER (MỚI: Có ảnh nền & Sắp xếp lại) ---
        # Lấy ảnh bìa làm nền, nếu không có thì dùng icon
        bg_url = d.get('headerImage') or d.get('icon')
        
        # Badges
        badges = ""
        if d.get('adSupported'): badges += "<span class='badge badge-ad'>Ads</span>"
        if d.get('offersIAP'): badges += "<span class='badge badge-iap'>IAP</span>"
        badges += f"<span class='badge' style='background:rgba(255,255,255,0.1)'>{d.get('version')}</span>"

        st.markdown(f"""
        <div class="hero-header">
            <div class="hero-bg" style="background-image: url('{bg_url}');"></div>
            <img src="{d.get('icon')}" class="hero-icon-big">
            <div style="z-index: 2; color: white;">
                <h1 class="hero-title-text">{d.get('title')}</h1>
                <div style="color: #64b5f6; margin-bottom: 10px; font-size: 1.1em;">by {d.get('developer')}</div>
                <div style="margin-bottom: 5px;">{badges}</div>
                <div style="font-family: monospace; color: #aaa; font-size: 0.9em;">ID: {d.get('appId')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- 2. METRICS GRID ---
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card-custom">
                <h3>⭐ {d.get('score', 0):.1f}</h3><small>RATING</small>
            </div>
            <div class="metric-card-custom">
                <h3>💬 {d.get('ratings', 0):,}</h3><small>REVIEWS</small>
            </div>
            <div class="metric-card-custom">
                <h3>📥 {d.get('installs', 'N/A')}</h3><small>INSTALLS</small>
            </div>
            <div class="metric-card-custom">
                <h3>📅 {d.get('updated', 'N/A')}</h3><small>UPDATED</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- 3. TABS (MỚI: Thêm Media & Data Safety) ---
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Reviews", "📸 Media", "🛡️ Data Safety", "⚔️ Đối thủ", "🏢 Cùng Dev", "ℹ️ Info"
        ])

        # TAB 1: REVIEWS (Giữ nguyên hoặc cập nhật logic hiển thị review của bạn)
        with tab1:
            # Chia cột: Bên trái là Bộ lọc & Thống kê, Bên phải là Biểu đồ
            c_dashboard, c_chart = st.columns([2, 3])
            
            with c_dashboard:
                st.subheader("🔍 Bộ lọc & Thống kê")
                
                # 1. Bộ lọc Review
                filter_option = st.selectbox(
                    "Hiển thị đánh giá:",
                    ["Tất cả", "Tích cực (4-5 ⭐)", "Trung bình (3 ⭐)", "Tiêu cực (1-2 ⭐)"],
                    key="rev_filter"
                )
                
                # Logic lọc danh sách review hiện có
                all_revs = st.session_state.current_reviews
                if filter_option == "Tích cực (4-5 ⭐)":
                    filtered_revs = [r for r in all_revs if r.get('score', 0) >= 4]
                elif filter_option == "Trung bình (3 ⭐)":
                    filtered_revs = [r for r in all_revs if r.get('score', 0) == 3]
                elif filter_option == "Tiêu cực (1-2 ⭐)":
                    filtered_revs = [r for r in all_revs if r.get('score', 0) <= 2]
                else:
                    filtered_revs = all_revs

                st.caption(f"Đang hiển thị: **{len(filtered_revs)}** / {len(all_revs)} đánh giá đã tải.")
                
            with c_chart:
                # 2. Biểu đồ Histogram (Phân bố sao)
                hist = d.get('histogram')
                if hist:
                    try:
                        # Chuyển đổi dữ liệu histogram thành DataFrame cho Plotly
                        # Google trả về keys dạng string "1", "2"...
                        data_hist = {
                            'Star': ['1', '2', '3', '4', '5'],
                            'Count': [
                                hist.get('1', 0), hist.get('2', 0), hist.get('3', 0), 
                                hist.get('4', 0), hist.get('5', 0)
                            ]
                        }
                        df_hist = pd.DataFrame(data_hist)
                        
                        # Vẽ biểu đồ cột ngang hoặc dọc
                        fig = px.bar(
                            df_hist, x='Star', y='Count', 
                            text='Count',
                            color='Star',
                            # Màu sắc từ Đỏ (1 sao) -> Xanh (5 sao)
                            color_discrete_map={
                                '1': '#ff4b4b', '2': '#ff8c00', '3': '#f1c40f', 
                                '4': '#9acd32', '5': '#4caf50'
                            }
                        )
                        
                        # Tinh chỉnh giao diện biểu đồ cho gọn
                        fig.update_layout(
                            height=220, 
                            margin=dict(t=10, b=10, l=10, r=10),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False,
                            xaxis_title=None,
                            yaxis_title=None,
                            yaxis={'showgrid': False, 'visible': False}, # Ẩn trục Y cho gọn
                            font=dict(color='#fff')
                        )
                        # Hiển thị số lượng trên cột
                        fig.update_traces(textposition='outside')
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    except Exception as e:
                        st.warning("Không thể vẽ biểu đồ phân bố.")
                else:
                    st.info("App này chưa có dữ liệu phân bố sao.")

            st.divider()

            # 3. Danh sách Review (Render danh sách đã lọc)
            if filtered_revs:
                for r in filtered_revs:
                    # Xử lý an toàn cho trường hợp thiếu key
                    user_name = r.get('userName', 'Người dùng ẩn')
                    date_post = r.get('date', '')
                    content = r.get('text', '')
                    score = int(r.get('score', 0))
                    
                    st.markdown(f"""
                    <div class="review-card-modern">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{user_name}</b>
                            <span style="color:#888; font-size:0.9em">{date_post}</span>
                        </div>
                        <div style="color:#ffbd45; margin: 4px 0;">{'⭐' * score}</div>
                        <div style="font-style: italic; color: #ddd; line-height:1.4;">"{content}"</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Không tìm thấy đánh giá nào phù hợp với bộ lọc này.")

            # 4. Nút tải thêm (Luôn hiển thị ở dưới cùng nếu còn token)
            if st.session_state.next_token:
                st.markdown("---")
                if st.button("⬇️ Tải thêm review cũ hơn từ Google Play", use_container_width=True):
                    with st.spinner("Đang kết nối tới Google..."):
                        more = run_node_safe(
                            "MORE_REVIEWS", d['appId'], curr_country, 
                            "more_reviews.json", st.session_state.next_token
                        )
                        
                        if more:
                            if more.get('error'):
                                st.error(f"Lỗi: {more.get('error')}")
                                if "token" in str(more.get('error')).lower():
                                    st.session_state.next_token = None # Token hết hạn thì xóa đi
                            else:
                                new_comments = more.get('comments', [])
                                if new_comments:
                                    st.session_state.current_reviews.extend(new_comments)
                                    st.session_state.next_token = more.get('nextToken')
                                    st.success(f"Đã tải thêm {len(new_comments)} đánh giá!")
                                    time.sleep(1) # Delay nhẹ để người dùng thấy thông báo
                                    st.rerun()
                                else:
                                    st.warning("Không còn review nào cũ hơn.")
                                    st.session_state.next_token = None
                                    st.rerun()
                        else: 
                            st.error("Không phản hồi từ Server.")

        # --- TAB 2: MEDIA (FIX LỖI HIỂN THỊ CODE HTML) ---
        with tab2:
            # 1. Video
            if d.get('video'):
                st.subheader("🎥 Video Trailer")
                st.video(d.get('video'))
                st.divider()
            
            # 2. Screenshots (Đã fix lỗi hiển thị text)
            if d.get('screenshots'):
                st.subheader("🖼️ Screenshots")
                st.caption("💡 Click ảnh để phóng to. Click vùng đen để đóng.")

                # Chuẩn bị HTML - Viết liền 1 dòng hoặc dùng textwrap để tránh lỗi Markdown hiểu nhầm là Code Block
                html_content = '<div class="screenshot-scroll">'
                
                base_id = d.get('appId', 'app').replace('.', '_')
                
                for i, url in enumerate(d.get('screenshots')):
                    unique_id = f"img_{base_id}_{i}"
                    
                    # QUAN TRỌNG: F-string được viết sát lề trái để tránh khoảng trắng thừa
                    html_content += f"""<div style="display:inline-block; margin-right:10px;">
                                        <input type="checkbox" id="{unique_id}" class="lightbox-toggle">
                                        <label for="{unique_id}" class="thumb-label">
                                        <img src="{url}" class="thumb-img" loading="lazy">
                                        </label>
                                        <label for="{unique_id}" class="lightbox-overlay">
                                        <img src="{url}" class="full-img">
                                        </label>
                                        </div>
                                    """
                
                html_content += '</div>'
                
                # QUAN TRỌNG NHẤT: Phải có unsafe_allow_html=True
                st.markdown(html_content, unsafe_allow_html=True)
            else: 
                st.info("Không có ảnh chụp màn hình.")

        # TAB 3: DATA SAFETY (HOÀN TOÀN MỚI)
        with tab3:
            ds = d.get('dataSafety', {})
            if ds:
                c_shared, c_collected = st.columns(2)
                with c_shared:
                    st.markdown("#### 📤 Dữ liệu chia sẻ (Shared)")
                    if ds.get('sharedData'):
                        for item in ds.get('sharedData'):
                            st.markdown(f"<div class='safety-item'><b>{item.get('data')}</b><br><small style='color:#ccc'>{item.get('purpose')}</small></div>", unsafe_allow_html=True)
                    else: st.success("✅ Không chia sẻ dữ liệu với bên thứ ba.")
                
                with c_collected:
                    st.markdown("#### 📥 Dữ liệu thu thập (Collected)")
                    if ds.get('collectedData'):
                        for item in ds.get('collectedData'):
                             st.markdown(f"<div class='safety-item'><b>{item.get('data')}</b><br><small style='color:#ccc'>{item.get('purpose')}</small></div>", unsafe_allow_html=True)
                    else: st.success("✅ Không thu thập dữ liệu người dùng.")
            else: st.info("Nhà phát triển không cung cấp thông tin an toàn dữ liệu.")

        # --- TAB 4: ĐỐI THỦ (FULL LIST - ĐÃ LỌC TRÙNG) ---
        with tab4:
            current_id = d.get('appId')
            current_dev = d.get('developer', '').lower().strip()
            country_code = st.session_state.selected_app.get('country_override', 'vn')

            # Logic lọc: Bỏ chính nó và bỏ app cùng nhà
            real_competitors = []
            if st.session_state.similar_apps:
                for s in st.session_state.similar_apps:
                    s_dev = s.get('developer', '').lower().strip()
                    if s.get('appId') != current_id and current_dev not in s_dev:
                        real_competitors.append(s)

            if real_competitors:
                # [UPDATE] Hiển thị full danh sách tìm được
                st.caption(f"🎯 Đã lọc bỏ các ứng dụng cùng nhà phát hành. Hiển thị toàn bộ **{len(real_competitors)}** đối thủ.")
                
                cols = st.columns(3)
                # Đã bỏ [:9] -> Vòng lặp chạy hết danh sách
                for i, s in enumerate(real_competitors):
                    with cols[i % 3]:
                        render_mini_card(s, country_code, i, "sim")
            else:
                st.info("⚠️ Không tìm thấy đối thủ cạnh tranh trực tiếp (hoặc Google chỉ gợi ý app cùng nhà).")

        # --- TAB 5: CÙNG DEV (FULL LIST - ĐÃ LỌC RÁC) ---
        with tab5:
            current_id = d.get('appId')
            current_dev_name = d.get('developer', '').lower()
            country_code = st.session_state.selected_app.get('country_override', 'vn')
            
            clean_devs = []
            if st.session_state.dev_apps:
                for dv in st.session_state.dev_apps:
                    if dv.get('appId') == current_id: continue
                    
                    dv_name = dv.get('developer', '').lower()
                    if current_dev_name in dv_name or dv_name in current_dev_name:
                        clean_devs.append(dv)

            if clean_devs:
                # [UPDATE] Hiển thị full danh sách tìm được
                st.success(f"📂 Tìm thấy và hiển thị toàn bộ **{len(clean_devs)}** ứng dụng khác của cùng nhà phát triển.")
                
                cols = st.columns(3)
                # Đã bỏ [:9] và logic display_count -> Vòng lặp chạy hết danh sách
                for i, dv in enumerate(clean_devs): 
                    with cols[i % 3]:
                        render_mini_card(dv, country_code, i, "dev")
            else:
                st.warning(f"Không tìm thấy ứng dụng nào khác của '{d.get('developer')}'.")

        # --- TAB 6: INFO (ĐÃ NÂNG CẤP: ĐẦY ĐỦ THÔNG SỐ) ---
        with tab6:
            # 1. Nhóm thông tin Kỹ thuật & Phân loại
            c_tech, c_cat = st.columns(2)
            
            with c_tech:
                st.markdown("#### 📱 Kỹ thuật")
                st.write(f"**📦 ID:** `{d.get('appId')}`")
                st.write(f"**🏷️ Version:** {d.get('version', 'Varies with device')}")
                st.write(f"**💾 Size:** {d.get('size', 'Varies with device')}")
                st.write(f"**🤖 Android:** {d.get('androidVersion', 'Varies')}")
            
            with c_cat:
                st.markdown("#### 🏷️ Phân loại")
                st.write(f"**📂 Genre:** {d.get('genre')}")
                st.write(f"**🔞 Content Rating:** {d.get('contentRating')}")
                st.write(f"**📅 Released:** {d.get('released')}")
                st.write(f"**🔄 Updated:** {d.get('updated')}")

            st.divider()

            # 2. Nhóm thông tin "Có gì mới" (Rất quan trọng để theo dõi update)
            if d.get('recentChanges'):
                st.markdown("#### 🆕 Có gì mới trong phiên bản này")
                st.info(d.get('recentChanges'))
                st.divider()

            # 3. Nhóm liên hệ Developer
            st.markdown("#### 📬 Liên hệ Nhà phát triển")
            c_contact1, c_contact2 = st.columns(2)
            
            with c_contact1:
                if d.get('developerEmail'): 
                    st.write(f"📧 **Email:** {d.get('developerEmail')}")
                if d.get('developerWebsite'): 
                    st.write(f"🌐 **Website:** [Truy cập]({d.get('developerWebsite')})")
            
            with c_contact2:
                if d.get('privacyPolicy'): 
                    st.write(f"🔒 **Privacy Policy:** [Xem chính sách]({d.get('privacyPolicy')})")
                if d.get('developerAddress'): 
                    st.write(f"🏢 **Address:** {d.get('developerAddress')}")

            st.divider()

            # 4. Mô tả chi tiết (HTML)
            st.markdown("#### 📝 Mô tả ứng dụng")
            # Dùng Expander để nội dung không bị quá dài nếu mô tả nhiều
            with st.expander("Xem toàn bộ nội dung mô tả", expanded=True):
                st.markdown(d.get('descriptionHTML', 'Chưa có mô tả.'), unsafe_allow_html=True)
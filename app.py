import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import os
import json
import datetime
import plotly.graph_objects as go
import plotly.express as px
import time
import shutil

# --- 1. CẤU HÌNH TRANG (PHẢI ĐỂ ĐẦU TIÊN) ---
st.set_page_config(page_title="Mobile Market Tool", layout="wide", page_icon="📱")

# --- 2. HẰNG SỐ ---
DB_PATH = 'data/market_data.db'
NODE_SCRIPT = 'scraper.js'

# --- 3. [QUAN TRỌNG] HÀM KHỞI TẠO & CÀI ĐẶT MÔI TRƯỜNG ---
def init_environment():
    """
    Hàm này chạy ngay khi app khởi động.
    Nó kiểm tra xem thư viện Node.js đã được cài đúng phiên bản chưa.
    Nếu chưa (dựa vào file lock), nó sẽ xóa bản cũ và cài lại bản mới.
    """
    
    # Tạo thư mục data nếu chưa có
    if not os.path.exists('data'):
        os.makedirs('data')

    # Tên file khóa để đánh dấu phiên bản hiện tại (v10 + Polyfill)
    # Nếu bạn đổi code Node.js/package.json, hãy đổi tên file này để ép app cài lại.
    install_flag = "install_v10_polyfill_final.lock"

    if not os.path.exists(install_flag):
        st.toast("♻️ Phát hiện cấu hình mới. Đang cập nhật hệ thống...", icon="🚀")
        
        container = st.empty()
        container.info("🧹 Đang dọn dẹp thư viện cũ (Clean up)...")
        
        # 1. Xóa node_modules cũ (để tránh xung đột version)
        if os.path.exists('node_modules'):
            try: shutil.rmtree('node_modules', ignore_errors=True)
            except: pass
            
        # 2. Xóa package-lock.json cũ
        if os.path.exists('package-lock.json'):
            try: os.remove('package-lock.json')
            except: pass

        container.info("📦 Đang cài đặt thư viện Node.js v10 (npm install)...")
        
        try:
            # 3. Chạy lệnh cài đặt
            # capture_output=True để ẩn log bớt, check=True để báo lỗi nếu thất bại
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
            
            # 4. Tạo file lock đánh dấu thành công
            with open(install_flag, 'w') as f:
                f.write("installed_ok")
                
            container.success("✅ Cài đặt thành công! App đang khởi động lại...")
            time.sleep(1)
            st.rerun() # Reload lại trang
            
        except subprocess.CalledProcessError as e:
            container.error("❌ Lỗi cài đặt Node.js. Vui lòng kiểm tra file package.json")
            st.error(f"Chi tiết lỗi: {e}")
            st.stop()

# Gọi hàm khởi tạo ngay lập tức
init_environment()


# --- 4. CÁC HÀM BACKEND (PYTHON GỌI NODE.JS) ---

def run_node_safe(mode, target, country, output_file, token=None):
    """Gọi script scraper.js an toàn, có bắt lỗi"""
    file_path = f"data/{output_file}"
    
    # Xóa file kết quả cũ để không đọc nhầm data rác
    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass
        
    try:
        # Xây dựng câu lệnh: node scraper.js MODE TARGET COUNTRY [TOKEN]
        args = ["node", NODE_SCRIPT, mode, target, country]
        if token: args.append(token)
        
        # Gọi subprocess
        # timeout=60s để tránh treo app nếu mạng lag
        subprocess.run(args, capture_output=True, text=True, check=True, timeout=60)
        
    except subprocess.CalledProcessError as e:
        # Node script trả về lỗi (exit code != 0)
        print(f"❌ Node Logic Error: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        st.error("⚠️ Quá trình lấy dữ liệu tốn quá nhiều thời gian (Timeout).")
        return None
    except Exception as e:
        print(f"❌ System Error: {e}")
        return None

    # Đọc file JSON kết quả trả về
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

def save_data_to_db(category_id, country_code):
    """Lưu dữ liệu từ raw_data.json vào SQLite"""
    json_path = "data/raw_data.json"
    if not os.path.exists(json_path): return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except: return False
    
    if not data: return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tạo bảng nếu chưa có
    cursor.execute('''CREATE TABLE IF NOT EXISTS app_history (
            scraped_at TIMESTAMP, category TEXT, country TEXT, collection_type TEXT,
            rank INT, app_id TEXT, title TEXT, developer TEXT, score REAL,
            installs TEXT, price REAL, currency TEXT, icon TEXT, reviews INT)''')
    
    # Xóa dữ liệu cũ của ngày hôm nay (để tránh trùng lặp khi quét lại)
    today = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
    cursor.execute("DELETE FROM app_history WHERE category=? AND country=? AND scraped_at>=?", (category_id, country_code, today))
    
    # Chuẩn bị dữ liệu insert
    clean_rows = []
    ts = datetime.datetime.now()
    
    for i in data:
        clean_rows.append((
            ts, 
            i.get('category'), 
            i.get('country'), 
            i.get('collection_type'), 
            i.get('rank'), 
            i.get('appId') or i.get('app_id'), # Fallback key
            i.get('title'), 
            i.get('developer'), 
            i.get('score', 0), 
            i.get('installs', 'N/A'), 
            i.get('price', 0), 
            'VND', 
            i.get('icon', ''), 
            0
        ))
    
    cursor.executemany('INSERT INTO app_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', clean_rows)
    conn.commit()
    conn.close()
    return True

def load_data_today(cat, country):
    """Lấy dữ liệu chart của ngày hôm nay từ DB"""
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # Lấy data theo ngày
        query = f"SELECT * FROM app_history WHERE category='{cat}' AND country='{country}' AND strftime('%Y-%m-%d', scraped_at)='{today}'"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except: 
        conn.close()
        return pd.DataFrame()

def load_app_history(app_id, country):
    """Lấy lịch sử thứ hạng của 1 app"""
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"SELECT scraped_at, rank, collection_type FROM app_history WHERE app_id='{app_id}' AND country='{country}' ORDER BY scraped_at ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except: 
        conn.close()
        return pd.DataFrame()

# --- 5. GIAO DIỆN (CSS & RENDERER) ---

st.markdown("""
<style>
    /* Card Style */
    .app-card-modern {
        background: linear-gradient(145deg, #1e2028, #23252e);
        border-radius: 16px; padding: 16px; margin-bottom: 16px;
        border: 1px solid #2c303a; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .app-card-modern:hover { transform: translateY(-3px); border-color: #64b5f6; }
    .card-content-flex { display: flex; align-items: flex-start; gap: 15px; }
    .rank-number { font-size: 1.4em; font-weight: 900; color: #64b5f6; min-width: 30px; }
    .app-icon-img { width: 72px; height: 72px; border-radius: 14px; object-fit: cover; border: 1px solid #333; }
    .app-info-box { flex-grow: 1; overflow: hidden; }
    .app-title-modern { font-size: 1.15em; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
    .app-publisher-modern { font-size: 0.9em; color: #b0b3b8; }
    .metric-score { color: #ffbd45; font-weight: 700; font-size: 0.95em; margin-top: 5px;}
    
    /* Detail Header */
    .hero-header { display: flex; gap: 25px; padding: 25px; background: linear-gradient(135deg, #2a2d3a 0%, #1e2028 100%); border-radius: 20px; border: 1px solid #3a3f4b; margin-bottom: 25px; align-items: center; }
    .hero-icon-big { width: 120px; height: 120px; border-radius: 20px; border: 2px solid #444; }
    .hero-title-text { font-size: 2.2em; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }
    .hero-dev-text { color: #64b5f6; font-size: 1.1em; margin-bottom: 8px; }
    
    /* Metrics Grid */
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
    .metric-card-custom { background: #23252e; padding: 20px 15px; border-radius: 16px; text-align: center; border: 1px solid #333; }
    .metric-val { font-size: 1.5em; font-weight: bold; color: white; display: block; }
    .metric-lbl { font-size: 0.85em; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }

    /* Review Card */
    .review-card-modern { background-color: #2a2d3a; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #ffbd45; }
    
    /* Button Fix */
    div.stButton > button { width: 100%; border-radius: 10px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def render_mini_card(app, country, rank_idx, key_prefix):
    """Vẽ thẻ ứng dụng nhỏ (dùng cho List và Search result)"""
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/72?text=App'
    title = app.get('title', 'Unknown Title')
    publisher = app.get('developer', 'Unknown Dev')
    score = app.get('score', 0)
    rank = rank_idx + 1
    
    # Lấy ID an toàn
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
    
    # HTML Card
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
    
    # Button Action
    if st.button("🔍 Chi tiết", key=unique_key):
        st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()

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

# --- 7. QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
if 'selected_app' not in st.session_state: st.session_state.selected_app = None
if 'search_results' not in st.session_state: st.session_state.search_results = []
if 'detail_data' not in st.session_state: st.session_state.detail_data = None
if 'detail_id' not in st.session_state: st.session_state.detail_id = None
if 'detail_country' not in st.session_state: st.session_state.detail_country = None

# --- 8. SIDEBAR (THANH ĐIỀU HƯỚNG) ---
st.sidebar.title("🚀 Mobile Market Tool")

# Khu vực tìm kiếm
st.sidebar.subheader("🔍 Tìm kiếm")
search_term = st.sidebar.text_input("Từ khóa / App ID:")
search_country_label = st.sidebar.selectbox("Quốc gia tìm", list(COUNTRIES_LIST.keys()), index=0)

if st.sidebar.button("🔎 Tìm ngay", type="secondary"):
    if search_term:
        s_country = COUNTRIES_LIST[search_country_label]
        with st.spinner(f"Đang tìm '{search_term}' tại {s_country}..."):
            res = run_node_safe("SEARCH", search_term, s_country, "search_results.json")
            if res:
                st.session_state.search_results = res
                st.session_state.view_mode = 'search_results'
                st.rerun()
            else:
                st.error("Không tìm thấy kết quả nào.")

st.sidebar.markdown("---")

# Khu vực Top Charts
st.sidebar.subheader("📊 Top Charts")
sel_country_lbl = st.sidebar.selectbox("Quốc Gia", list(COUNTRIES_LIST.keys()))
sel_cat_lbl = st.sidebar.selectbox("Thể Loại", list(CATEGORIES_LIST.keys()))
target_country = COUNTRIES_LIST[sel_country_lbl]
target_cat = CATEGORIES_LIST[sel_cat_lbl]

if st.sidebar.button("🚀 Quét Chart", type="primary"):
    with st.status("Đang xử lý dữ liệu...", expanded=True) as status:
        st.write("📡 Đang gọi Scraper (v10)...")
        
        # Bước 1: Gọi Scraper lấy List
        # Gọi subprocess trực tiếp ở đây để bắt lỗi rõ hơn nếu cần
        try:
            subprocess.run(
                ["node", NODE_SCRIPT, "LIST", target_cat, target_country], 
                check=True, capture_output=True, text=True, timeout=90
            )
            st.write("💾 Đang lưu vào Database...")
            
            # Bước 2: Lưu DB
            if save_data_to_db(target_cat, target_country):
                status.update(label="✅ Hoàn tất!", state="complete", expanded=False)
                st.session_state.view_mode = 'list'
                st.rerun()
            else:
                status.update(label="⚠️ Lỗi lưu Database", state="error")
                st.error("Không đọc được file raw_data.json trả về.")
                
        except subprocess.CalledProcessError as e:
            status.update(label="❌ Lỗi Node.js Scraper", state="error")
            st.error("Scraper bị lỗi. Chi tiết:")
            st.code(e.stderr)
        except subprocess.TimeoutExpired:
            status.update(label="⏰ Timeout", state="error")
            st.error("Quá trình quét mất quá nhiều thời gian.")

# --- 9. MÀN HÌNH CHÍNH (MAIN CONTENT) ---

# === VIEW 1: TOP CHARTS ===
if st.session_state.view_mode == 'list':
    st.title(f"📊 Market: {sel_cat_lbl} ({target_country.upper()})")
    
    # Load data
    df = load_data_today(target_cat, target_country)
    
    if not df.empty:
        tab_names = ["🔥 Top Free", "💸 Top Paid", "💰 Grossing"]
        # Lọc data cho từng loại
        free_apps = df[df['collection_type']=='top_free'].sort_values('rank')
        paid_apps = df[df['collection_type']=='top_paid'].sort_values('rank')
        gross_apps = df[df['collection_type']=='top_grossing'].sort_values('rank')
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.subheader("🔥 Top Free")
            if not free_apps.empty:
                for i, (_, r) in enumerate(free_apps.head(20).iterrows()):
                    render_mini_card(r, target_country, i, "tf")
            else: st.info("Không có dữ liệu.")
            
        with c2:
            st.subheader("💸 Top Paid")
            if not paid_apps.empty:
                for i, (_, r) in enumerate(paid_apps.head(20).iterrows()):
                    render_mini_card(r, target_country, i, "tp")
            else: st.info("Không có dữ liệu.")

        with c3:
            st.subheader("💰 Grossing")
            if not gross_apps.empty:
                for i, (_, r) in enumerate(gross_apps.head(20).iterrows()):
                    render_mini_card(r, target_country, i, "tg")
            else: st.info("Không có dữ liệu.")
            
    else:
        st.info("👋 Chưa có dữ liệu của ngày hôm nay. Hãy chọn Thể loại/Quốc gia bên trái và bấm '🚀 Quét Chart'.")

# === VIEW 2: SEARCH RESULTS ===
elif st.session_state.view_mode == 'search_results':
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))
    st.title(f"🔎 Kết quả tìm kiếm")
    
    results = st.session_state.search_results
    if results:
        cols = st.columns(3)
        for i, app in enumerate(results):
            with cols[i % 3]:
                render_mini_card(app, COUNTRIES_LIST[search_country_label], i, "sr")
    else:
        st.warning("Không tìm thấy kết quả nào.")

# === VIEW 3: APP DETAIL ===
elif st.session_state.view_mode == 'detail' and st.session_state.selected_app:
    # Lấy thông tin từ state
    app_meta = st.session_state.selected_app
    curr_country = app_meta.get('country_override', target_country)
    target_id = app_meta['app_id']
    
    st.button("⬅️ Quay lại danh sách", on_click=lambda: st.session_state.update(view_mode='list'))

    # Logic tải dữ liệu chi tiết (nếu ID thay đổi hoặc chưa có data)
    if st.session_state.detail_id != target_id or st.session_state.detail_country != curr_country:
        with st.spinner(f"Đang phân tích chi tiết: {target_id}..."):
            d = run_node_safe("DETAIL", target_id, curr_country, "app_detail.json")
            if d:
                st.session_state.detail_data = d
                st.session_state.detail_id = target_id
                st.session_state.detail_country = curr_country
                
                # Tải thêm Similar và Developer Apps song song (nếu cần tối ưu)
                # Ở đây gọi tuần tự cho an toàn
                run_node_safe("SIMILAR", target_id, curr_country, "similar_apps.json")
                if d.get('developerId'):
                    run_node_safe("DEVELOPER", str(d.get('developerId')), curr_country, "developer_apps.json")
            else:
                st.error("Không thể lấy dữ liệu chi tiết ứng dụng này.")
    
    # Hiển thị dữ liệu
    d = st.session_state.detail_data
    if d:
        # 1. Hero Header
        st.markdown(f"""
        <div class="hero-header">
            <img src="{d.get('icon')}" class="hero-icon-big">
            <div>
                <h1 class="hero-title-text">{d.get('title')}</h1>
                <div class="hero-dev-text">by {d.get('developer')}</div>
                <span>{d.get('appId')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Metrics Grid
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card-custom">
                <span class="metric-val">⭐ {d.get('score', 0):.1f}</span>
                <span class="metric-lbl">Rating</span>
            </div>
            <div class="metric-card-custom">
                <span class="metric-val">📥 {d.get('installs', 'N/A')}</span>
                <span class="metric-lbl">Installs</span>
            </div>
            <div class="metric-card-custom">
                <span class="metric-val">💬 {d.get('ratings', 0):,}</span>
                <span class="metric-lbl">Ratings Count</span>
            </div>
             <div class="metric-card-custom">
                <span class="metric-val">🔄 {d.get('updated', 'N/A')}</span>
                <span class="metric-lbl">Updated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Tabs
        t1, t2, t3, t4 = st.tabs(["📝 Mô tả", "📊 Reviews", "⚔️ Đối thủ", "ℹ️ Thông tin khác"])
        
        with t1:
            st.markdown(d.get('descriptionHTML', ''), unsafe_allow_html=True)
            
        with t2:
            comments = d.get('comments', [])
            if comments:
                for c in comments:
                    star = "⭐" * c.get('score', 0)
                    st.markdown(f"""
                    <div class="review-card-modern">
                        <strong>{c.get('userName')}</strong> - {c.get('date')} <br>
                        <span style="color:#ffbd45">{star}</span> <br>
                        <i>"{c.get('text')}"</i>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Chưa có review nào được tải về.")
                
        with t3:
            # Load file similar_apps.json
            sim_path = "data/similar_apps.json"
            if os.path.exists(sim_path):
                try:
                    with open(sim_path, "r", encoding="utf-8") as f: sims = json.load(f)
                    if sims:
                        cols = st.columns(3)
                        for i, s in enumerate(sims[:9]): # Lấy top 9
                             with cols[i % 3]: render_mini_card(s, curr_country, i, "sim")
                    else: st.info("Không tìm thấy ứng dụng tương tự.")
                except: st.info("Lỗi đọc dữ liệu đối thủ.")
            else: st.info("Đang tải dữ liệu...")
            
        with t4:
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Version:** {d.get('version')}")
                st.write(f"**Android:** {d.get('androidVersion')}")
                st.write(f"**Developer ID:** {d.get('developerId')}")
            with c2:
                st.write(f"**Email:** {d.get('developerEmail')}")
                st.write(f"**Website:** {d.get('developerWebsite')}")
                st.write(f"**Address:** {d.get('developerAddress')}")
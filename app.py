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

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Mobile Market Analyzer", layout="wide", page_icon="📱")
DB_PATH = 'data/market_data.db'
NODE_SCRIPT = 'scraper.js'

# --- 2. [AUTO-INSTALL] HỆ THỐNG TỰ CÀI ĐẶT ---
def init_environment():
    if not os.path.exists('data'): os.makedirs('data')
    
    # File lock đánh dấu phiên bản "Full Features"
    install_flag = "install_v10_ultimate.lock" 

    if not os.path.exists(install_flag):
        st.toast("♻️ Đang nâng cấp hệ thống...", icon="🚀")
        if os.path.exists('node_modules'): shutil.rmtree('node_modules', ignore_errors=True)
        if os.path.exists('package-lock.json'): os.remove('package-lock.json')
        try:
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
            with open(install_flag, 'w') as f: f.write("ok")
            st.toast("✅ Nâng cấp xong! Reloading...", icon="🎉")
            time.sleep(1)
            st.rerun()
        except: st.error("Lỗi cài đặt Node.js."); st.stop()

init_environment()

# --- 3. DỮ LIỆU CẤU HÌNH ---
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

# --- 4. QUẢN LÝ TRẠNG THÁI (SESSION) ---
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
if 'selected_app' not in st.session_state: st.session_state.selected_app = None
if 'search_results' not in st.session_state: st.session_state.search_results = []
if 'detail_id' not in st.session_state: st.session_state.detail_id = None
if 'detail_data' not in st.session_state: st.session_state.detail_data = None
if 'current_reviews' not in st.session_state: st.session_state.current_reviews = []
if 'next_token' not in st.session_state: st.session_state.next_token = None
if 'similar_apps' not in st.session_state: st.session_state.similar_apps = []
if 'dev_apps' not in st.session_state: st.session_state.dev_apps = []

# --- 5. CSS GIAO DIỆN (FULL) ---
st.markdown("""
<style>
    /* Card Xịn */
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
    .metric-score { color: #ffbd45; font-weight: 700; font-size: 0.95em; display: flex; align-items: center; margin-top: 5px; }

    /* Review Card */
    .review-card-modern { background-color: #2a2d3a; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #ffbd45; }
    .review-header { display: flex; justify-content: space-between; margin-bottom: 8px; color: #ccc; font-size: 0.9em; }
    .review-user { font-weight: 700; color: #fff; }
    
    /* Metrics Grid */
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
    .metric-card-custom { background: #23252e; padding: 20px 15px; border-radius: 16px; text-align: center; border: 1px solid #333; }
    .metric-val { font-size: 1.6em; font-weight: 800; color: #fff; display: block; }
    .metric-lbl { font-size: 0.85em; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Tags */
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; margin-right: 6px; display: inline-block; border: 1px solid rgba(255,255,255,0.1); }
    .badge-ad { background: rgba(230, 81, 0, 0.2); color: #ff9800; }
    .badge-iap { background: rgba(27, 94, 32, 0.2); color: #4caf50; }
    .badge-free { background: rgba(13, 71, 161, 0.2); color: #64b5f6; }
    
    div.stButton > button { width: 100%; border-radius: 10px; font-weight: 600; }
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
    except Exception: return None
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return None
    return None

def save_data_to_db(cat, country):
    if not os.path.exists("data/raw_data.json"): return False
    try:
        with open("data/raw_data.json", 'r', encoding='utf-8') as f: data = json.load(f)
    except: return False
    if not data: return False
    
    conn = sqlite3.connect(DB_PATH)
    today = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
    conn.execute("DELETE FROM app_history WHERE category=? AND country=? AND scraped_at>=?", (cat, country, today))
    conn.execute('''CREATE TABLE IF NOT EXISTS app_history (
            scraped_at TIMESTAMP, category TEXT, country TEXT, collection_type TEXT,
            rank INT, app_id TEXT, title TEXT, developer TEXT, score REAL,
            installs TEXT, price REAL, currency TEXT, icon TEXT, reviews INT)''')
    clean = []
    ts = datetime.datetime.now()
    for i in data:
        clean.append((ts, i.get('category'), i.get('country'), i.get('collection_type'), i.get('rank'), i.get('appId') or i.get('app_id'), i.get('title'), i.get('developer'), i.get('score', 0), i.get('installs', 'N/A'), i.get('price', 0), 'VND', i.get('icon', ''), 0))
    conn.executemany('INSERT INTO app_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', clean)
    conn.commit(); conn.close(); return True

def load_data_today(cat, country):
    conn = sqlite3.connect(DB_PATH)
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return pd.read_sql(f"SELECT * FROM app_history WHERE category='{cat}' AND country='{country}' AND strftime('%Y-%m-%d', scraped_at)='{today}'", conn)
    except: return pd.DataFrame()

# --- 7. UI RENDERER ---
def render_mini_card(app, country, rank_idx, key_prefix):
    icon = app.get('icon') or 'https://via.placeholder.com/72'
    title = app.get('title', 'Unknown')
    dev = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    app_id = app.get('appId') or app.get('app_id') or f"u_{rank_idx}"
    rank = rank_idx + 1
    
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
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Chi tiết", key=f"btn_{key_prefix}_{app_id}"):
        st.session_state.selected_app = {'app_id': app_id, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()

# --- 8. SIDEBAR ---
st.sidebar.title("🚀 Super Tool")

# Khu vực tìm kiếm & Gợi ý
st.sidebar.subheader("🔍 Tìm kiếm")
search_term = st.sidebar.text_input("Từ khóa / App ID:")
search_country = COUNTRIES_LIST[st.sidebar.selectbox("Quốc gia", list(COUNTRIES_LIST.keys()))]

c1, c2 = st.sidebar.columns(2)
if c1.button("🔎 Tìm"):
    if search_term:
        with st.spinner("Đang tìm..."):
            res = run_node_safe("SEARCH", search_term, search_country, "search_results.json")
            if res:
                st.session_state.search_results = res
                st.session_state.view_mode = 'search_results'
                st.rerun()
            else: st.error("Không tìm thấy.")

if c2.button("💡 Gợi ý"):
    if search_term:
        sugs = run_node_safe("SUGGEST", search_term, search_country, "suggest_results.json")
        if sugs: st.sidebar.success(f"Gợi ý: {', '.join(sugs)}")
        else: st.sidebar.warning("Không có gợi ý.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Top Charts")
sel_cat = CATEGORIES_LIST[st.sidebar.selectbox("Thể Loại", list(CATEGORIES_LIST.keys()))]

if st.sidebar.button("🚀 Quét Chart", type="primary"):
    with st.status("Đang xử lý...", expanded=True):
        st.write("📡 Đang quét dữ liệu Google Play...")
        subprocess.run(["node", NODE_SCRIPT, "LIST", sel_cat, search_country], check=True)
        st.write("💾 Đang lưu vào Database...")
        if save_data_to_db(sel_cat, search_country):
            st.session_state.view_mode = 'list'
            st.rerun()

with st.sidebar.expander("📂 Tiện ích khác"):
    if st.button("Check Danh mục"):
        cats = run_node_safe("CATEGORIES", "", "", "all_categories.json")
        st.write(cats)

# --- 9. MAIN CONTENT ---

# A. LIST VIEW
if st.session_state.view_mode == 'list':
    st.title(f"📊 Market: {sel_cat} ({search_country.upper()})")
    df = load_data_today(sel_cat, search_country)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.subheader("🔥 Top Free")
            for i, r in enumerate(df[df['collection_type']=='top_free'].sort_values('rank').head(20).to_dict('records')): render_mini_card(r, search_country, i, "tf")
        with c2: 
            st.subheader("💸 Top Paid")
            for i, r in enumerate(df[df['collection_type']=='top_paid'].sort_values('rank').head(20).to_dict('records')): render_mini_card(r, search_country, i, "tp")
        with c3: 
            st.subheader("💰 Grossing")
            for i, r in enumerate(df[df['collection_type']=='top_grossing'].sort_values('rank').head(20).to_dict('records')): render_mini_card(r, search_country, i, "tg")
    else: st.info("Chưa có dữ liệu hôm nay. Bấm '🚀 Quét Chart' để lấy data.")

# B. SEARCH RESULTS
elif st.session_state.view_mode == 'search_results':
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))
    st.title(f"🔎 Kết quả: '{search_term}'")
    res = st.session_state.search_results
    if res:
        cols = st.columns(3)
        for i, app in enumerate(res):
            with cols[i%3]: render_mini_card(app, search_country, i, "sr")
    else: st.warning("Không tìm thấy kết quả.")

# C. DETAIL VIEW
elif st.session_state.view_mode == 'detail' and st.session_state.selected_app:
    meta = st.session_state.selected_app
    app_id, country = meta['app_id'], meta['country_override']
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))

    # Logic Load Data
    if st.session_state.detail_id != app_id:
        with st.spinner(f"Đang phân tích {app_id}..."):
            d = run_node_safe("DETAIL", app_id, country, "app_detail.json")
            if d:
                st.session_state.detail_data = d
                st.session_state.detail_id = app_id
                st.session_state.current_reviews = d.get('comments', [])
                st.session_state.next_token = d.get('nextToken')
                st.session_state.dev_apps = [] # Reset dev apps
                
                # Load Async Similar & Dev
                run_node_safe("SIMILAR", app_id, country, "similar_apps.json")
                if d.get('developerId'):
                    run_node_safe("DEVELOPER", str(d['developerId']), country, "developer_apps.json")

    d = st.session_state.detail_data
    
    # Reload phụ (nếu có file)
    if os.path.exists("data/similar_apps.json"):
        try: st.session_state.similar_apps = json.load(open("data/similar_apps.json"))
        except: pass
    if os.path.exists("data/developer_apps.json"):
        try: st.session_state.dev_apps = json.load(open("data/developer_apps.json"))
        except: pass

    if d:
        # 1. Header & Metrics
        badges = ""
        if d.get('adSupported'): badges += "<span class='badge badge-ad'>Ads</span>"
        if d.get('offersIAP'): badges += "<span class='badge badge-iap'>IAP</span>"
        badges += f"<span class='badge badge-free'>{d.get('priceText') or 'Free'}</span>"

        st.markdown(f"""
        <div class="hero-header">
            <img src="{d.get('icon')}" class="hero-icon-big">
            <div>
                <h1 class="hero-title-text">{d.get('title')}</h1>
                <div class="hero-dev-text">by {d.get('developer')}</div>
                <div style="margin-bottom:10px;">{badges}</div>
                <span class="hero-id-text">ID: {d.get('appId')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card-custom"><span class="metric-val">⭐ {d.get('score', 0):.1f}</span><span class="metric-lbl">Rating</span></div>
            <div class="metric-card-custom"><span class="metric-val">📥 {d.get('installs', 'N/A')}</span><span class="metric-lbl">Installs</span></div>
            <div class="metric-card-custom"><span class="metric-val">💬 {d.get('ratings', 0):,}</span><span class="metric-lbl">Reviews</span></div>
            <div class="metric-card-custom"><span class="metric-val">🔄 {d.get('updated', 'N/A')}</span><span class="metric-lbl">Updated</span></div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Tabs Full Tính Năng
        t1, t2, t3, t4, t5, t6 = st.tabs(["📝 Mô tả", "📊 Reviews", "🛡️ Data Safety", "⚔️ Đối thủ", "🏢 Cùng Dev", "ℹ️ Thông tin"])

        with t1: st.markdown(d.get('descriptionHTML', ''), unsafe_allow_html=True)

        # TAB REVIEW (KHÔI PHỤC FULL)
        with t2:
            c_fil, c_chart = st.columns([1, 2])
            with c_fil:
                rev_filter = st.selectbox("Lọc:", ["Tất cả", "Tích cực (4-5⭐)", "Tiêu cực (1-3⭐)"])
            
            all_revs = st.session_state.current_reviews
            show_revs = all_revs
            if rev_filter == "Tích cực (4-5⭐)": show_revs = [r for r in all_revs if r.get('score', 0) >= 4]
            if rev_filter == "Tiêu cực (1-3⭐)": show_revs = [r for r in all_revs if r.get('score', 0) <= 3]

            with c_chart:
                hist = d.get('histogram', {})
                if hist:
                    h_df = pd.DataFrame({'Sao':['1','2','3','4','5'], 'Lượng':[hist.get(k,0) for k in ['1','2','3','4','5']]})
                    fig = px.bar(h_df, x='Sao', y='Lượng', color='Sao', color_discrete_sequence=['#e53935','#fb8c00','#fdd835','#7cb342','#43a047'])
                    fig.update_layout(height=150, margin=dict(t=0,b=0,l=0,r=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#ccc', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            st.caption(f"Hiển thị {len(show_revs)} / {len(all_revs)} đánh giá.")
            st.markdown("---")
            
            for r in show_revs:
                st.markdown(f"""
                <div class="review-card-modern">
                    <div class="review-header">
                        <span class="review-user">{r.get('userName')}</span>
                        <span>{r.get('date')}</span>
                    </div>
                    <div style="color:#ffbd45;">{'⭐'*r.get('score', 0)}</div>
                    <div style="font-style:italic; margin-top:5px; color:#ddd;">"{r.get('text')}"</div>
                </div>""", unsafe_allow_html=True)

            if st.session_state.next_token:
                if st.button("⬇️ Tải thêm review cũ hơn", use_container_width=True):
                    with st.spinner("Đang tải..."):
                        more = run_node_safe("MORE_REVIEWS", app_id, country, "more_reviews.json", st.session_state.next_token)
                        if more and more.get('comments'):
                            st.session_state.current_reviews.extend(more.get('comments'))
                            st.session_state.next_token = more.get('nextToken')
                            st.rerun()
                        elif more and more.get('error'):
                            st.warning(f"Dừng tải: {more.get('error')}")
                            st.session_state.next_token = None
                            st.rerun()
                        else:
                            st.info("Đã hết review."); st.session_state.next_token = None; st.rerun()

        # TAB DATA SAFETY (MỚI)
        with t3:
            ds = d.get('dataSafety', {})
            if ds:
                st.info(ds.get('summary', ''))
                c_s, c_c = st.columns(2)
                with c_s: 
                    st.markdown("### 📤 Shared Data")
                    for x in ds.get('sharedData', []): st.write(f"- {x.get('data')}: {x.get('purpose')}")
                with c_c:
                    st.markdown("### 📥 Collected Data")
                    for x in ds.get('collectedData', []): st.write(f"- {x.get('data')}: {x.get('purpose')}")
            else: st.warning("Không có thông tin Data Safety.")

        # TAB ĐỐI THỦ
        with t4:
            if st.session_state.similar_apps:
                cols = st.columns(3)
                for i, s in enumerate(st.session_state.similar_apps[:9]):
                    with cols[i%3]: render_mini_card(s, country, i, "sim")
            else: st.info("Đang tải hoặc không có đối thủ...")

        # TAB CÙNG DEV (KHÔI PHỤC)
        with t5:
            if st.session_state.dev_apps:
                cols = st.columns(3)
                # Lọc bỏ app hiện tại
                dev_list = [a for a in st.session_state.dev_apps if a.get('appId') != app_id]
                for i, s in enumerate(dev_list[:9]):
                    with cols[i%3]: render_mini_card(s, country, i, "dev")
            else: st.info("Dev này chỉ có 1 app này hoặc đang tải...")

        # TAB THÔNG TIN
        with t6:
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Version:** {d.get('version')}")
                st.write(f"**Android:** {d.get('androidVersion')}")
                st.write(f"**Email:** {d.get('developerEmail')}")
            with c2:
                st.write(f"**Website:** {d.get('developerWebsite')}")
                st.write(f"**Address:** {d.get('developerAddress')}")
                st.write(f"**Privacy:** [Link]({d.get('privacyPolicy')})")
            
            st.markdown("---")
            st.markdown("### 🔑 Permissions")
            if d.get('permissions'):
                for p in d.get('permissions'):
                    st.markdown(f"- **{p.get('permission')}**: {p.get('description') or ''}")
            else: st.info("Không yêu cầu quyền đặc biệt.")
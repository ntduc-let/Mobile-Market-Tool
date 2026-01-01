import streamlit as st

def load_css():
    st.markdown("""
    <style>
        /* --- 1. GLOBAL VARIABLES & RESET --- */
        :root {
            --bg-color: #0e1117;
            --card-bg: #161b22; /* Github Dark Dimmed style */
            --card-hover: #1f242e;
            --border-color: rgba(240, 246, 252, 0.1);
            --accent-primary: #58a6ff; /* Xanh dịu */
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --success: #3fb950;
            --warning: #d29922;
        }

        .stApp { background-color: var(--bg-color); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        
        /* --- 2. METRIC CARDS (DASHBOARD TOP) --- */
        .kpi-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            transition: all 0.2s;
        }
        .kpi-label { font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-value { font-size: 1.8rem; font-weight: 700; color: #fff; margin-top: 5px; }

        /* --- 3. APP MINI CARD (LIST VIEW) --- */
        .app-card-top {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px; /* Bo góc vừa phải */
            padding: 16px;
            margin-bottom: 12px;
            display: flex; gap: 16px; align-items: center;
            transition: transform 0.2s, border-color 0.2s;
        }
        .app-card-top:hover {
            transform: translateY(-2px);
            border-color: var(--accent-primary);
            background-color: var(--card-hover);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .rank-badge { 
            min-width: 40px; height: 40px; 
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; font-weight: 700; color: var(--text-secondary);
            background: rgba(255,255,255,0.03); border-radius: 8px;
        }
        
        .app-icon-opt { 
            width: 64px; height: 64px; /* Icon nhỏ lại chút cho tinh tế */
            border-radius: 14px; 
            object-fit: cover; border: 1px solid var(--border-color);
        }
        
        .app-info-col { flex: 1; overflow: hidden; display: flex; flex-direction: column; gap: 4px; }
        .app-title-opt { font-size: 1rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .app-dev-opt { font-size: 0.85rem; color: var(--text-secondary); }

        .meta-tags { display: flex; gap: 8px; margin-top: 6px; }
        .meta-pill { 
            font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; 
            background: rgba(255,255,255,0.05); color: var(--text-primary); 
            border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 4px;
        }
        
        /* Custom Button Override */
        div[data-testid="stButton"] button {
            border-radius: 8px; font-weight: 600; border: 1px solid var(--border-color);
            background-color: transparent; color: var(--accent-primary);
        }
        div[data-testid="stButton"] button:hover {
            border-color: var(--accent-primary); color: #fff; background: rgba(88, 166, 255, 0.1);
        }

        /* --- 4. HERO HEADER (DETAIL VIEW) --- */
        .hero-container {
            position: relative; border-radius: 16px; overflow: hidden; margin-bottom: 24px;
            border: 1px solid var(--border-color); background: #0d1117;
        }
        .hero-bg { filter: blur(30px) opacity(0.3); transform: scale(1.2); }
        .hero-content { padding: 32px; display: flex; align-items: flex-end; gap: 24px; position: relative; z-index: 2; background: linear-gradient(to top, #0d1117 0%, transparent 100%); }
        .hero-icon-big { width: 100px; height: 100px; border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        .hero-title { font-size: 2rem; font-weight: 800; line-height: 1.2; margin-bottom: 8px; }
        
        /* Tabs Clean */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { height: 40px; border-radius: 6px; padding: 0 16px; background-color: transparent; border: none; }
        .stTabs [aria-selected="true"] { background-color: rgba(88, 166, 255, 0.1); color: var(--accent-primary); }

        /* --- HEADER CHÍNH (Fix lỗi gradient bị cắt) --- */
        .main-header-container {
            padding: 24px 0 32px 0;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            /* Gradient trải dài 100% thay vì 50% để không bị vệt cắt giữa màn hình */
            background: linear-gradient(to right, rgba(88, 166, 255, 0.1) 0%, rgba(88, 166, 255, 0.02) 100%);
        }
        
        /* --- DASHBOARD HEADER (Chứa Badges Quốc gia/Thể loại) --- */
        .dashboard-header-container {
            /* Bỏ background tối cũ, dùng border tinh tế hơn */
            background: transparent;
            margin-bottom: 20px; 
            display: flex; 
            align-items: center; 
            gap: 15px;
            padding: 10px 0;
        }
                
        .header-badges { 
            display: flex; gap: 12px; flex-wrap: wrap; 
        }

        /* Badge thiết kế lại: Phẳng, hiện đại, icon nổi bật */
        .h-badge { 
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px; 
            border-radius: 12px; 
            font-size: 0.9rem; 
            font-weight: 600; 
            letter-spacing: 0.3px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* Badge Thể loại (Màu tím neon) */
        .h-badge.category { 
            background: linear-gradient(135deg, rgba(123, 31, 162, 0.2), rgba(123, 31, 162, 0.1));
            border: 1px solid rgba(123, 31, 162, 0.4); 
            color: #e1bee7; 
        }

        /* Badge Quốc gia (Màu xanh dương) */
        .h-badge.country { 
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.2), rgba(33, 150, 243, 0.1));
            border: 1px solid rgba(33, 150, 243, 0.4); 
            color: #90caf9; 
        }
                
        .h-badge:hover { transform: translateY(-2px); filter: brightness(1.2); }

        /* --- EMPTY STATE (Thông báo chưa có dữ liệu đẹp hơn) --- */
        .empty-state-box {
            text-align: center;
            padding: 60px 20px;
            border: 2px dashed var(--border-color); /* Viền nét đứt */
            border-radius: 16px;
            background-color: rgba(22, 27, 34, 0.5);
            margin-top: 20px;
        }
        .empty-icon { font-size: 4rem; margin-bottom: 15px; opacity: 0.8; display: block; animation: float 3s ease-in-out infinite; }
        .empty-title { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 8px; }
        .empty-desc { color: var(--text-secondary); font-size: 1rem; max-width: 500px; margin: 0 auto; }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }

        .header-content-wrapper {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        /* Style cho icon logo giả lập (có thể thay bằng ảnh thật) */
        .header-logo-box {
            width: 64px; height: 64px;
            background: linear-gradient(135deg, var(--accent-primary), #8e44ad);
            border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            font-size: 32px; color: white;
            box-shadow: 0 8px 16px rgba(88, 166, 255, 0.2);
        }

        .header-text-col {
            display: flex; flex-direction: column;
        }

        /* Tiêu đề chính với hiệu ứng gradient text */
        .header-main-title {
            margin: 0;
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: -1px;
            line-height: 1.1;
            /* Tạo màu chữ gradient chuyển từ trắng sang xanh dương */
            background: linear-gradient(90deg, #ffffff 0%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Dòng subtitle phụ */
        .header-subtitle {
            margin: 8px 0 0 0;
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 400;
        }
    </style>
    """, unsafe_allow_html=True)
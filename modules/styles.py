# modules/styles.py
import streamlit as st

def load_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        
        /* --- CARD TOP (INFO PART) --- */
        .app-card-top {
            background: linear-gradient(145deg, #1e2028, #242730);
            border-radius: 16px; /* Bo tròn cả 4 góc */
            padding: 16px 20px;
            margin-bottom: 10px; /* Tạo khoảng cách với nút */
            border: 1px solid rgba(255, 255, 255, 0.08);
            
            display: grid; grid-template-columns: 50px 80px 1fr; gap: 20px; align-items: center;
        }

        /* --- ELEMENTS (Badge, Icon, Text...) --- */
        .rank-badge { font-size: 1.8em; font-weight: 900; text-align: center; opacity: 0.9; font-family: 'Segoe UI', sans-serif; }
        .app-icon-opt { width: 80px; height: 80px; border-radius: 18px; object-fit: cover; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .app-info-col { display: flex; flex-direction: column; gap: 6px; overflow: hidden; justify-content: center; }
        .app-title-opt { font-size: 1.25em; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3; }
        .app-dev-opt { font-size: 0.95em; color: #b0b3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .meta-tags { display: flex; gap: 10px; align-items: center; margin-top: 4px; }
        .meta-pill { font-size: 0.8em; padding: 3px 10px; border-radius: 6px; background: rgba(255,255,255,0.05); color: #ccc; border: 1px solid rgba(255,255,255,0.1); font-weight: 600; }
        .meta-pill.score { color: #ffbd45; border-color: rgba(255, 189, 69, 0.2); }
        .meta-pill.price { color: #69f0ae; border-color: rgba(105, 240, 174, 0.2); }

        /* --- NEW BUTTONS STYLE (OUTLINED PILLS) --- */
        
        /* 1. Cấu hình chung cho cả 2 nút */
        div[data-testid="stLinkButton"] a, div[data-testid="stButton"] button {
            width: 100%;
            background-color: transparent !important; /* Nền trong suốt */
            border-width: 1px !important;
            border-style: solid !important;
            font-weight: 700 !important;
            border-radius: 8px !important; /* Bo góc giống Badge */
            margin-top: -5px !important;   /* Kéo sát lên card trên */
            height: 40px !important;
            transition: all 0.3s ease !important;
            text-transform: none !important;
            display: flex; align-items: center; justify-content: center;
        }

        /* 2. Nút TRÁI (Google Play) -> Style giống thẻ FREE (Màu Xanh Lá) */
        div[data-testid="column"]:nth-of-type(1) div[data-testid="stLinkButton"] a {
            border-color: #69f0ae !important;
            color: #69f0ae !important;
        }
        /* Hover hiệu ứng phát sáng xanh */
        div[data-testid="column"]:nth-of-type(1) div[data-testid="stLinkButton"] a:hover {
            background-color: rgba(105, 240, 174, 0.1) !important;
            box-shadow: 0 0 10px rgba(105, 240, 174, 0.4) !important;
            transform: translateY(-2px);
        }

        /* 3. Nút PHẢI (Chi tiết) -> Style giống thẻ STAR (Màu Vàng) */
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button {
            border-color: #ffbd45 !important;
            color: #ffbd45 !important;
        }
        /* Hover hiệu ứng phát sáng vàng */
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button:hover {
            background-color: rgba(255, 189, 69, 0.1) !important;
            box-shadow: 0 0 10px rgba(255, 189, 69, 0.4) !important;
            transform: translateY(-2px);
        }

        /* --- Detail Header --- */
        .hero-header {
            position: relative; overflow: hidden; display: flex; gap: 25px; padding: 30px;
            background: linear-gradient(180deg, rgba(30,32,40,0.85) 0%, rgba(30,32,40,1) 100%);
            border-radius: 20px; border: 1px solid #3a3f4b; margin-bottom: 25px; align-items: center;
        }
        .hero-bg {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-size: cover; background-position: center; opacity: 0.2; z-index: -1; filter: blur(10px);
        }
        .hero-icon-big { width: 120px; height: 120px; border-radius: 24px; border: 2px solid #444; z-index: 2; }
        .hero-title-text { font-size: 2.5em; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }

        /* --- Metrics & Safety --- */
        .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
        .metric-card-custom { background: #23252e; padding: 20px 15px; border-radius: 16px; text-align: center; border: 1px solid #333; }
        .safety-item { background: #252730; padding: 12px; margin-bottom: 8px; border-radius: 8px; border-left: 3px solid #64b5f6; font-size: 0.95em; }
        .review-card-modern { background-color: #2a2d3a; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #ffbd45; }
        .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; margin-right: 6px; border: 1px solid rgba(255,255,255,0.1); display: inline-block;}
        .badge-ad { background-color: rgba(230, 81, 0, 0.2); color: #ff9800; }
        .badge-iap { background-color: rgba(27, 94, 32, 0.2); color: #4caf50; }

        /* --- Screenshots Zoom --- */
        .screenshot-container { overflow-x: auto; white-space: nowrap; padding-bottom: 15px; }
        .lightbox-toggle { display: none !important; }
        .thumb-label { display: inline-block; margin-right: 15px; cursor: zoom-in; transition: transform 0.2s; border: 1px solid #444; border-radius: 10px; overflow: hidden; }
        .thumb-label:hover { transform: scale(1.02); border-color: #64b5f6; }
        .thumb-img { height: 300px; width: auto; display: block; }
        .lightbox-overlay { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.95); z-index: 999999; justify-content: center; align-items: center; cursor: zoom-out; }
        .lightbox-toggle:checked ~ .lightbox-overlay { display: flex; animation: fadeIn 0.2s ease-out; }
        .full-img {
            position: fixed !important;  /* Ép vị trí cố định theo màn hình */
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important; /* Căn giữa tuyệt đối */

            width: 95vw !important;      /* Chiếm 95% chiều ngang màn hình */
            height: 95vh !important;     /* Chiếm 95% chiều dọc màn hình */

            max-width: none !important;  /* Gỡ bỏ mọi giới hạn chiều rộng */
            max-height: none !important; /* Gỡ bỏ mọi giới hạn chiều cao */

            object-fit: contain !important; /* Đảm bảo ảnh không bị méo */
            z-index: 1000000 !important;    /* Đảm bảo luôn nằm trên cùng */

            background-color: transparent;  /* Nền trong suốt */
            box-shadow: none !important;    /* Bỏ bóng đổ nếu có */
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                
        /* Dashboard Header */
        .dashboard-header-container {
            background: linear-gradient(90deg, #1e222b 0%, #262a35 100%);
            padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2); margin-bottom: 25px; display: flex; flex-direction: column; gap: 5px;
        }
        .header-sub { text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1.5px; font-weight: 700; color: #64b5f6; display: flex; align-items: center; gap: 8px; }
        .header-main { font-size: 2rem; font-weight: 800; color: #ffffff; line-height: 1.2; background: -webkit-linear-gradient(45deg, #ffffff, #e0e0e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header-badges { display: flex; gap: 12px; margin-top: 10px; flex-wrap: wrap; }
        .h-badge { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 6px 14px; border-radius: 50px; font-size: 0.9rem; font-weight: 600; color: #e0e0e0; }
        .h-badge.country { border-color: #ff4b4b; color: #ffbcbc; background: rgba(255, 75, 75, 0.1); }
        .h-badge.category { border-color: #4caf50; color: #b9f6ca; background: rgba(76, 175, 80, 0.1); }
                
        /* --- REVIEW CARD CHI TIẾT --- */
        .rev-container {
            background-color: #1e2028;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .rev-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
        .rev-user-info { display: flex; gap: 12px; align-items: center; }
        .rev-avatar { 
            width: 40px; height: 40px; border-radius: 50%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Avatar giả gradient */
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; color: white; font-size: 1.2em;
        }
        .rev-name { font-weight: 700; color: #fff; font-size: 0.95em; }
        .rev-date { font-size: 0.8em; color: #888; }
        
        .rev-star-row { color: #ffbd45; margin-bottom: 8px; font-size: 1.1em; display: flex; gap: 10px; align-items: center; }
        .rev-version { 
            font-size: 0.75em; padding: 2px 8px; border-radius: 4px; 
            background: #2d3748; color: #a0aec0; border: 1px solid #4a5568; 
        }
        
        .rev-text { color: #e2e8f0; line-height: 1.5; font-size: 0.95em; margin-bottom: 12px; white-space: pre-wrap; }
        
        .rev-footer { display: flex; gap: 15px; font-size: 0.85em; color: #718096; align-items: center; }
        .rev-like { display: flex; align-items: center; gap: 5px; cursor: default; }
        
        /* Box trả lời của Developer */
        .dev-reply-box {
            margin-top: 15px;
            background-color: #232a3b; /* Nền đậm hơn */
            border-left: 3px solid #64b5f6;
            padding: 12px 15px;
            border-radius: 0 8px 8px 0;
        }
        .dev-reply-header { font-size: 0.85em; font-weight: 700; color: #64b5f6; margin-bottom: 5px; display: flex; justify-content: space-between; }
        .dev-reply-text { font-size: 0.9em; color: #cbd5e0; font-style: italic; }

        /* --- DATA SAFETY STYLES (NEW) --- */

        /* 1. Khung chứa Security Practices (Màu xanh bảo mật) */
        .security-box {
            background-color: rgba(27, 94, 32, 0.15); /* Nền xanh lá nhạt */
            border: 1px solid #2e7d32;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .sec-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 8px;
            color: #e8f5e9;
            font-size: 0.95em;
        }
        .sec-icon { color: #69f0ae; font-size: 1.2em; margin-top: 2px; }

        /* 2. Thẻ dữ liệu chi tiết (Data Card) */
        .data-item-card {
            background-color: #23252e;
            border: 1px solid #3a3f4b;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            transition: all 0.2s;
        }
        .data-item-card:hover { border-color: #64b5f6; background-color: #2a2d36; }

        .data-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .data-name { font-weight: 700; color: #fff; font-size: 0.95em; }
        .data-type { color: #aaa; font-size: 0.85em; font-style: italic; }

        .data-purpose { 
            font-size: 0.85em; color: #ccc; 
            background: rgba(255,255,255,0.05); 
            padding: 6px; border-radius: 6px; margin-top: 6px; 
            line-height: 1.4;
        }

        /* 3. Badges trạng thái */
        .badge-req { background: rgba(255, 75, 75, 0.2); color: #ff8a80; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; border: 1px solid rgba(255, 75, 75, 0.3); }
        .badge-opt { background: rgba(105, 240, 174, 0.2); color: #b9f6ca; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; border: 1px solid rgba(105, 240, 174, 0.3); }
        
        /* --- MỚI: CSS CHO TAB INFO --- */
        /* 1. Grid chứa thông tin kỹ thuật */
        .info-grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .info-box-item {
            background-color: #1e2028;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            transition: transform 0.2s;
        }
        .info-box-item:hover {
            border-color: #64b5f6;
            transform: translateY(-2px);
            background-color: #232630;
        }
        
        .ib-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #8b949e;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .ib-value {
            font-size: 1rem;
            color: #e6edf3;
            font-weight: 700;
            word-break: break-word;
        }
        
        /* 2. Developer Contact Card */
        .dev-contact-card {
            background: linear-gradient(145deg, #161b22, #0d1117);
            border-left: 4px solid #f78c6c; /* Màu cam */
            padding: 20px;
            border-radius: 0 12px 12px 0;
            margin-bottom: 25px;
        }
        .dev-row {
            display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
            color: #c9d1d9; font-size: 0.95rem;
        }
        .dev-row a { color: #58a6ff; text-decoration: none; }
        .dev-row a:hover { text-decoration: underline; }
        .dev-icon { width: 20px; text-align: center; color: #f78c6c; }

        /* 3. Description Styling */
        .desc-container {
            background-color: #161b22;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            color: #c9d1d9;
            line-height: 1.6;
            font-size: 0.95rem;
        }
        /* Style cho HTML description từ Google trả về */
        .desc-container h2, .desc-container h3 { color: #fff; margin-top: 15px; margin-bottom: 10px; }
        .desc-container b { color: #e6edf3; }        
        </style>
    """, unsafe_allow_html=True)
# modules/styles.py
import streamlit as st

def load_css():
    st.markdown("""
    <style>
        /* --- Global Reset --- */
        .stApp { background-color: #0e1117; }
        
        /* --- 1. CARD TOP (INFO PART) --- */
        .app-card-top {
            background: linear-gradient(145deg, #1e2028, #242730);
            border-radius: 16px 16px 0 0; /* Chỉ bo góc trên */
            padding: 16px 20px;
            margin-bottom: 0px !important; /* Xóa khoảng cách dưới */
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-bottom: none; /* Bỏ viền dưới để nối với nút */
            
            /* Grid Layout */
            display: grid;
            grid-template-columns: 50px 80px 1fr;
            gap: 20px;
            align-items: center;
        }

        /* --- 2. CARD ELEMENTS --- */
        .rank-badge { 
            font-size: 1.8em; font-weight: 900; text-align: center; opacity: 0.9; 
            font-family: 'Segoe UI', sans-serif;
        }
        
        .app-icon-opt { 
            width: 80px; height: 80px; 
            border-radius: 18px; object-fit: cover; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.3); 
        }

        .app-info-col { 
            display: flex; flex-direction: column; gap: 6px; overflow: hidden; justify-content: center;
        }
        
        .app-title-opt { 
            font-size: 1.25em; font-weight: 700; color: #fff; 
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3;
        }
        
        .app-dev-opt { 
            font-size: 0.95em; color: #b0b3b8; 
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
        }
        
        .meta-tags { display: flex; gap: 10px; align-items: center; margin-top: 4px; }
        .meta-pill {
            font-size: 0.8em; padding: 3px 10px; border-radius: 6px;
            background: rgba(255,255,255,0.05); color: #ccc; border: 1px solid rgba(255,255,255,0.1);
            font-weight: 600;
        }
        .meta-pill.score { color: #ffbd45; border-color: rgba(255, 189, 69, 0.2); }
        .meta-pill.price { color: #69f0ae; border-color: rgba(105, 240, 174, 0.2); }

        /* --- 3. BUTTONS DESIGN (CARD FOOTER) --- */
        
        /* Chỉnh sửa nút Link (Store) và Button (Xem) */
        div[data-testid="stLinkButton"] a, div[data-testid="stButton"] button {
            width: 100%;
            border-radius: 0 0 12px 12px !important; /* Bo góc dưới */
            border-top: none !important; /* Bỏ viền trên */
            border: 1px solid rgba(255,255,255,0.1);
            background-color: #242730; /* Màu nền trùng với Card */
            color: #ccc;
            font-weight: 600;
            transition: all 0.2s;
            height: 42px; /* Chiều cao cố định */
            margin-top: -16px; /* Kỹ thuật quan trọng: Kéo nút lên dính vào card */
            z-index: 1;
        }
        
        /* Hiệu ứng Hover riêng biệt */
        div[data-testid="stLinkButton"] a:hover {
            background-color: #1b5e20 !important; /* Xanh lá đậm cho Store */
            color: #fff !important;
            border-color: #4caf50 !important;
        }
        
        div[data-testid="stButton"] button:hover {
            background-color: #0d47a1 !important; /* Xanh dương đậm cho Xem */
            color: #fff !important;
            border-color: #2979ff !important;
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
        .full-img { width: 98vw; height: 98vh; object-fit: contain; }
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
    </style>
    """, unsafe_allow_html=True)
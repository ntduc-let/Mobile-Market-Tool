# modules/styles.py
import streamlit as st

def load_css():
    st.markdown("""
    <style>
        /* --- Global --- */
        .stApp { background-color: #0e1117; }
        
        /* --- Card Design --- */
        .app-card-optimized {
            background: linear-gradient(145deg, #1e222b, #262a35);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            
            /* Dùng Grid để chia bố cục: Rank | Icon | Info | Actions */
            display: grid;
            grid-template-columns: 40px 64px 1fr auto; 
            gap: 15px;
            align-items: center;
        }
        
        .app-card-optimized:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            border-color: rgba(100, 181, 246, 0.5); /* Viền sáng khi hover */
        }

        /* Rank */
        .rank-badge { font-size: 1.5em; font-weight: 900; text-align: center; }
        
        /* Icon */
        .app-icon-opt { width: 64px; height: 64px; border-radius: 14px; object-fit: cover; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        
        /* Info Column */
        .app-info-col { display: flex; flex-direction: column; gap: 4px; overflow: hidden; }
        .app-title-opt { font-size: 1.05em; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .app-dev-opt { font-size: 0.85em; color: #a0a0a0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        /* Meta Tags Row */
        .meta-tags { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 2px; }
        .meta-tag { 
            font-size: 0.75em; padding: 2px 8px; border-radius: 4px; 
            background: rgba(255,255,255,0.05); color: #ccc; border: 1px solid rgba(255,255,255,0.1);
            display: flex; align-items: center; gap: 4px;
        }
        .meta-tag.score { color: #ffbd45; border-color: rgba(255, 189, 69, 0.3); }
        .meta-tag.price { color: #69f0ae; border-color: rgba(105, 240, 174, 0.3); }
        
        /* Action Column (Right Side) */
        .app-actions-col { 
            display: flex; flex-direction: column; gap: 8px; 
            min-width: 100px; /* Đảm bảo nút không bị bóp méo */
        }
        
        /* Custom Buttons */
        .btn-store {
            text-decoration: none;
            display: flex; justify-content: center; align-items: center; gap: 6px;
            background: rgba(255,255,255,0.05); color: #ccc;
            padding: 6px 12px; border-radius: 6px; font-size: 0.8em;
            transition: all 0.2s; border: 1px solid rgba(255,255,255,0.1);
        }
        .btn-store:hover { background: #fff; color: #000; border-color: #fff; }
                
        /* --- Button Override --- */
        div[data-testid="stButton"] button {
            width: 100%;
            border-radius: 6px;
            font-size: 0.8em;
            padding: 0.4rem 0.8rem;
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
                
        /* --- Dashboard Header Style --- */
        .dashboard-header-container {
            background: linear-gradient(90deg, #1e222b 0%, #262a35 100%);
            padding: 25px 30px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            margin-bottom: 25px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .header-sub {
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1.5px;
            font-weight: 700;
            color: #64b5f6; /* Màu xanh dương nhạt */
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-main {
            font-size: 2rem; /* Chữ to */
            font-weight: 800;
            color: #ffffff;
            line-height: 1.2;
            background: -webkit-linear-gradient(45deg, #ffffff, #e0e0e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-badges {
            display: flex;
            gap: 12px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .h-badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            color: #e0e0e0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .h-badge.country { border-color: #ff4b4b; color: #ffbcbc; background: rgba(255, 75, 75, 0.1); }
        .h-badge.category { border-color: #4caf50; color: #b9f6ca; background: rgba(76, 175, 80, 0.1); }
    </style>
    """, unsafe_allow_html=True)
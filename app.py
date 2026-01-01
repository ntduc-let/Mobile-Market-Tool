# app.py
import streamlit as st
from modules.config import CATEGORIES_LIST, COUNTRIES_LIST
from modules.styles import load_css
from modules.backend import init_environment, save_data_to_db, load_data_today, run_node_safe_custom
from modules.views import render_list_view, render_search_results, render_detail_view
from modules.views import render_list_view, render_detail_view, render_custom_header
import subprocess # Dùng cho sidebar scraper

# 1. Config
st.set_page_config(page_title="Mobile Market Tool", layout="wide", page_icon="📱")
load_css()
init_environment()
render_custom_header()

# 2. Session State
if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
if 'selected_app' not in st.session_state: st.session_state.selected_app = None
if 'search_results' not in st.session_state: st.session_state.search_results = []
if 'detail_id' not in st.session_state: st.session_state.detail_id = None
if 'detail_country' not in st.session_state: st.session_state.detail_country = None

# 3. Sidebar
st.sidebar.title("🚀 Super Tool")
st.sidebar.subheader("🔍 Tìm kiếm")
search_term = st.sidebar.text_input("Từ khóa / App ID:")
search_country = st.sidebar.selectbox("Quốc gia (Search)", list(COUNTRIES_LIST.keys()), index=0)
search_limit = st.sidebar.slider("Số lượng", 10, 200, 30)

if st.sidebar.button("🔎 Tìm ngay"):
    s_country_code = COUNTRIES_LIST[search_country]
    if "." in search_term and " " not in search_term:
        st.session_state.selected_app = {'app_id': search_term.strip(), 'title': search_term, 'country_override': s_country_code}
        st.session_state.view_mode = 'detail'
    else:
        with st.status(f"Đang tìm '{search_term}'..."):
            res = run_node_safe_custom("SEARCH", search_term, s_country_code, "search_results.json", str(search_limit))
            st.session_state.search_results = res or []
            st.session_state.view_mode = 'search_results'
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Top Charts")
sel_country_lbl = st.sidebar.selectbox("Quốc Gia", list(COUNTRIES_LIST.keys()))
sel_cat_lbl = st.sidebar.selectbox("Thể Loại", list(CATEGORIES_LIST.keys()))
limit_num = st.sidebar.slider("Số lượng App", 10, 120, 30)

if st.sidebar.button("🚀 Quét Chart", type="primary"):
    with st.status("Đang quét..."):
        try:
            subprocess.run(["node", "scraper.js", "LIST", CATEGORIES_LIST[sel_cat_lbl], COUNTRIES_LIST[sel_country_lbl], str(limit_num)], check=True)
            save_data_to_db(CATEGORIES_LIST[sel_cat_lbl], COUNTRIES_LIST[sel_country_lbl])
            st.session_state.view_mode = 'list'
            st.rerun()
        except Exception as e: st.error(f"Lỗi: {e}")

# 4. Main Router
if st.session_state.view_mode == 'list':
    st.markdown(f"""
    <div class="dashboard-header-container">
        <div class="header-badges">
            <span class="h-badge category">{sel_cat_lbl}</span>
            <span class="h-badge country">{sel_country_lbl}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ----------------------------
    df = load_data_today(CATEGORIES_LIST[sel_cat_lbl], COUNTRIES_LIST[sel_country_lbl])
    render_list_view(df, sel_country_lbl)

elif st.session_state.view_mode == 'search_results':
    render_search_results()

elif st.session_state.view_mode == 'detail':
    render_detail_view(CATEGORIES_LIST[sel_cat_lbl])
# modules/views.py
import streamlit as st
import pandas as pd
import time
import plotly.express as px
from .components import render_mini_card
from .backend import run_node_safe
from .config import COUNTRIES_LIST

def render_list_view(df, sel_country_lbl):
    if not df.empty:
        st.divider()
        col_free, col_paid, col_gross = st.columns(3)
        def render_column(container, header_title, collection_name, key_suffix, header_color):
            with container:
                st.markdown(f"""<div style="text-align: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid {header_color};"><h3 style="margin:0; color: {header_color}; text-shadow: 0 0 10px {header_color}80;">{header_title}</h3></div>""", unsafe_allow_html=True)
                subset = df[df['collection_type'] == collection_name].sort_values('rank')
                if not subset.empty:
                    for i, r in enumerate(subset.to_dict('records')):
                        render_mini_card(r, COUNTRIES_LIST[sel_country_lbl], i, key_suffix, theme_color=header_color)
                else: st.info("Chưa có dữ liệu.")
        render_column(col_free, "🔥 Top Free", "top_free", "tf", "#00e676")       
        render_column(col_paid, "💸 Top Paid", "top_paid", "tp", "#2979ff")       
        render_column(col_gross, "💰 Grossing", "top_grossing", "tg", "#ffab00")
    else: st.info("👋 Chưa có dữ liệu. Hãy chọn và bấm '🚀 Quét Chart'.")

def render_search_results():
    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))
    results = st.session_state.search_results
    st.title(f"🔎 Kết quả: {len(results)} ứng dụng")
    if results:
        st.divider()
        search_country_code = 'vn' 
        cols = st.columns(3)
        for i, app in enumerate(results):
            with cols[i % 3]: render_mini_card(app, search_country_code, i, "sr")
    else: st.warning("Không tìm thấy kết quả.")

def render_detail_view(target_cat_default):
    app = st.session_state.selected_app
    curr_country = app.get('country_override', 'vn')
    target_id = app['app_id']

    st.button("⬅️ Quay lại", on_click=lambda: st.session_state.update(view_mode='list'))

    # Load data Detail
    if st.session_state.detail_id != target_id or st.session_state.detail_country != curr_country:
        with st.spinner(f"Đang phân tích {target_id}..."):
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
                run_node_safe("SIMILAR", target_id, curr_country, "similar_apps.json")
                if d.get('developerId'): run_node_safe("DEVELOPER", str(d.get('developerId')), curr_country, "developer_apps.json")

    d = st.session_state.detail_data
    if not d: return

    # Header
    bg_url = d.get('headerImage') or d.get('icon')
    badges = ""
    if d.get('adSupported'): badges += "<span class='badge badge-ad'>Ads</span>"
    if d.get('offersIAP'): badges += "<span class='badge badge-iap'>IAP</span>"
    st.markdown(f"""<div class="hero-header"><div class="hero-bg" style="background-image: url('{bg_url}');"></div><img src="{d.get('icon')}" class="hero-icon-big"><div style="z-index: 2; color: white;"><h1 class="hero-title-text">{d.get('title')}</h1><div style="color: #64b5f6; margin-bottom: 10px;">by {d.get('developer')}</div><div>{badges}</div></div></div>""", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Reviews", "📸 Media", "🛡️ Data Safety", "⚔️ Đối thủ", "🏢 Cùng Dev", "ℹ️ Info"])
    
    # --- TAB 1: ADVANCED REVIEWS (ĐÃ NÂNG CẤP) ---
    with tab1:
        # Lấy dữ liệu review hiện tại
        all_revs = st.session_state.current_reviews
        
        # 1. Dashboard tổng quan
        c_chart, c_filter = st.columns([1.5, 1])
        with c_chart:
            # Biểu đồ phân bố sao
            hist = d.get('histogram', {})
            if hist:
                df_hist = pd.DataFrame({'Star': ['1','2','3','4','5'], 'Count': [hist.get('1',0), hist.get('2',0), hist.get('3',0), hist.get('4',0), hist.get('5',0)]})
                fig = px.bar(df_hist, x='Star', y='Count', color='Star', color_discrete_map={'1':'#ff4b4b','2':'#ff9800','3':'#ffeb3b','4':'#cddc39','5':'#4caf50'})
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title=None, yaxis={'visible':False})
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with c_filter:
            st.markdown("##### 🌪️ Bộ lọc")
            # Filter 1: Rating
            sel_rating = st.multiselect("Số sao:", ["5 Sao", "4 Sao", "3 Sao", "2 Sao", "1 Sao"], default=[])
            
            # Filter 2: Version (Lấy dynamic từ data)
            # Lọc ra các version khác None
            versions = sorted(list(set([r.get('version') for r in all_revs if r.get('version')])))
            sel_ver = st.multiselect("Phiên bản App:", versions)

        st.divider()

        # 2. Logic Lọc
        filtered_revs = all_revs
        if sel_rating:
            # Chuyển "5 Sao" -> 5 (int)
            target_scores = [int(s[0]) for s in sel_rating]
            filtered_revs = [r for r in filtered_revs if r.get('score') in target_scores]
        
        if sel_ver:
            filtered_revs = [r for r in filtered_revs if r.get('version') in sel_ver]

        st.caption(f"Hiển thị **{len(filtered_revs)}** / {len(all_revs)} đánh giá.")

        # 3. Hiển thị Review (Card Chi Tiết)
        for r in filtered_revs:
            # Xử lý dữ liệu an toàn
            user_name = r.get('userName', 'Hidden User')
            avatar_char = user_name[0].upper() if user_name else "?"
            score = r.get('score', 0)
            stars = "⭐" * score
            date = r.get('date', '')
            text = r.get('text', '')
            likes = r.get('thumbsUp', 0)
            version = r.get('version', '')
            reply_text = r.get('replyText')
            reply_date = r.get('replyDate')

            version_badge = f"<span class='rev-version'>v{version}</span>" if version else ""
            reply_html = ""
            if reply_text:
                reply_html = f"""
                <div class="dev-reply-box">
                    <div class="dev-reply-header">
                        <span>👨‍💻 Developer Response</span>
                        <span>{reply_date}</span>
                    </div>
                    <div class="dev-reply-text">{reply_text}</div>
                </div>
                """

            st.markdown(f"""
            <div class="rev-container">
                <div class="rev-header">
                    <div class="rev-user-info">
                        <div class="rev-avatar">{avatar_char}</div>
                        <div>
                            <div class="rev-name">{user_name}</div>
                            <div class="rev-date">{date}</div>
                        </div>
                    </div>
                    {version_badge}
                </div>
                <div class="rev-star-row">{stars}</div>
                <div class="rev-text">{text}</div>
                <div class="rev-footer">
                    <div class="rev-like">👍 {likes} Hữu ích</div>
                </div>
                {reply_html}
            </div>
            """, unsafe_allow_html=True)

        # 4. Nút Tải Thêm (Fix Lỗi)
        if st.session_state.next_token:
            if st.button("⬇️ Tải thêm đánh giá cũ hơn", use_container_width=True):
                with st.spinner("Đang tải từ Google..."):
                    # Gọi backend với token
                    more = run_node_safe("MORE_REVIEWS", d['appId'], curr_country, "more_reviews.json", token=st.session_state.next_token)
                    
                    if more and more.get('comments'):
                        # Cập nhật Session State
                        new_comments = more.get('comments', [])
                        st.session_state.current_reviews.extend(new_comments)
                        st.session_state.next_token = more.get('nextToken') # Cập nhật token mới
                        st.success(f"Đã tải thêm {len(new_comments)} review!")
                        time.sleep(1)
                        st.rerun() # Load lại trang để hiển thị data mới
                    elif more and more.get('error'):
                        st.error(f"Lỗi API: {more.get('error')}")
                    else:
                        st.warning("Hết đánh giá để tải.")
                        st.session_state.next_token = None
                        st.rerun()

    with tab2:
        if d.get('screenshots'):
            html = '<div class="screenshot-container">'
            base_id = d.get('appId').replace('.', '_')
            for i, url in enumerate(d.get('screenshots')):
                uid = f"{base_id}_{i}"
                html += f"""<div style="display:inline-block;"><input type="checkbox" id="{uid}" class="lightbox-toggle"><label for="{uid}" class="thumb-label"><img src="{url}" class="thumb-img"></label><label for="{uid}" class="lightbox-overlay"><img src="{url}" class="full-img"></label></div>"""
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
    
    with tab3: # Data Safety
        ds = d.get('dataSafety', {})
        if ds:
            c_shared, c_collected = st.columns(2)
            with c_shared:
                st.markdown("#### 📤 Chia sẻ (Shared)")
                if ds.get('sharedData'):
                    for item in ds.get('sharedData'): st.markdown(f"<div class='safety-item'><b>{item.get('data')}</b><br><small style='color:#ccc'>{item.get('purpose')}</small></div>", unsafe_allow_html=True)
                else: st.success("✅ Không chia sẻ.")
            with c_collected:
                st.markdown("#### 📥 Thu thập (Collected)")
                if ds.get('collectedData'):
                    for item in ds.get('collectedData'): st.markdown(f"<div class='safety-item'><b>{item.get('data')}</b><br><small style='color:#ccc'>{item.get('purpose')}</small></div>", unsafe_allow_html=True)
                else: st.success("✅ Không thu thập.")
        else: st.info("Không có thông tin Data Safety.")

    with tab4: # Competitors
        if st.session_state.similar_apps:
            cols = st.columns(3)
            for i, s in enumerate(st.session_state.similar_apps):
                with cols[i%3]: render_mini_card(s, curr_country, i, "sim")
    
    with tab5: # Dev Apps
        if st.session_state.dev_apps:
            cols = st.columns(3)
            clean_devs = [dv for dv in st.session_state.dev_apps if dv.get('appId') != target_id]
            for i, dv in enumerate(clean_devs):
                with cols[i%3]: render_mini_card(dv, curr_country, i, "dev")

    with tab6: # Info
        c_tech, c_cat = st.columns(2)
        with c_tech:
            st.markdown("#### 📱 Kỹ thuật")
            st.write(f"**ID:** `{d.get('appId')}`")
            st.write(f"**Version:** {d.get('version')}")
            st.write(f"**Size:** {d.get('size')}")
        with c_cat:
            st.markdown("#### 🏷️ Phân loại")
            st.write(f"**Genre:** {d.get('genre')}")
            st.write(f"**Released:** {d.get('released')}")
            st.write(f"**Updated:** {d.get('updated')}")
        st.divider()
        if d.get('recentChanges'):
            st.markdown("#### 🆕 Có gì mới")
            st.info(d.get('recentChanges'))
        st.divider()
        with st.expander("📝 Mô tả chi tiết"):
            st.markdown(d.get('descriptionHTML', ''), unsafe_allow_html=True)
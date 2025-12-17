# modules/views.py
import streamlit as st
import pandas as pd
import time
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo
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
                st.session_state.similar_apps = run_node_safe("SIMILAR", target_id, curr_country, "similar_apps.json") or []
                
                dev_target = d.get('developerId') or d.get('developer')
                
                if dev_target: 
                    st.session_state.dev_apps = run_node_safe("DEVELOPER", str(dev_target), curr_country, "developer_apps.json") or []
                else:
                    st.session_state.dev_apps = []
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

        # BẢNG MAPPING MÚI GIỜ CÁC QUỐC GIA PHỔ BIẾN
        # Bạn có thể bổ sung thêm nếu thiếu
        TZ_MAP = {
            # --- CHÂU Á ---
            'vn': 'Asia/Ho_Chi_Minh',   # Việt Nam
            'jp': 'Asia/Tokyo',         # Nhật Bản
            'kr': 'Asia/Seoul',         # Hàn Quốc
            'cn': 'Asia/Shanghai',      # Trung Quốc
            'tw': 'Asia/Taipei',        # Đài Loan
            'hk': 'Asia/Hong_Kong',     # Hồng Kông
            'sg': 'Asia/Singapore',     # Singapore
            'th': 'Asia/Bangkok',       # Thái Lan
            'id': 'Asia/Jakarta',       # Indonesia (Tây)
            'ph': 'Asia/Manila',        # Philippines
            'my': 'Asia/Kuala_Lumpur',  # Malaysia
            'in': 'Asia/Kolkata',       # Ấn Độ
            'pk': 'Asia/Karachi',       # Pakistan
            'bd': 'Asia/Dhaka',         # Bangladesh
            'sa': 'Asia/Riyadh',        # Ả Rập Xê Út
            'ae': 'Asia/Dubai',         # UAE
            'il': 'Asia/Jerusalem',     # Israel
            'tr': 'Europe/Istanbul',    # Thổ Nhĩ Kỳ

            # --- CHÂU MỸ ---
            'us': 'America/New_York',   # Hoa Kỳ (Bờ Đông)
            'ca': 'America/Toronto',    # Canada (Bờ Đông)
            'br': 'America/Sao_Paulo',  # Brazil
            'mx': 'America/Mexico_City',# Mexico
            'ar': 'America/Argentina/Buenos_Aires', # Argentina
            'cl': 'America/Santiago',   # Chile
            'co': 'America/Bogota',     # Colombia
            'pe': 'America/Lima',       # Peru

            # --- CHÂU ÂU ---
            'gb': 'Europe/London',      # Anh
            'de': 'Europe/Berlin',      # Đức
            'fr': 'Europe/Paris',       # Pháp
            'it': 'Europe/Rome',        # Ý
            'es': 'Europe/Madrid',      # Tây Ban Nha
            'ru': 'Europe/Moscow',      # Nga
            'nl': 'Europe/Amsterdam',   # Hà Lan
            'se': 'Europe/Stockholm',   # Thụy Điển
            'ch': 'Europe/Zurich',      # Thụy Sĩ
            'no': 'Europe/Oslo',        # Na Uy
            'dk': 'Europe/Copenhagen',  # Đan Mạch
            'fi': 'Europe/Helsinki',    # Phần Lan
            'pl': 'Europe/Warsaw',      # Ba Lan
            'ua': 'Europe/Kyiv',        # Ukraine
            'pt': 'Europe/Lisbon',      # Bồ Đào Nha
            'ro': 'Europe/Bucharest',   # Romania
            'cz': 'Europe/Prague',      # Séc
            'hu': 'Europe/Budapest',    # Hungary
            'be': 'Europe/Brussels',    # Bỉ
            'at': 'Europe/Vienna',      # Áo
            'ie': 'Europe/Dublin',      # Ireland

            # --- CHÂU ÚC & CHÂU PHI ---
            'au': 'Australia/Sydney',   # Úc
            'nz': 'Pacific/Auckland',   # New Zealand
            'za': 'Africa/Johannesburg',# Nam Phi
            'eg': 'Africa/Cairo',       # Ai Cập
            'ng': 'Africa/Lagos'        # Nigeria
        }

        # 3. Hiển thị Review (Card Chi Tiết) - ĐÃ CÓ TIMEZONE
        for r in filtered_revs:
            # --- HÀM XỬ LÝ NGÀY THÁNG THEO QUỐC GIA ---
            def format_date_by_country(iso_str, country_code):
                try:
                    if "T" in iso_str and "Z" in iso_str:
                        # 1. Parse giờ UTC gốc từ Google (Z = UTC)
                        dt_utc = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
                        
                        # 2. Lấy timezone đích dựa vào mã quốc gia (mặc định là UTC nếu không tìm thấy)
                        target_tz_name = TZ_MAP.get(country_code, 'UTC')
                        target_tz = ZoneInfo(target_tz_name)
                        
                        # 3. Chuyển đổi múi giờ
                        dt_local = dt_utc.astimezone(target_tz)
                        
                        # 4. Format: HH:MM ngày dd/mm/yyyy (Kèm tên múi giờ cho rõ)
                        # Ví dụ: 14:30 16/12/2025 (EST)
                        tz_abbr = dt_local.tzname() 
                        return f"{dt_local.strftime('%H:%M %d/%m/%Y')} ({tz_abbr})"
                    return iso_str
                except Exception:
                    return iso_str
            # ----------------------------------------------

            user_name = r.get('userName', 'Hidden User')
            avatar_char = user_name[0].upper() if user_name else "?"
            score = int(r.get('score', 0))
            stars = "⭐" * score
            
            # Xử lý text
            raw_text = r.get('text', '') or ''
            text = raw_text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            
            likes = r.get('thumbsUp', 0)
            version = r.get('version', '')
            
            # Gọi hàm format cho cả user date
            raw_date = r.get('date', '')
            date_display = format_date_by_country(raw_date, curr_country)

            reply_text = r.get('replyText')
            raw_reply_date = r.get('replyDate', '')
            
            # Convert giờ trả lời của Dev theo quốc gia
            reply_date_fmt = format_date_by_country(raw_reply_date, curr_country) if raw_reply_date else ""

            version_badge = f"<span class='rev-version'>v{version}</span>" if version else ""
            
            reply_html = ""
            if reply_text:
                safe_reply = reply_text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                reply_html = f"""
<div class="dev-reply-box">
<div class="dev-reply-header">
<span>👨‍💻 Developer Response</span>
<span>{reply_date_fmt}</span>
</div>
<div class="dev-reply-text">{safe_reply}</div>
</div>"""

            review_html = f"""
<div class="rev-container">
<div class="rev-header">
<div class="rev-user-info">
<div class="rev-avatar">{avatar_char}</div>
<div>
<div class="rev-name">{user_name}</div>
<div class="rev-date">{date_display}</div>
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
"""
            st.markdown(review_html, unsafe_allow_html=True)

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
        # 1. Video Section
        st.subheader("🎥 Video Trailer")
        
        video_url = d.get('video')
        if video_url:
            # Nếu có video -> Hiển thị
            st.video(video_url)
        else:
            # Nếu không có -> Báo rõ ràng cho người dùng biết
            st.info("🔕 Ứng dụng này không có Video giới thiệu.")
        
        st.divider()
        
        # 2. Screenshots Section
        st.subheader("🖼️ Screenshots")
        
        if d.get('screenshots'):
            st.caption("💡 Click ảnh để phóng to (Full màn hình).")
            # HTML Content cho Screenshot (Giữ nguyên logic Zoom cũ)
            html_content = '<div class="screenshot-scroll">'
            base_id = d.get('appId', 'app').replace('.', '_')
            
            for i, url in enumerate(d.get('screenshots')):
                unique_id = f"img_{base_id}_{i}"
                html_content += f"""<div style="display:inline-block;">
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
            st.markdown(html_content, unsafe_allow_html=True)
        else: 
            st.warning("📭 Không có ảnh chụp màn hình.")
    
    # --- TAB 3: DATA SAFETY (FULL VERSION) ---
    with tab3:
        ds = d.get('dataSafety', {})
        
        st.markdown("#### 🛡️ Cơ chế Bảo mật & Chính sách")
        
        sec_col, policy_col = st.columns([2, 1])
        
        with sec_col:
            practices = ds.get('securityPractices', [])
            if practices:
                html_sec = '<div class="security-box">'
                for p in practices:
                    practice_text = p.get('practice', '') if isinstance(p, dict) else str(p)
                    desc_text = p.get('description', '') if isinstance(p, dict) else ''
                    full_text = f"<b>{practice_text}</b>"
                    if desc_text: full_text += f": {desc_text}"
                    html_sec += f'<div class="sec-item"><span class="sec-icon">✔</span><div>{full_text}</div></div>'
                html_sec += '</div>'
                st.markdown(html_sec, unsafe_allow_html=True)
            else:
                # Nếu không có thông tin thì hiện box xám báo chưa rõ, thay vì ẩn đi
                st.warning("⚠️ Chưa có thông tin về quy trình mã hóa hoặc xóa dữ liệu.")
        with policy_col:
             privacy_url = d.get('privacyPolicy')
             if privacy_url:
                 st.info(f"📜 **Chính sách riêng tư**\n\n[Đọc tài liệu gốc tại đây]({privacy_url})")
             else:
                 st.error("❌ Không có Link chính sách.")
        st.divider()
        col_share, col_collect = st.columns(2)

        def render_safety_card(items, is_collected=False):
            if not items:
                # Nếu rỗng -> Hiển thị trạng thái "Sạch" (Màu xanh) nhìn sẽ tích cực hơn lỗi đỏ
                st.success("✅ Không có mục nào." if not is_collected else "✅ Không thu thập dữ liệu này.")
                return
            
            for item in items:
                data_name = item.get('data', 'Unknown Data')
                data_type = item.get('type', '')
                purpose = item.get('purpose', 'Chưa rõ mục đích')
                
                optional_badge = ""
                if is_collected:
                    is_optional = item.get('optional', False)
                    if is_optional:
                        optional_badge = "<span class='badge-opt'>Tùy chọn</span>"
                    else:
                        optional_badge = "<span class='badge-req'>Bắt buộc</span>"
                
                st.markdown(f"""
                <div class="data-item-card">
                    <div class="data-head">
                        <div>
                            <div class="data-name">{data_name}</div>
                            <div class="data-type">{data_type}</div>
                        </div>
                        {optional_badge}
                    </div>
                    <div class="data-purpose">🎯 <b>Mục đích:</b> {purpose}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_share:
            st.markdown("#### 📤 Dữ liệu chia sẻ")
            st.caption("Dữ liệu chia sẻ với bên thứ 3.")
            render_safety_card(ds.get('sharedData', []), is_collected=False)

        with col_collect:
            st.markdown("#### 📥 Dữ liệu thu thập")
            st.caption("Dữ liệu ứng dụng thu thập.")
            render_safety_card(ds.get('collectedData', []), is_collected=True)

        with tab4:
            current_id = d.get('appId')
            current_dev = d.get('developer', '').lower().strip()
            
            # [FIX QUAN TRỌNG] Lấy country_code ngay từ đầu để dùng cho cả if và else
            country_code = st.session_state.selected_app.get('country_override', 'vn')

            # 1. Kiểm tra dữ liệu đầu vào
            if not st.session_state.similar_apps:
                st.info("⚠️ Không tìm thấy danh sách ứng dụng tương tự từ Google Play.")
            else:
                # 2. Logic lọc: Bỏ chính nó và bỏ App cùng nhà phát triển
                real_competitors = []
                for s in st.session_state.similar_apps:
                    s_id = s.get('appId')
                    s_dev = s.get('developer', '').lower().strip()
                    
                    if s_id != current_id and (current_dev not in s_dev):
                        real_competitors.append(s)

                # 3. Hiển thị kết quả
                if real_competitors:
                    st.caption(f"🎯 Hiển thị **{len(real_competitors)}** đối thủ cạnh tranh (Đã lọc bỏ App cùng nhà phát hành).")
                    
                    cols = st.columns(3)
                    # (Dòng country_code cũ ở đây đã được đưa lên đầu rồi)
                    
                    for i, s in enumerate(real_competitors):
                        with cols[i % 3]:
                            render_mini_card(s, country_code, i, "sim")
                else:
                    # Trường hợp Google trả về data nhưng toàn là App cùng nhà -> Bị lọc hết
                    st.warning(f"⚠️ Google Play có gợi ý ứng dụng tương tự, nhưng tất cả đều thuộc cùng nhà phát triển '{d.get('developer')}'.")
                    
                    # Bây giờ country_code đã tồn tại, không còn lỗi nữa
                    with st.expander("Xem danh sách chưa lọc"):
                         cols_raw = st.columns(3)
                         for i, s in enumerate(st.session_state.similar_apps[:6]):
                             with cols_raw[i % 3]:
                                 render_mini_card(s, country_code, i, "raw_sim")
    
    # --- TAB 5: CÙNG DEV---
    with tab5:
        # 1. Kiểm tra có dữ liệu thô không
        if not st.session_state.dev_apps:
            st.info(f"📭 Không tìm thấy ứng dụng nào khác của **{d.get('developer')}**.")
        else:
            target_id = d.get('appId')
            
            # 2. Lọc bỏ chính ứng dụng đang xem
            other_apps = [dv for dv in st.session_state.dev_apps if dv.get('appId') != target_id]
            
            if other_apps:
                st.caption(f"📂 Tìm thấy **{len(other_apps)}** ứng dụng khác cùng nhà phát hành.")
                
                # Grid 3 cột
                cols = st.columns(3)
                # Lấy country code an toàn
                country_code = st.session_state.selected_app.get('country_override', 'vn')
                
                for i, dv in enumerate(other_apps):
                    with cols[i % 3]:
                        render_mini_card(dv, country_code, i, "dev")
            else:
                # Trường hợp danh sách trả về chỉ có duy nhất 1 app là chính nó
                st.warning(f"⚠️ Nhà phát triển **{d.get('developer')}** chỉ có duy nhất ứng dụng này trên cửa hàng.")

    # --- TAB 6: INFO (FULL UPDATE) ---
    with tab6:
        # Chuẩn bị dữ liệu
        dev_email = d.get('developerEmail') or "Không có Email"
        dev_web = d.get('developerWebsite')
        dev_addr = d.get('developerAddress') or "Không có địa chỉ"
        dev_id = d.get('developerId') or d.get('developer')
        
        # --- PHẦN 1: THÔNG SỐ KỸ THUẬT (GRID VIEW) ---
        st.markdown("#### 📱 Thông số kỹ thuật")
            
        specs = [
            {"label": "App ID", "val": d.get('appId'), "icon": "🆔", "color": "bg-blue"},
            {"label": "Phiên bản", "val": d.get('version') or 'Varies', "icon": "🚀", "color": "bg-green"},
            {"label": "Cập nhật", "val": format_date_by_country(d.get('updated', 0), curr_country) if d.get('updated') else 'N/A', "icon": "📅", "color": "bg-orange"},
            {"label": "Phát hành", "val": d.get('released') or 'N/A', "icon": "🎂", "color": "bg-pink"},
            {"label": "Android OS", "val": d.get('androidVersion') or 'Varies', "icon": "🤖", "color": "bg-teal"},
            {"label": "Độ tuổi", "val": d.get('contentRating') or 'Unrated', "icon": "🔞", "color": "bg-red"},
            {"label": "Dung lượng", "val": d.get('size') or 'Varies', "icon": "💾", "color": "bg-purple"},
            {"label": "Thể loại", "val": d.get('genre'), "icon": "🎮", "color": "bg-cyan"},
        ]
        # Tạo HTML từ danh sách trên
        cards_html = ""
        for s in specs:
            cards_html += f"""
<div class="tech-card">
<div class="tc-icon-box {s['color']}">{s['icon']}</div>
<div class="tc-content">
<span class="tc-label">{s['label']}</span>
<span class="tc-value" title="{s['val']}">{s['val']}</span>
</div>
</div>
"""
            
            # Render Grid
            final_html = f'<div class="tech-grid">{cards_html}</div>'
            st.markdown(final_html, unsafe_allow_html=True)
        
        # --- PHẦN 2: THÔNG TIN DEVELOPER ---
        st.markdown("#### 🏢 Nhà phát triển (Developer)")
        
        # Xây dựng HTML Contact
        web_link = f'<a href="{dev_web}" target="_blank">{dev_web}</a>' if dev_web else "Không có Website"
        email_link = f'<a href="mailto:{dev_email}">{dev_email}</a>'
        
        dev_html = f"""
        <div class="dev-contact-card">
            <div class="dev-row"><span class="dev-icon">🆔</span> <b>ID:</b> &nbsp; {dev_id}</div>
            <div class="dev-row"><span class="dev-icon">📧</span> <b>Email:</b> &nbsp; {email_link}</div>
            <div class="dev-row"><span class="dev-icon">🌐</span> <b>Web:</b> &nbsp; {web_link}</div>
            <div class="dev-row"><span class="dev-icon">📍</span> <b>Address:</b> &nbsp; {dev_addr}</div>
        </div>
        """
        st.markdown(dev_html, unsafe_allow_html=True)
        
        # --- PHẦN 3: MÔ TẢ & LIÊN KẾT KHÁC ---
        c_desc, c_link = st.columns([2, 1])
        
        with c_desc:
            st.markdown("#### 📝 Mô tả ứng dụng")
            # Dùng expander để không chiếm hết màn hình nếu mô tả quá dài
            with st.expander("Xem toàn bộ mô tả (Description)", expanded=True):
                desc_html = d.get('descriptionHTML') or d.get('description') or "Không có mô tả."
                st.markdown(f'<div class="desc-container">{desc_html}</div>', unsafe_allow_html=True)
                
        with c_link:
            st.markdown("#### 🔗 Liên kết")
            if d.get('privacyPolicy'):
                st.link_button("🛡️ Chính sách riêng tư", d.get('privacyPolicy'), use_container_width=True)
            
            st.link_button("🌍 Xem trên Google Play Store", d.get('url'), use_container_width=True)
            
            if d.get('recentChanges'):
                st.info(f"**🆕 Có gì mới:**\n\n{d.get('recentChanges')}")
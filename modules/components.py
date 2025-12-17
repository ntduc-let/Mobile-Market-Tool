# modules/components.py
import streamlit as st

def render_mini_card(app, country, rank_idx, key_prefix, theme_color="#fff"):
    # Lấy dữ liệu an toàn
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/80'
    title = app.get('title', 'Unknown')
    publisher = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    price = app.get('price', 0)
    
    rank = rank_idx + 1
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    
    # Store URL
    store_url = f"https://play.google.com/store/apps/details?id={app_id_safe}&hl={country}"

    # Style động
    rank_style = f"color: {theme_color};"
    border_style = f"border-left: 5px solid {theme_color};" # Viền dày hơn chút
    price_text = "Free" if price == 0 else f"{price:,.0f} đ"

    # --- HTML CONTENT (CHỈ CHỨA INFO, KHÔNG CHỨA BUTTON CHI TIẾT) ---
    # Nút Store giờ là một link nhỏ gọn gàng bên cạnh giá/điểm
    html_content = f"""
    <div class="app-card-optimized" style="{border_style}">
        <div class="rank-badge" style="{rank_style}">#{rank}</div>
        <img src="{icon_url}" class="app-icon-opt">
        <div class="app-info-col">
            <div class="app-title-opt" title="{title}">{title}</div>
            <div class="app-dev-opt">{publisher}</div>
            <div class="meta-tags">
                <span class="meta-pill score">⭐ {score:.1f}</span>
                <span class="meta-pill price">{price_text}</span>
                <a href="{store_url}" target="_blank" class="store-link-small">
                    🌍 Google Play
                </a>
            </div>
        </div>
    </div>
    """
    
    # --- LAYOUT RENDER ---
    # Chia làm 2 cột: 
    # Cột 1 (85%): Hiển thị Card thông tin (HTML)
    # Cột 2 (15%): Hiển thị nút bấm "Chi tiết" (Streamlit Button)
    
    c_info, c_btn = st.columns([0.82, 0.18]) 
    
    with c_info:
        st.markdown(html_content, unsafe_allow_html=True)
        
    with c_btn:
        # Hack CSS để căn giữa nút bấm theo chiều dọc so với card bên cạnh
        # (Thêm khoảng trắng phía trên nút để đẩy nó xuống giữa)
        st.markdown('<div style="height: 35px;"></div>', unsafe_allow_html=True)
        
        unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
        # Dùng icon mũi tên hoặc kính lúp để nút gọn và đẹp
        if st.button("🔍 Xem", key=unique_key, use_container_width=True):
            st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
            st.session_state.view_mode = 'detail'
            st.rerun()
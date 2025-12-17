# modules/components.py
import streamlit as st

def render_mini_card(app, country, rank_idx, key_prefix, theme_color="#fff"):
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/80'
    title = app.get('title', 'Unknown')
    publisher = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    price = app.get('price', 0)
    
    rank = rank_idx + 1
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    store_url = f"https://play.google.com/store/apps/details?id={app_id_safe}&hl={country}"
    
    rank_style = f"color: {theme_color};"
    border_style = f"border-left: 5px solid {theme_color};"
    price_text = "Free" if price == 0 else f"{price:,.0f} đ"

    # HTML INFO
    html_top = f"""
    <div class="app-card-top" style="{border_style}">
        <div class="rank-badge" style="{rank_style}">#{rank}</div>
        <img src="{icon_url}" class="app-icon-opt">
        <div class="app-info-col">
            <div class="app-title-opt" title="{title}">{title}</div>
            <div class="app-dev-opt">{publisher}</div>
            <div class="meta-tags">
                <span class="meta-pill score">⭐ {score:.1f}</span>
                <span class="meta-pill price">{price_text}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_top, unsafe_allow_html=True)

    # BUTTONS - Dùng gap="small" để 2 nút tách nhau ra
    c1, c2 = st.columns(2, gap="small")
    
    with c1:
        # Nút Trái -> CSS sẽ tự biến thành màu Xanh (Google Play)
        st.link_button("🌍 Google Play", store_url, use_container_width=True)
        
    with c2:
        # Nút Phải -> CSS sẽ tự biến thành màu Vàng (Chi tiết)
        unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
        if st.button("🔍 Chi tiết", key=unique_key, use_container_width=True):
            st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
            st.session_state.view_mode = 'detail'
            st.rerun()
            
    # Thêm khoảng trống nhỏ cuối mỗi card để không bị dính vào card tiếp theo
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
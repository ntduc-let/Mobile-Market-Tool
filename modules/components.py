# Trong file modules/components.py
import streamlit as st

def render_mini_card(app, country, rank_idx, key_prefix, theme_color="#fff"):
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/64'
    title = app.get('title', 'Unknown')
    publisher = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    price = app.get('price', 0)
    
    # Dữ liệu mở rộng (Nếu có thì hiện, không thì hiện N/A hoặc ẩn)
    # Lưu ý: List scraper mặc định chưa có 'reviews' và 'updated', ta cứ để placeholder
    reviews_count = app.get('reviews', 0) 
    updated_at = app.get('updated', None) # Dạng timestamp hoặc string
    
    rank = rank_idx + 1
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    
    # Tạo link Store
    store_url = f"https://play.google.com/store/apps/details?id={app_id_safe}&hl={country}"

    # CSS động cho màu rank
    rank_style = f"color: {theme_color};"
    border_style = f"border-left: 4px solid {theme_color};"

    # Xử lý hiển thị giá
    price_text = "Free" if price == 0 else f"{price:,.0f} đ"

    # --- RENDER HTML CARD ---
    st.markdown(f"""
    <div class="app-card-optimized" style="{border_style}">
        <div class="rank-badge" style="{rank_style}">#{rank}</div>
        
        <img src="{icon_url}" class="app-icon-opt">
        
        <div class="app-info-col">
            <div class="app-title-opt" title="{title}">{title}</div>
            <div class="app-dev-opt">{publisher}</div>
            
            <div class="meta-tags">
                <span class="meta-tag score">⭐ {score:.1f}</span>
                <span class="meta-tag price">🏷️ {price_text}</span>
                </div>
        </div>

        <div class="app-actions-col">
            <a href="{store_url}" target="_blank" class="btn-store">
                🌍 Store
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nút Chi tiết (Streamlit Button) - Đặt bên ngoài HTML để giữ logic Python
    # Dùng columns để căn chỉnh nút này khớp với cột Actions bên phải
    c1, c2, c3, c4 = st.columns([40, 64, 200, 80]) # Tỷ lệ tương đối
    with c4: 
        unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
        if st.button("🔍 Chi tiết", key=unique_key, use_container_width=True):
            st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
            st.session_state.view_mode = 'detail'
            st.rerun()
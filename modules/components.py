import streamlit as st

def render_mini_card(app, country, rank_idx, key_prefix, theme_color="#fff"):
    icon_url = app.get('icon', '')
    title = app.get('title', 'Unknown')
    publisher = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    
    # Xử lý giá
    raw_price = app.get('price')
    try:
        price = float(raw_price) if raw_price is not None else 0
    except: price = 0
    price_text = "FREE" if price == 0 else f"{price:,.0f} đ"
    
    rank = rank_idx + 1
    app_id = app.get('app_id') or app.get('appId') or f"u_{rank}"

    # Style màu sắc cho Rank (Top 1,2,3 nổi bật hơn)
    rank_color = "#ffd700" if rank == 1 else "#c0c0c0" if rank == 2 else "#cd7f32" if rank == 3 else "var(--text-secondary)"

    # HTML Card tối giản
    html = f"""
    <div class="app-card-top">
        <div class="rank-badge" style="color: {rank_color};">#{rank}</div>
        <img src="{icon_url}" class="app-icon-opt" loading="lazy">
        <div class="app-info-col">
            <div class="app-title-opt" title="{title}">{title}</div>
            <div class="app-dev-opt">{publisher}</div>
            <div class="meta-tags">
                <span class="meta-pill">⭐ {score:.1f}</span>
                <span class="meta-pill" style="color: {'#3fb950' if price==0 else '#d29922'}">{price_text}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # Nút bấm ẩn (invisible but clickable area) hoặc nút nhỏ gọn
    # Ở đây em dùng st.button full width nhưng style CSS ở trên đã làm nó trong suốt và tinh tế
    if st.button("Chi tiết", key=f"btn_{key_prefix}_{rank}_{app_id}", use_container_width=True):
        st.session_state.selected_app = {'app_id': app_id, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()
    
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
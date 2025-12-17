# modules/components.py
import streamlit as st

def render_mini_card(app, country, rank_idx, key_prefix, theme_color="#fff"):
    icon_url = app.get('icon', '') or 'https://via.placeholder.com/64'
    title = app.get('title', 'Unknown')
    publisher = app.get('developer', 'Unknown')
    score = app.get('score', 0)
    rank = rank_idx + 1
    app_id_safe = app.get('app_id') or app.get('appId') or f"unknown_{rank}"
    
    card_style = f"border-left: 4px solid {theme_color};"
    rank_style = f"color: {theme_color};"

    st.markdown(f"""
    <div class="app-card-optimized" style="{card_style}">
        <div class="rank-badge" style="{rank_style}">#{rank}</div>
        <img src="{icon_url}" class="app-icon-opt">
        <div class="app-info-opt">
            <div class="app-title-opt" title="{title}">{title}</div>
            <div class="app-dev-opt">{publisher}</div>
            <div class="app-meta-row">
                <span style="color:#ffbd45; font-weight:bold;">★ {score:.1f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    unique_key = f"btn_{key_prefix}_{rank}_{app_id_safe}"
    if st.button("🔍 Chi tiết", key=unique_key, use_container_width=True):
        st.session_state.selected_app = {'app_id': app_id_safe, 'title': title, 'country_override': country}
        st.session_state.view_mode = 'detail'
        st.rerun()
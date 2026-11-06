import streamlit as st

registration_page = st.Page(
    "registration.py",
    title="Student Registration",
    url_path="",
    default=True,
)

players_page = st.Page(
    "player.py",
    title="Registered Players",
    url_path="player",
)

admin_page = st.Page(
    "admin.py",
    title="Admin",
    url_path="admin",
)

pg = st.navigation(
    [registration_page, players_page,admin_page],
    position="hidden",
)

pg.run()
import streamlit as st

registration_page = st.Page(
    "registration.py",
    title="Student Registration",
    url_path="",
    default=True,
)

player_page = st.Page(
    "player.py",
    title="Registered Players",
    url_path="player",
)

pg = st.navigation(
    [registration_page, player_page],
    position="hidden",
)

pg.run()
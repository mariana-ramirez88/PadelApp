import streamlit as st
from PIL import Image

def sidebar_style():

    sidebar_bg = """
    <style>
        /* Target all sidebar titles with class starting with e1dbuyne */
        [class^="st-emotion-cache"][class*="e1dbuyne"] {
            color: #5E3187;
            font-weight: bold;
            font-size: 20px;
        }
        </style>
    """

    logo = Image.open("assets/logo_playzone_purple.jpg")
    st.markdown(sidebar_bg, unsafe_allow_html=True)
    with st.sidebar:
        st.image(logo)
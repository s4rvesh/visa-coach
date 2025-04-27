import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        body, .stApp { background-color: #FFFFFF; color: #000000; }
        .block-container { padding-top: 2rem; max-width: 900px; margin: auto; background-color: #FFFFFF; }
        .user-bubble { background-color: #007BFF; color: #FFFFFF; padding: 12px; border-radius: 10px; margin-bottom: 10px; font-size: 16px; }
        .bot-bubble { background-color: #D4EDDA; color: #000000; padding: 12px; border-radius: 10px; margin-bottom: 10px; font-size: 16px; }
        .stButton>button { background-color: #007BFF; color: white; font-size: 16px; padding: 10px 24px; border-radius: 10px; border: none; margin-top: 20px; }
        .stButton>button:hover { background-color: #0056b3; }
        input { background-color: #F0F0F5 !important; color: #000000 !important; border: 1px solid #CCCCCC !important; border-radius: 8px !important; padding: 12px !important; font-size: 16px !important; }
        input::placeholder { color: #666666 !important; opacity: 1 !important; }
        h1 { color: #000000; text-align: center; font-size: 2.5rem; margin-bottom: 2rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

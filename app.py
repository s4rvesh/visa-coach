import os
import time
import streamlit as st
from dotenv import load_dotenv
from model import load_model

load_dotenv()

# Setup Streamlit
st.set_page_config(page_title="Visa Coach - SJSU", page_icon="🧳", layout="wide")

# Custom CSS
st.markdown("""
<style>
body, .stApp { background-color: #FFFFFF; color: #000000; }
.block-container { padding-top: 2rem; max-width: 900px; margin: auto; }
.user-bubble {
    background-color: #007BFF; color: white; padding: 12px; border-radius: 10px;
    margin-bottom: 10px; font-size: 16px;
}
.bot-bubble {
    background-color: #D4EDDA; color: black; padding: 12px; border-radius: 10px;
    margin-bottom: 10px; font-size: 16px;
}
.stButton>button {
    background-color: #007BFF; color: white; font-size: 16px;
    padding: 10px 24px; border-radius: 10px; border: none; margin-top: 20px;
}
input {
    background-color: #F0F0F5 !important; color: black !important;
    border: 1px solid #CCCCCC !important; border-radius: 8px !important;
    padding: 12px !important; font-size: 16px !important;
}
input::placeholder { color: #666666 !important; opacity: 1 !important; }
h1 { color: #000000; text-align: center; font-size: 2.5rem; }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("<h1>🎓 VisaCoach for SJSU Students</h1>", unsafe_allow_html=True)

# Spinner
with st.spinner('Loading VisaCoach...'):
    time.sleep(1.0)

# Load the RAG chain
qa_chain = load_model()

# User Input
query = st.text_input("Ask your question about CPT, OPT, SEVIS, etc:")

if query and query.strip():
    st.markdown(f"<div class='user-bubble'><b>You:</b> {query}</div>", unsafe_allow_html=True)

    with st.spinner("VisaCoach is thinking..."):
        result = qa_chain.invoke(query)

    st.markdown(f"<div class='bot-bubble'><b>VisaCoach:</b><br>{result['result']}</div>", unsafe_allow_html=True)
    st.caption("⚠️ Disclaimer: Always verify with your ISSS Advisor for final approval.")

    st.markdown("### 🔗 Sources")
    for doc in result["source_documents"]:
        st.markdown(f"- [{doc.metadata['source']}]({doc.metadata['source']})")

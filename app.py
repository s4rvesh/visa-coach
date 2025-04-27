import os
import time
import streamlit as st
from dotenv import load_dotenv
from model import load_model
from utils import reset_session, is_query_vague
from style import apply_custom_styles

load_dotenv()

# Setup page
st.set_page_config(page_title="Visa Coach - SJSU", page_icon="🧳", layout="wide")
apply_custom_styles()

# Spinner at page load
with st.spinner('Loading VisaCoach...'):
    time.sleep(1.5)

# Title
st.markdown("<h1>🎓 VisaCoach for SJSU Students</h1>", unsafe_allow_html=True)

# Load the model
qa_chain = load_model(
    model_name="google/flan-t5-base", 
    temperature=0.3, 
    max_new_tokens=512
)

# Chat logic
if "question_submitted" not in st.session_state:
    st.session_state["question_submitted"] = False

if not st.session_state["question_submitted"]:
    st.markdown("<h3 style='color: black;'>Ask a question about CPT, OPT, SEVIS, etc:</h3>", unsafe_allow_html=True)
    query = st.text_input(label="", placeholder="Type your question here...")
    if query and query.strip():
        st.session_state["original_query"] = query
        st.session_state["question_submitted"] = True
        st.rerun()

if st.session_state["question_submitted"]:
    query = st.session_state["original_query"]

    st.markdown(f"<div class='user-bubble'><b>You:</b> {query}</div>", unsafe_allow_html=True)

    if is_query_vague(query):
        if "clarification_given" not in st.session_state:
            st.session_state["clarification_given"] = False

        if not st.session_state["clarification_given"]:
            st.markdown("<h3 style='color: black;'>🤔 Could you please clarify your question a bit more?</h3>", unsafe_allow_html=True)
            clarification = st.text_input(label="", placeholder="For example: 'second semester, part-time CPT'")
            if clarification and clarification.strip():
                st.session_state["clarification"] = clarification
                st.session_state["clarification_given"] = True
                st.rerun()

        if st.session_state["clarification_given"]:
            clarification = st.session_state["clarification"]
            st.markdown(f"<div class='user-bubble'><b>You (Clarification):</b> {clarification}</div>", unsafe_allow_html=True)
            full_query = query + " " + clarification
            with st.spinner('VisaCoach is thinking...'):
                st.session_state["result"] = qa_chain.invoke(full_query)
    else:
        with st.spinner('VisaCoach is thinking...'):
            st.session_state["result"] = qa_chain.invoke(query)

    if "result" in st.session_state:
        st.markdown(f"<div class='bot-bubble'><b>VisaCoach:</b><br>{st.session_state['result']['result']}</div>", unsafe_allow_html=True)
        st.caption("⚠️ Disclaimer: Always verify with your ISSS Advisor for final approval.")

        st.markdown("### 🔗 Sources")
        for doc in st.session_state['result']['source_documents']:
            st.markdown(f"- [{doc.metadata['source']}]({doc.metadata['source']})")

    if st.button("💬 Ask another question"):
        reset_session()
        st.rerun()

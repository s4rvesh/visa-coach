import os
import time
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub
import pandas as pd
from datetime import datetime

load_dotenv()

# Helper functions
def is_query_vague(text):
    key_keywords = ["semester", "full-time", "part-time", "paid", "unpaid", "first", "second", "final", "graduate", "credit", "course"]
    return not any(word in text.lower() for word in key_keywords)

def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Streamlit page config
st.set_page_config(page_title="Visa Coach - SJSU", page_icon="🧳", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
        margin: auto;
        background-color: #FFFFFF;
    }
    .user-bubble {
        background-color: #007BFF;
        color: #FFFFFF;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 16px;
    }
    .bot-bubble {
        background-color: #D4EDDA;
        color: #000000;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 16px;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 10px;
        border: none;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    input {
        background-color: #F0F0F5 !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    input::placeholder {
        color: #666666 !important;
        opacity: 1 !important;
    }
    h1 {
        color: #000000;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Spinner at page load
with st.spinner('Loading VisaCoach...'):
    time.sleep(1.5)

# Title
st.markdown("<h1>🎓 VisaCoach for SJSU Students</h1>", unsafe_allow_html=True)

# Load model and vectorstore
huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

qa_chain = RetrievalQA.from_chain_type(
    llm=HuggingFaceHub(
        repo_id="google/flan-t5-large",
        huggingfacehub_api_token=huggingfacehub_api_token,
        model_kwargs={"temperature": 0.3, "max_new_tokens": 512}
    ),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
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

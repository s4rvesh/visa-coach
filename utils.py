def reset_session():
    import streamlit as st
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def is_query_vague(text):
    key_keywords = ["semester", "full-time", "part-time", "paid", "unpaid", "first", "second", "final", "graduate", "credit", "course"]
    return not any(word in text.lower() for word in key_keywords)

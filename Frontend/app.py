import streamlit as st
import requests
import json
import pandas as pd

S_URL = "https://single-agent-with-multi-tools.onrender.com"

st.title("Single Agent Multi Tools")

w_tab, s_tab, web_tab = st.tabs([
    "Weather_Tool", "SQL Tool", "Web Tool"
])


def safe_post(endpoint, params):
    res = requests.post(f"{S_URL}{endpoint}", params=params)

    if res.status_code != 200:
        return None, res.text

    return res.json(), None


def get_final_answer(obj):
    messages = obj.get("messages", [])

    if len(messages) == 0:
        return ""

    return messages[-1].get("content", "")


with web_tab:
    question = st.text_input("Ask a general question ")

    if st.button("GetGenData"):
        obj, error = safe_post("/web_tool_calling", {
            "question": question
        })

        if error:
            st.error("Backend Error")
            st.write(error)
        else:
            answer = get_final_answer(obj)
            st.write(answer)


with s_tab:
    question = st.text_input("Ask a sql question ")

    if st.button("GetData"):
        obj, error = safe_post("/sql_tool_calling", {
            "question": question
        })

        if error:
            st.error("Backend Error")
            st.write(error)
        else:
            answer = get_final_answer(obj)
            st.write(answer)


with w_tab:
    st.title("🌤 AI Weather Agent")

    city = st.text_input("Enter City")

    question = st.text_input("Ask Your Weather Question")

    if st.button("Ask Agent"):
        obj, error = safe_post("/tool_calling", {
            "city": city,
            "question": question
        })

        if error:
            st.error("Backend Error")
            st.write(error)
        else:
            answer = get_final_answer(obj)
            st.write(answer)
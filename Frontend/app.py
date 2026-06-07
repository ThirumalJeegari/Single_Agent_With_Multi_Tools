import streamlit as st
import requests
import json
import pandas as pd

S_URL = "http://127.0.0.1:8000"

w_tab, s_tab, web_tab = st.tabs([
    "Weather Tool",
    "SQL Tool",
    "Web Tool"
])



with web_tab:

    st.title("🌐 AI Web Search Agent")

    question = st.text_input(
        "Ask a general question"
    )

    if st.button("GetGenData"):

        res = requests.post(
            f"{S_URL}/web_tool_calling",
            params={
                "question": question
            }
        )

        obj = res.json()

        st.json(obj)



with s_tab:

    st.title("🗄 AI SQL Agent")

    question = st.text_input(
        "Ask a SQL question"
    )

    if st.button("GetData"):

        res = requests.post(
            f"{S_URL}/sql_tool_calling",
            params={
                "question": question
            }
        )

        obj = res.json()

        try:
            messages = obj["messages"][2]["content"]

            emps = json.loads(messages)

            st.write(emps)

            df = pd.DataFrame(emps)

            st.dataframe(df)

        except Exception as e:
            st.error(f"Error : {e}")
            st.json(obj)



with w_tab:

    st.title("🌤 AI Weather Agent")

    city = st.text_input(
        "Enter City"
    )

    question = st.text_input(
        "Ask Your Weather Question"
    )

    if st.button("Ask Agent"):

        res = requests.post(
            f"{S_URL}/tool_calling",
            params={
                "city": city,
                "question": question
            }
        )

        objRes = res.json()

        try:
            messages = objRes["messages"][2]["content"]

            obj = json.loads(messages)

            st.write("### Weather Details")
            st.write(obj["main"])

        except Exception as e:
            st.error(f"Error : {e}")
            st.json(objRes)
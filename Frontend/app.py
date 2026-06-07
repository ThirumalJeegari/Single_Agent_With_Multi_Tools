import streamlit as st
import requests
import json
import pandas as pd
S_URL = "http://127.0.0.1:8000"

w_tab ,s_tab, web_tab=st.tabs([
    "Weather_Tool","SQL Tool","Web Tool"
])

with web_tab:
    question=st.text_input("Ask a general question ")

    if st.button("GetGenData"):
        res=requests.post(f"{S_URL}/web_tool_calling",params={
            "question":question
        })

        st.write(res)
        


with s_tab:
    question=st.text_input("Ask a sql question ")

    if st.button("GetData"):
        res=requests.post(f"{S_URL}/sql_tool_calling",params={
            "question":question
        })

        obj=res.json()
        messages=obj["messages"][2]["content"]
        emps = json.loads(messages)
        st.write(emps)
        df=pd.DataFrame(emps)
        st.dataframe(df)

with w_tab:
    
    st.title("🌤 AI Weather Agent")

    city = st.text_input(
        "Enter City"
    )

    question = st.text_input(
        "Ask Your Weather Question"
    )

    if st.button("Ask Agent"):
        res=requests.post(f"{S_URL}/tool_calling",params={
            "city":city,
            "question":question
        })
        objRes=res.json()
        messages=objRes["messages"][2]["content"]
        obj=json.loads(messages)
        st.write(obj["main"])
        # st.write(messages)
        # st.write(res.json()["messages"][2]["content"])
        st.write(res.json()["messages"][3]["content"])

        # st.success(res.json()["messages"][-1]["content"])
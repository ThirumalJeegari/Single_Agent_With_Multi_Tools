import streamlit as st
import requests
import json
import pandas as pd

S_URL = "https://single-agent-with-multi-tools.onrender.com"

w_tab, s_tab, web_tab = st.tabs([
    "Weather_Tool", "SQL Tool", "Web Tool"
])


def safe_post(endpoint, params):
    res = requests.post(f"{S_URL}{endpoint}", params=params)

    if res.status_code != 200:
        return None, res.text

    try:
        return res.json(), None
    except Exception:
        return None, res.text


def get_tool_content(obj, tool_name):
    messages = obj.get("messages", [])

    for msg in messages:
        if msg.get("name") == tool_name:
            return msg.get("content")

    return None


def get_final_answer(obj):
    messages = obj.get("messages", [])

    if len(messages) == 0:
        return ""

    return messages[-1].get("content", "")


def parse_json_content(content):
    if content is None:
        return None

    if isinstance(content, list) or isinstance(content, dict):
        return content

    try:
        return json.loads(content)
    except Exception:
        return content


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
            st.write(get_final_answer(obj))

            web_content = get_tool_content(obj, "web_tool")
            web_data = parse_json_content(web_content)

            st.json(web_data)


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
            st.write(get_final_answer(obj))

            sql_content = get_tool_content(obj, "sql_tool")
            emps = parse_json_content(sql_content)

            st.write(emps)

            if isinstance(emps, list):
                df = pd.DataFrame(emps)
                st.dataframe(df)
            else:
                st.write(emps)


with w_tab:

    st.title("🌤 AI Weather Agent")

    city = st.text_input(
        "Enter City"
    )

    question = st.text_input(
        "Ask Your Weather Question"
    )

    if st.button("Ask Agent"):
        obj, error = safe_post("/tool_calling", {
            "city": city,
            "question": question
        })

        if error:
            st.error("Backend Error")
            st.write(error)
        else:
            weather_content = get_tool_content(obj, "get_temp_details")
            weather_data = parse_json_content(weather_content)

            if isinstance(weather_data, dict):
                if "main" in weather_data:
                    st.write(weather_data["main"])

                st.json(weather_data)
            else:
                st.write(weather_data)

            st.write(get_final_answer(obj))
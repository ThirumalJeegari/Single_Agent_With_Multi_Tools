import streamlit as st
import requests
import json
import pandas as pd

S_URL = "https://single-agent-with-multi-tools.onrender.com"



def safe_json_response(res):
    try:
        return res.json()
    except Exception:
        st.error("Backend did not return JSON")
        st.write("Status Code:", res.status_code)
        st.write("Backend Response:")
        st.code(res.text)
        st.stop()

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

        obj = safe_json_response(res)

        try:
            answer = obj["messages"][-1]["content"]
            st.write("### Web Search Result")
            st.write(answer)

        except Exception as e:
            st.error(f"Error : {e}")
            st.json(obj)

            
@app.get("/test_db")
def test_db():
    try:
        con_obj = get_db_connection()
        cursor = con_obj.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_employees FROM employees")
        result = cursor.fetchone()

        cursor.close()
        con_obj.close()

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


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

        objRes = safe_json_response(res)

        
        messages = objRes["messages"][2]["content"]

        obj = json.loads(messages)

        st.write("### Weather Details")

        st.write(
            f"Temperature is {obj['main']['temp']}°C. "
            f"It feels like {obj['main']['feels_like']}°C. "
            f"Humidity is {obj['main']['humidity']}%. "
            f"Pressure is {obj['main']['pressure']} hPa."
        )
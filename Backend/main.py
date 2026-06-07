from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
import mysql.connector
import requests
import os
import json
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@app.get("/")
def home():
    return {
        "message": "Backend Running Successfully"
    }


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE", "agents"),
        password=os.getenv("MYSQL_PASSWORD")
    )


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("api_key") or os.getenv("GROQ_API_KEY")
)


client = TavilyClient(
    api_key=os.getenv("tavily_api_key") or os.getenv("TAVILY_API_KEY")
)


@tool
def get_temp_details(city: str):
    """
    this is to get city details
    """
    try:
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        data = res.json()
        return data

    except Exception as e:
        return {
            "error": str(e)
        }

@tool
def sql_tool(query: str):
    """
    Execute a MySQL SELECT query.

    Important:
    - Input must be only one argument: query
    - Do not pass username
    - Do not pass password
    - Do not pass host
    - Do not pass database name
    Example input: SELECT * FROM employees
    """

    try:
        clean_query = query.strip()

        if not clean_query.lower().startswith("select"):
            return [
                {
                    "error": "Only SELECT queries are allowed"
                }
            ]

        con_obj = get_db_connection()

        cursor = con_obj.cursor(dictionary=True)
        cursor.execute(clean_query)

        allEmps = cursor.fetchall()

        cursor.close()
        con_obj.close()

        return allEmps

    except Exception as e:
        return [
            {
                "error": str(e)
            }
        ]

@tool
def web_tool(question: str):
    """
    web search
    """
    try:
        result = client.search(
            query=question,
            max_results=5
        )

        return result

    except Exception as e:
        return {
            "error": str(e)
        }


agent = create_agent(
    model=llm,
    tools=[get_temp_details, sql_tool, web_tool]
)


def make_json_safe(result):
    safe_messages = []

    for msg in result["messages"]:
        content = msg.content

        try:
            json.dumps(content)
        except Exception:
            content = str(content)

        safe_messages.append({
            "type": msg.__class__.__name__,
            "content": content,
            "name": getattr(msg, "name", None)
        })

    return {
        "messages": safe_messages
    }


@app.post("/web_tool_calling")
def incoming_web_search_(question: str = Query(...)):
    try:
        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"question:{question}"
                }
            ]
        })

        return make_json_safe(result)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


@app.post("/tool_calling")
def incoming_weather_params(
    city: str = Query(...),
    question: str = Query(...)
):
    try:
        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"city:{city} question:{question}"
                }
            ]
        })

        return make_json_safe(result)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )

@app.post("/sql_tool_calling")
def sql_tool_calling_function(question: str = Query(...)):

    try:
        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""
You are a SQL assistant.

Your task:
1. Convert the user question into a MySQL SELECT query.
2. Call sql_tool with only this format:
   sql_tool(query="SELECT ...")

Rules:
- Do not pass username.
- Do not pass password.
- Do not pass host.
- Do not pass database.
- The database connection is already handled inside sql_tool.
- Use only SELECT queries.
- Table name is employees.

User question: {question}
"""
                }
            ]
        })

        return make_json_safe(result)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )
from fastapi import FastAPI, Query
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
import mysql.connector
import requests
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("api_key")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        database=os.getenv("MYSQL_DATABASE"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)


client = TavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
def get_temp_details(city: str):
    """
    Get current weather details for a city using OpenWeather API.
    """

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    res = requests.get(url)
    data = res.json()

    return data


@tool
def sql_tool(query: str):
    """
    Fetch details from MySQL database.
    Only SELECT queries are allowed.
    """

    if not query.strip().lower().startswith("select"):
        return {"error": "Only SELECT queries are allowed"}

    con_obj = get_db_connection()
    cursor = con_obj.cursor(dictionary=True)

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    con_obj.close()

    return result


@tool
def web_tool(question: str):
    """
    Search the web using Tavily.
    """

    result = client.search(
        query=question,
        max_results=5
    )

    return result


agent = create_agent(
    model=llm,
    tools=[get_temp_details, sql_tool, web_tool]
)


@app.get("/")
def home():
    return {
        "message": "Single Agent With Multiple Tools Backend Running Successfully"
    }


@app.post("/web_tool_calling")
def incoming_web_search(question: str = Query(...)):

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Use web_tool and answer this question: {question}"
            }
        ]
    })

    return result


@app.post("/tool_calling")
def incoming_weather_params(
    city: str = Query(...),
    question: str = Query(...)
):

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"City: {city}. Question: {question}. Use weather tool if needed."
            }
        ]
    })

    return result


@app.post("/sql_tool_calling")
def sql_tool_calling_function(question: str = Query(...)):

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Convert this user question into a safe SELECT SQL query and use sql_tool: {question}"
            }
        ]
    })

    return result
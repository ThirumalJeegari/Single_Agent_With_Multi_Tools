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


con_obj = mysql.connector.connect(
    host="localhost",
    user="root",
    database="agents",
    password="10000Coders"
)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("api_key")
)


# minor change: Tavily client moved here
client = TavilyClient(
    api_key=os.getenv("tavily_api_key")
)


@tool
def get_temp_details(city: str):
    """
    this is to get city details
    """
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}"
    )

    data = res.json()
    return data


@tool
def sql_tool(query: str):
    """
    this query is to fetch details from db
    """
    cursor = con_obj.cursor(dictionary=True)
    cursor.execute(query)

    allEmps = cursor.fetchall()

    return allEmps


@tool
def web_tool(question: str):
    """
    web search
    """
    result = client.search(
        query=question,
        max_results=5   # minor change: max_limit changed to max_results
    )

    return result


agent = create_agent(
    model=llm,
    tools=[get_temp_details, sql_tool, web_tool]
)


@app.post("/web_tool_calling")
def incoming_web_search_(question: str = Query(...)):
    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"question:{question}"
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
                "content": f"city:{city} question:{question}"
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
                "content": f"query : {question}"
            }
        ]
    })

    return result
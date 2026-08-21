import langchain_mcp_adapters
import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq


from dotenv import load_dotenv
load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))

import asyncio
async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [os.path.join(script_dir, "mathserver.py")],
                "transport": "stdio",
            },
            "weather": {
                "command": sys.executable,
                "args": [os.path.join(script_dir, "weather.py")],
                "transport": "stdio",
            }
        }
    )

    # load the llm model
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    print("API Key Loaded:", os.getenv("GROQ_API_KEY")[:10] if os.getenv("GROQ_API_KEY") else "FAILED TO LOAD")

    tools = await client.get_tools()
    model = ChatGroq(model="llama-3.3-70b-versatile")
    agent = create_react_agent(model,tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role":"user","content":"What is the square root of 16?"}]}
    )

    print("math response",math_response['messages'][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role":"user","content":"What is the weather in Karwar?"}]}
    )
    print("weather response",weather_response['messages'][-1].content)


asyncio.run(main())




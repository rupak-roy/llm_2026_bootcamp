#load the API

import os 
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
print("API Key Loaded:", os.getenv("GROQ_API_KEY")[:10] if os.getenv("GROQ_API_KEY") else "FAILED TO LOAD")

#Test the API KEY
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI #alternative 

llm_model = ChatGroq(model ="llama-3.3-70b-versatile" )
print(llm_model.invoke("hello, tell me about yourself in few words").content)


from typing import TypedDict
from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

limiter = Limiter(key_func=get_remote_address)
# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="LangGraph Multi-Agent API",
    description="FastAPI API for Research, Analysis and Quality Agents",
    version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler)

# ---------------------------------------------------------
# API Request Model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    user_input: str


# ---------------------------------------------------------
# API Response Model
# ---------------------------------------------------------

class ChatResponse(BaseModel):
    user_input: str
    answer: str
    feedback: str
    satisfactory: bool
    iterations: int


# ---------------------------------------------------------
# Shared LangGraph State
# ---------------------------------------------------------

class State(TypedDict):
    user_input: str
    answer: str
    feedback: str
    satisfactory: bool
    iteration: int


# ---------------------------------------------------------
# Agent 1: Research Agent
# ---------------------------------------------------------

def research_agent(state: State):

    print("\n🔎 Research Agent")

    prompt = f"""
    User request:
    {state['user_input']}

    Previous feedback:
    {state['feedback']}

    Provide a clear and accurate answer to the user's request.

    If feedback is provided, improve the previous answer
    based on that feedback.
    """

    response = llm_model.invoke(prompt)

    return {
        "answer": response.content,
        "iteration": state.get("iteration", 0) + 1
    }


# ---------------------------------------------------------
# Agent 2: Analysis Agent
# ---------------------------------------------------------

def analysis_agent(state: State):

    print("\n🔍 Analysis Agent")

    prompt = f"""
    Review the following answer for the user's request.

    User request:
    {state['user_input']}

    Answer:
    {state['answer']}

    Identify what is missing, incorrect, unclear,
    or could be improved.

    Give concise improvement feedback.
    """

    response = llm_model.invoke(prompt)

    return {
        "feedback": response.content
    }


# ---------------------------------------------------------
# Agent 3: Quality Agent
# ---------------------------------------------------------

def quality_agent(state: State):

    print("\n✅ Quality Agent")
    prompt = f"""
    You are a quality evaluator.

    User request:
    {state['user_input']}

    Answer:
    {state['answer']}

    Reviewer feedback:
    {state['feedback']}

    Decide whether the answer is satisfactory.

    Respond ONLY with:

    YES
    or
    NO
    """

    response = llm_model.invoke(prompt)

    decision = response.content.strip().upper()

    if "YES" in decision:

        print("Result is satisfactory!")

        return {"satisfactory": True}

    print("Result needs improvement.")

    return {"satisfactory": False}


# ---------------------------------------------------------
# Routing Logic
# ---------------------------------------------------------

def check_quality(state: State):

    # Safety limit
    if state["satisfactory"] or state["iteration"] >= 3:
        return "done"

    return "improve"


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------

graph = StateGraph(State)
graph.add_node("research",research_agent)
graph.add_node("analysis",analysis_agent)
graph.add_node("quality",quality_agent)

# ---------------------------------------------------------
# Graph Edges
# ---------------------------------------------------------

graph.add_edge(START,"research")
graph.add_edge("research","analysis")
graph.add_edge("analysis","quality")

# ---------------------------------------------------------
# Conditional Routing
# ---------------------------------------------------------

graph.add_conditional_edges("quality",check_quality,
    {
        "improve": "research",
        "done": END
    })


# ---------------------------------------------------------
# Compile Graph
# ---------------------------------------------------------

workflow = graph.compile()

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "LangGraph Multi-Agent API"
    }


# ---------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------

@app.post("/chat",response_model=ChatResponse)
@limiter.limit("5/minute")
def chat(request: Request, chat_request: ChatRequest):

    try:

        print("\n===================================")
        print("New User Request")
        print("===================================")
        print(f"User Input: {request.user_input}")

        # ---------------------------------------------
        # Initial State
        # ---------------------------------------------

        initial_state: State = {
            "user_input": request.user_input,
            "answer": "",
            "feedback": "",
            "satisfactory": False,
            "iteration": 0
        }

        # ---------------------------------------------
        # Execute LangGraph
        # ---------------------------------------------

        result = workflow.invoke(
            initial_state
        )

        # ---------------------------------------------
        # Return Response
        # ---------------------------------------------

        return ChatResponse(
            user_input=result["user_input"],
            answer=result["answer"],
            feedback=result["feedback"],
            satisfactory=result["satisfactory"],
            iterations=result["iteration"]
        )

    except Exception as e:

        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500,
            detail=str(e))


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

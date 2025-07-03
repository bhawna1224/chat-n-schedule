import os
from dotenv import load_dotenv

from calendar_utils import get_availability, create_event
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
from date_utils import parse_date_string

# Load env and configure Gemini
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Init Gemini LLM with tools
llm = init_chat_model(model="gemini-1.5-flash-latest", model_provider="google_genai")

@tool
def check_availability(start: str, end: str, timezone: str = "UTC") -> str:
    """Check if the calendar is free for a given time period in given timezone."""
    try:
        start_parsed = parse_date_string(start, timezone)
        end_parsed = parse_date_string(end, timezone)
        busy = get_availability(start_parsed, end_parsed)
        return "Free" if not busy else f"Busy during: {busy}"
    except Exception as e:
        return f"Error parsing dates: {str(e)}"

@tool
def book_event(start: str, end: str, summary: str, description: str = "No description provided", timezone: str = "UTC") -> str:
    """Book a meeting in Google Calendar."""
    try:
        start_parsed = parse_date_string(start, timezone)
        end_parsed = parse_date_string(end, timezone)
        link = create_event(start_parsed, end_parsed, summary, description)
        return f"Booked! 📅 {link}"
    except Exception as e:
        return f"Error booking event: {str(e)}"

# Bind tools to the LLM
model = llm.bind_tools([check_availability, book_event])
tool_node = ToolNode([check_availability, book_event])

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    slots: dict
    user_timezone: str

def llm_node(state: AgentState):
    messages = state["messages"]
    response = model.invoke(messages)

    if hasattr(response, "tool_calls"):
        for call in response.tool_calls:
            args = call.get("args", {})
            for k, v in args.items():
                state["slots"][k] = v
    return {"messages": [response], "slots": state["slots"]}

g = StateGraph(AgentState)
g.add_node("llm", llm_node)
g.add_node("tools", tool_node)
g.add_edge(START, "llm")
g.add_conditional_edges("llm",
    lambda st: "tools" if getattr(st["messages"][-1], "tool_calls", None) else END,
    {"tools": "tools", END: END})
g.add_edge("tools", "llm")
graph = g.compile()

def chat_with_agent(prompt: str, user_timezone: str = "UTC", previous_slots: dict = None):
    print("chat_with_agent called")

    if previous_slots is None:
        previous_slots = {}

    print(" Prompt:", prompt)
    print("Previous slots:", previous_slots)
    print("Timezone:", user_timezone)

    messages = [HumanMessage(content=prompt)]
    slot_info = "\n".join(f"{k}: {v}" for k, v in previous_slots.items())
    if slot_info:
        messages.insert(0, HumanMessage(content=f"Previously known info:\n{slot_info}"))

    state = {
        "messages": messages,
        "slots": previous_slots,
        "user_timezone": user_timezone,
    }

    print("Invoking LangGraph...")
    out = graph.invoke(state)
    print("LangGraph returned:", out)

    messages = out["messages"]
    response = next(m.content for m in reversed(messages) if isinstance(m, AIMessage))
    print("Final response:", response)

    return response, out["slots"]

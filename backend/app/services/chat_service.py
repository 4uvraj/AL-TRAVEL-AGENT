"""
Chat service — wraps a simple LangChain ConversationChain for follow-up queries
about an already-planned trip or general travel advice.
"""
import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


SYSTEM_PROMPT = """You are AI Travel Copilot, a friendly and expert travel assistant.
You help users plan trips, suggest places to visit, estimate budgets, and answer
travel-related questions. Be concise, helpful, and enthusiastic about travel.
If asked about itinerary details, provide structured, actionable responses."""


def run_chat(message: str, history: List[Dict[str, str]] = None) -> str:
    """
    Single-turn chat with conversation history.
    history is a list of {"role": "user"|"assistant", "content": "..."} dicts.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for turn in (history or []):
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=message))

    response = llm.invoke(messages)
    return response.content

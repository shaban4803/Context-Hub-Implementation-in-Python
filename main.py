import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from tool import fetch_api_docs

load_dotenv()

MODEL = "gpt-4o-mini"
PROMPT = "what is quantum mechanics."
DEFAULT_API_NAME = "openai"
SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Use the fetched API documentation as reference context before answering."
)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    system_prompt: str
    api_name: str
    api_docs: str


llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))


def fetch_docs_node(state: AgentState) -> dict:
    api_name = state.get("api_name", DEFAULT_API_NAME)
    api_docs = state.get("api_docs", "").strip()

    if api_docs:
        return {}

    return {"api_docs": fetch_api_docs.invoke({"api_name": api_name})}



def chatbot_node(state: AgentState) -> dict:
    doc_context = state.get("api_docs", "").strip() or "No API docs were fetched."

    response = llm.invoke(
        [
            SystemMessage(content=state["system_prompt"]),
            SystemMessage(content=f"Fetched API docs:\n{doc_context}"),
            *state["messages"],
        ]
    )
    return {"messages": [response]}


graph_builder = StateGraph(AgentState)
graph_builder.add_node("fetch_docs", fetch_docs_node)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_edge(START, "fetch_docs")
graph_builder.add_edge("fetch_docs", "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


def run_agent(
    prompt: str,
    api_name: str = DEFAULT_API_NAME,
    session_state: AgentState | None = None,
) -> AgentState:
    initial_state: AgentState = session_state or {
        "messages": [],
        "system_prompt": SYSTEM_PROMPT,
        "api_name": api_name,
        "api_docs": "",
    }

    initial_state["api_name"] = api_name
    initial_state["messages"] = [*initial_state["messages"], HumanMessage(content=prompt)]

    return graph.invoke(initial_state)


if __name__ == "__main__":
    session_state = run_agent(PROMPT)
    final_message = session_state["messages"][-1]
    fetched_docs = session_state.get("api_docs", "").strip()

    print(f"Prompt: {PROMPT}\n")
    print("Fetched docs:")
    print(fetched_docs or "No API docs were fetched.")
    print()
    print("Response:")
    if isinstance(final_message, AIMessage):
        print(final_message.content)
    else:
        print(final_message)

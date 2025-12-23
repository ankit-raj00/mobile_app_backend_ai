from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agent.llm_setup import get_llm
from langgraph.graph.message import add_messages

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Define nodes and edges
def call_model(state: AgentState):
    messages = state["messages"]
    llm, _ = get_llm()
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM makes a tool call, go to "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, end
    return END

# Build the graph
def build_agent_graph():
    _, tools = get_llm()
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    
    # Add normal edges
    workflow.add_edge("tools", "agent")
    
    # Compile
    app = workflow.compile()
    return app

agent_app = build_agent_graph()

from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatTongyi
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from .state import AgentState
from .agents.profiler import profiler_node
from .agents.navigator import navigator_node
from .agents.storyteller import storyteller_node

# Define the routing model for structured output
class RouteResponse(BaseModel):
    next: Literal["Profiler", "Navigator", "Storyteller", "FINISH"]

def supervisor_node(state: AgentState):
    # Hardcoded logic: If the last message is from Storyteller, we are done.
    # Check the last message in state
    if state["messages"]:
        last_msg = state["messages"][-1]
        if isinstance(last_msg, str):
            content = last_msg
        else:
            content = last_msg.content
            
        if "Storyteller" in content or "导游" in content:
            return {"next": "FINISH"}

    # Initialize LLM
    import os
    llm_model = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    llm = ChatTongyi(model=llm_model, temperature=0)
    
    system_prompt = (
        "你是整个导览系统的管理者。根据用户的输入，决定下一步是交给 'Profiler' 完善画像，"
        "还是交给 'Navigator' 规划路线，还是交给 'Storyteller' 进行讲解。"
        "如果用户输入的是 JSON 格式的问卷数据（包含 'selected_themes', 'mbti_selection' 等字段），请务必选择 'Profiler'。"
        "如果 'Navigator' 已经规划好路线，选择 'Storyteller' 或 'FINISH'。"
        "如果上一条消息是 'Storyteller' 发出的导览词，或者任务已完成，务必选择 'FINISH'。"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? Or should we FINISH? Select one: 'Profiler', 'Navigator', 'Storyteller', 'FINISH'.")
    ])
    
    # Create the chain with structured output
    supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
    
    # Invoke the chain
    result = supervisor_chain.invoke(state)
    
    return {"next": result.next}

def start_node(state: AgentState):
    # Check if we have structured data in user_profile
    user_profile = state.get("user_profile")
    if user_profile and user_profile.interests:
        print(f"DEBUG: Start Node routing to Navigator (Structured Data). Interests: {user_profile.interests}")
        return {"next": "Navigator"}
    
    # Check if the last message is JSON (Legacy check, or if main.py didn't populate profile)
    last_message = state["messages"][-1]
    content = last_message.content.strip()
    
    if content.startswith("{") and content.endswith("}"):
        print(f"DEBUG: Start Node routing to Profiler (JSON Input).")
        return {"next": "Profiler"}
    else:
        # Natural language input -> Profiler to extract interests
        print(f"DEBUG: Start Node routing to Profiler (Text Input).")
        return {"next": "Profiler"}

# --- Build Graph ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("Start", start_node)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Profiler", profiler_node)
workflow.add_node("Navigator", navigator_node)
workflow.add_node("Storyteller", storyteller_node)

# Add edges
# Start at Start Node
workflow.set_entry_point("Start")

# Conditional edges from Start
workflow.add_conditional_edges(
    "Start",
    lambda x: x["next"],
    {
        "Profiler": "Profiler",
        "Navigator": "Navigator",
        "Supervisor": "Supervisor"
    }
)

# Conditional edges from Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "Profiler": "Profiler",
        "Navigator": "Navigator",
        "Storyteller": "Storyteller",
        "FINISH": END
    }
)

# Edges from workers back to Supervisor
# workflow.add_edge("Profiler", "Supervisor") # Removed
workflow.add_edge("Profiler", "Navigator") # Direct routing
workflow.add_edge("Navigator", "Supervisor")
workflow.add_edge("Storyteller", "Supervisor")

# Compile the graph
app_graph = workflow.compile()

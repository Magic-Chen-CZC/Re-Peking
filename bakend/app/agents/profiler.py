import json
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi
from ..state import AgentState, UserProfile

from pydantic import BaseModel, Field
from typing import List

class ProfilerOutput(BaseModel):
    selected_themes: List[str] = Field(description="List of interest tags extracted from user input")

def profiler_node(state: AgentState):
    # Get existing profile or create new (though it should exist from main.py)
    user_profile = state.get("user_profile")
    if not user_profile:
        # Fallback if not initialized
        user_profile = UserProfile(
            mbti_type="Unknown",
            interests=[],
            time_budget="half_day",
            pace_preference="medium",
            transportation="auto",
            persona_instruction=""
        )

    # Get the last message content
    last_message = state["messages"][-1]
    content = last_message.content
    
    # Initialize LLM
    import os
    llm_model = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    llm = ChatTongyi(model=llm_model, temperature=0)
    
    system_prompt = (
        "你是一个用户画像分析引擎。你的唯一任务是从用户的自然语言输入中，分析并提取出 Interest Tags (兴趣关键词) 列表。\n"
        "如果没有明确的兴趣（例如用户只说了心情），请推断出最合适的 1-3 个标签。\n"
        "不要提取时间预算、MBTI 或出行方式，这些信息已经由前端提供。\n"
        "只返回 selected_themes。"
    )
    
    # We want the LLM to output just the themes
    profiler_chain = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "User Input: {input}")
    ]) | llm.with_structured_output(ProfilerOutput)
    
    # Invoke
    result = profiler_chain.invoke({"input": content})
    
    # Update existing profile
    if result and result.selected_themes:
        user_profile.interests = result.selected_themes
        
    # Generate persona instruction based on new interests and existing MBTI
    # (Optional: we can keep the logic here or move it to Storyteller. 
    # The previous Profiler did this. Let's keep a simple one or leave it empty as Storyteller handles it now.)
    # The user request said "Simplification... Remove... extraction of mbti...". 
    # It didn't explicitly say remove persona generation, but Storyteller now handles default persona.
    # Let's update persona_instruction just in case, or leave it blank.
    # Storyteller uses: if not persona_instruction ...
    # Let's leave it as is (likely empty from main.py) or generate a simple one.
    # To be safe and simple, let's leave it to Storyteller's dynamic logic or just set a basic one.
    # Actually, Storyteller logic is: `if not persona_instruction or ...`. 
    # So we don't need to generate it here.
    
    return {
        "user_profile": user_profile,
        "next": "Navigator",
        "messages": [AIMessage(content=f"Interests identified: {user_profile.interests}")]
    }

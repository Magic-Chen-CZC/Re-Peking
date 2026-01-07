from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi
from ..state import AgentState
from ..services.rag_service import rag_service

def storyteller_node(state: AgentState):
    user_profile = state["user_profile"]
    
    # Get the last message to extract entity
    # In a real scenario, we might look at the current location or the last user message
    # For this flow, let's assume the user just arrived at a spot or we are explaining the route.
    # But wait, the previous flow was Navigator -> Supervisor -> Storyteller.
    # The user hasn't said "I am at Forbidden City".
    # However, the Navigator outputted a plan.
    # Let's assume the Storyteller picks the first POI from the route plan to explain, 
    # OR if there is a user message asking about a place.
    
    # For the purpose of this demo, let's try to extract a POI name from the context or default to "故宫" if none found.
    # If the route plan exists, we can pick the first POI.
    target_poi = "故宫" # Default
    if state.get("route_plan") and state["route_plan"].steps:
        target_poi = state["route_plan"].steps[0].poi.name
        
    # Retrieve context
    context_str = rag_service.retrieve_context(target_poi)
    
    # Initialize LLM
    import os
    llm_model = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    llm = ChatTongyi(model=llm_model, temperature=0.7) # Higher temp for creativity
    
    # Handle missing persona
    persona_instruction = user_profile.persona_instruction
    if not persona_instruction or user_profile.mbti_type in ["Unknown", None, ""]:
        persona_instruction = (
            "Default Persona: Be professional, warm, knowledgeable, and neutral. "
            "Do not assume any specific personality type. Just be a good guide."
        )

    system_prompt = (
        "你是一位专业的个性化导游。\n\n"
        f"当前人设: {persona_instruction}\n\n"
        f"景点事实数据 (Context): {context_str}\n\n"
        "任务: 根据上述事实数据，用符合你人设的语气为游客讲解该景点。\n"
        "严格基于事实，不要编造年份或数据。\n"
        "必须体现人设的风格。\n"
        "不要提及'根据数据库'或'根据提供的信息'，要自然地讲出来。"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"请为我讲解一下【{target_poi}】。")
    ])
    
    chain = prompt | llm
    response = chain.invoke({})
    
    return {"messages": [response]}

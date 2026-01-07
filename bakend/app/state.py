import operator
from typing import Annotated, List, Optional, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class UserProfile(BaseModel):
    mbti_type: str = Field(description="User's MBTI type, e.g., INFP")
    interests: List[str] = Field(description="User's interests, e.g., ['History', 'Food']")
    current_location: Optional[str] = Field(None, description="User's current location")
    time_budget: str = Field("half_day", description="Time budget, e.g., 'half_day', 'full_day'")
    pace_preference: str = Field("medium", description="Pace preference, e.g., 'slow', 'medium', 'fast'")
    transportation: str = Field("auto", description="Transportation mode: 'walking', 'driving', 'auto'")
    persona_instruction: str = Field(description="System persona instruction for the Storyteller")

class POI(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    tags: List[str]
    zone: str

class RouteStep(BaseModel):
    poi: POI
    visit_duration: int # minutes
    transit_note: str

class RoutePlan(BaseModel):
    steps: List[RouteStep]
    total_duration: int # minutes
    total_distance: int # meters
    summary: str
    polyline: Optional[str] = None # AMap polyline string
    mode: str = "walking" # Final transportation mode used

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_profile: Optional[UserProfile]
    route_plan: Optional[RoutePlan]
    plan: Optional[dict]
    next: str

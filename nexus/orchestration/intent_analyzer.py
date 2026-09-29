from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types
import os

class SubIntent(BaseModel):
    action: str
    entity: str
    priority: int = Field(ge=1, le=3, default=1)

class IntentGraph(BaseModel):
    primary_domain: Literal["student", "shopkeeper", "mixed"]
    sub_intents: List[SubIntent]
    raw_query: str
    confidence: float

def analyze_intent(query: str) -> IntentGraph:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_analyze(query)
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Analyze the user query: '{query}'. "
            "Decompose into atomic sub-intents (action, entity, priority 1-3) "
            "and classify the primary domain as 'student', 'shopkeeper', or 'mixed'."
        )
        response = client.models.generate_content(
            model='gemma-4-26b-a4b-it',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_json_schema=IntentGraph.model_json_schema(),
            ),
        )
        return IntentGraph.model_validate_json(response.text)
    except Exception:
        return _fallback_analyze(query)

def _fallback_analyze(query: str) -> IntentGraph:
    q = query.lower()
    domain = "mixed"
    if any(k in q for k in ["study", "grade", "exam", "assignment", "attendance", "formula", "note", "citation"]):
        domain = "student"
    elif any(k in q for k in ["shop", "stock", "inventory", "cash", "ledger", "supplier", "barcode", "profit", "udhar"]):
        domain = "shopkeeper"
    return IntentGraph(
        primary_domain=domain,
        sub_intents=[SubIntent(action="process", entity="workspace", priority=1)],
        raw_query=query,
        confidence=0.85
    )

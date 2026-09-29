from nexus.orchestration.intent_analyzer import analyze_intent
from nexus.orchestration.tool_caller import call_tools
from nexus.orchestration.workspace_composer import compose_workspace
from nexus.parser.models import ComponentMetadata
import json
import os

def run_agentic_loop(user_query: str) -> dict:
    try:
        with open("vector_index/metadata.json", "r") as f:
            meta = json.load(f)
            components = [ComponentMetadata(**m) for m in meta.values()]
    except Exception:
        components = []
        
    intent = analyze_intent(user_query)
    filtered = components
    if intent.primary_domain != "mixed":
        filtered = [c for c in components if c.domain == intent.primary_domain]
        
    call = call_tools(intent, filtered)
    workspace = compose_workspace(call)
    
    return {
        "intent_graph": intent.model_dump(),
        "workspace_call": call.model_dump(),
        "workspace_config": workspace
    }

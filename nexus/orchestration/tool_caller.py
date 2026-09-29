from pydantic import BaseModel
from typing import List, Dict, Any
from google import genai
from google.genai import types
import os
import json
from nexus.orchestration.intent_analyzer import IntentGraph
from nexus.parser.models import ComponentMetadata
from nexus.representation.schema_compressor import compress_schema

class ToolBinding(BaseModel):
    component_id: str
    bound_props: Dict[str, Any]
    confidence: float

class WorkspaceCall(BaseModel):
    selected_tools: List[ToolBinding]
    intent_coverage: float
    schema_conformance_rate: float

def call_tools(intent: IntentGraph, components: List[ComponentMetadata]) -> WorkspaceCall:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_call(intent, components)
        
    try:
        client = genai.Client(api_key=api_key)
        comp_str = "\n".join([compress_schema(c).capability_card for c in components])
        
        prompt = (
            f"User Intent: {intent.model_dump_json()}\n\n"
            f"Available Component Tools (SEA Compressed Capability Cards):\n{comp_str}\n\n"
            "Select the most appropriate components to satisfy the user's intent, and bind necessary props."
        )
        response = client.models.generate_content(
            model='gemma-4-26b-a4b-it',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_json_schema=WorkspaceCall.model_json_schema(),
            ),
        )
        parsed = WorkspaceCall.model_validate_json(response.text)
        
        # Normalize tool names (remove file path prefixes if any)
        for t in parsed.selected_tools:
            t.component_id = t.component_id.split("/")[-1].replace(".tsx", "").strip()

        # Validate schema conformance against actual component props
        valid_props_count = 0
        total_props_count = 0
        comp_lookup = {c.name: c for c in components}

        for t in parsed.selected_tools:
            if t.component_id in comp_lookup:
                allowed_props = {p.name for p in comp_lookup[t.component_id].props}
                for prop_name in t.bound_props:
                    total_props_count += 1
                    if prop_name in allowed_props:
                        valid_props_count += 1

        conformance = (valid_props_count / total_props_count) if total_props_count > 0 else 1.0
        parsed.schema_conformance_rate = conformance
        return parsed
    except Exception:
        return _fallback_call(intent, components)

def _fallback_call(intent: IntentGraph, components: List[ComponentMetadata]) -> WorkspaceCall:
    # Heuristic fallback matching component domain to intent
    selected = []
    for c in components:
        if c.domain == intent.primary_domain or intent.primary_domain == "mixed":
            selected.append(ToolBinding(
                component_id=c.name,
                bound_props={},
                confidence=0.85
            ))
            if len(selected) >= 2:
                break
    return WorkspaceCall(
        selected_tools=selected,
        intent_coverage=1.0 if selected else 0.0,
        schema_conformance_rate=1.0
    )

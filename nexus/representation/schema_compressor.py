from pydantic import BaseModel
from typing import List, Dict
from nexus.parser.models import ComponentMetadata
import os

class CompressedSchema(BaseModel):
    component_id: str
    capability_card: str
    minimal_props: List[str]
    token_count_raw: int
    token_count_compressed: int
    compression_ratio: float

def compress_schema(metadata: ComponentMetadata) -> CompressedSchema:
    raw_tokens = 100
    try:
        if os.path.exists(metadata.file_path):
            with open(metadata.file_path, "r", encoding="utf-8") as f:
                raw_tokens = len(f.read().split())
    except Exception:
        pass

    props = [p.name for p in metadata.props] if metadata.props else []
    caps = ", ".join(metadata.dependencies) if metadata.dependencies else "none"
    
    card = f"[{metadata.name}] ({metadata.domain}) | {metadata.description} | props: {props} | caps: {caps}"
    comp_tokens = len(card.split())
    
    ratio = 1 - (comp_tokens / raw_tokens) if raw_tokens > 0 else 0
    
    return CompressedSchema(
        component_id=metadata.name,
        capability_card=card,
        minimal_props=props,
        token_count_raw=raw_tokens,
        token_count_compressed=comp_tokens,
        compression_ratio=ratio
    )

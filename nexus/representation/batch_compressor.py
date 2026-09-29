import json
from nexus.parser.models import ComponentMetadata
from nexus.representation.schema_compressor import compress_schema
import os

def run_batch_compression():
    with open("vector_index/metadata.json", "r") as f:
        meta = json.load(f)
    
    results = []
    total_raw = 0
    total_comp = 0
    
    for m_dict in meta.values():
        m = ComponentMetadata(**m_dict)
        c = compress_schema(m)
        results.append(c.model_dump())
        total_raw += c.token_count_raw
        total_comp += c.token_count_compressed
        
    overall = 1 - (total_comp / total_raw) if total_raw > 0 else 0
    
    out = {
        "schemas": results,
        "summary": {
            "total_raw_tokens": total_raw,
            "total_compressed_tokens": total_comp,
            "overall_compression_ratio": overall
        }
    }
    
    os.makedirs("vector_index", exist_ok=True)
    with open("vector_index/compressed_schemas.json", "w") as f:
        json.dump(out, f, indent=2)
        
    return out

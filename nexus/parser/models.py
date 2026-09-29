"""
Data models for component representation and AST parsing.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class PropDefinition(BaseModel):
    name: str
    type_signature: str
    is_optional: bool = False
    description: Optional[str] = None


class HookUsage(BaseModel):
    hook_type: str  # useState, useEffect, useCallback, useMemo, etc.
    state_variable: Optional[str] = None
    setter_name: Optional[str] = None
    inferred_type: Optional[str] = None
    inferred_purpose: Optional[str] = None


class ComponentMetadata(BaseModel):
    component_id: str  # e.g., "student/PomodoroTimer"
    name: str  # e.g., "PomodoroTimer"
    file_path: str  # e.g., "registry/student/PomodoroTimer.tsx"
    domain: str  # "student" | "shopkeeper" | "general"
    description: str
    capabilities: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    exports: List[str] = Field(default_factory=list)
    props_interface_name: Optional[str] = None
    props: List[PropDefinition] = Field(default_factory=list)
    hooks: List[HookUsage] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    
    # Hashes for incremental indexing
    raw_code_sha256: str
    semantic_sha256: str
    
    # Multi-granularity text representations for retrieval (SEA / Zhong et al. 2025)
    summary_card: str
    interface_signature: str
    clean_semantic_code: str
    composite_representation: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

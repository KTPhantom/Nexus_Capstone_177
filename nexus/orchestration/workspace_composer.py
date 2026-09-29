from pydantic import BaseModel
from typing import List, Dict, Any
from nexus.orchestration.tool_caller import WorkspaceCall

class GridCell(BaseModel):
    component_id: str
    col: int
    row: int
    col_span: int
    row_span: int

class WorkspaceConfig(BaseModel):
    grid_layout: List[GridCell]
    tool_bindings: List[Dict[str, Any]]
    workspace_title: str

def compose_workspace(call: WorkspaceCall) -> dict:
    n = len(call.selected_tools)
    layout = []
    cols = 1 if n <= 2 else (2 if n <= 4 else 3)
    for i, tool in enumerate(call.selected_tools):
        layout.append(GridCell(
            component_id=tool.component_id,
            col=(i % cols) + 1,
            row=(i // cols) + 1,
            col_span=1,
            row_span=1
        ))
    
    cfg = WorkspaceConfig(
        grid_layout=layout,
        tool_bindings=[t.model_dump() for t in call.selected_tools],
        workspace_title="Auto-Generated Workspace"
    )
    return cfg.model_dump()

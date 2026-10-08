"""
Component Representation & AST Parser Engine for React (.tsx) components.
Extracts component boundaries, props interfaces, hook dependencies, capabilities,
and generates multi-granularity semantic chunks (Zhong et al. 2025, Hu et al. 2024).
"""

import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from .models import ComponentMetadata, PropDefinition, HookUsage
from .noise_filter import clean_semantic_tsx


class TSXComponentParser:
    """
    Parser for TypeScript React (.tsx) component files.
    """

    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def parse_file(self, file_path: str | Path) -> ComponentMetadata:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            raw_code = f.read()

        return self.parse_source(raw_code, relative_path=str(path).replace("\\", "/"))

    def parse_source(self, raw_code: str, relative_path: str = "") -> ComponentMetadata:
        # Extract JSDoc block
        jsdoc_meta = self._extract_jsdoc(raw_code)

        # Infer component name and domain
        name = jsdoc_meta.get("name")
        if not name:
            name_match = re.search(r"export\s+(?:const|function|class)\s+([A-Z][a-zA-Z0-9]+)", raw_code)
            if not name_match:
                name_match = re.search(r"export\s+default\s+(?:function\s+)?([A-Z][a-zA-Z0-9]+)", raw_code)
            name = name_match.group(1) if name_match else Path(relative_path).stem

        domain = jsdoc_meta.get("domain")
        if not domain:
            if "student" in relative_path.lower():
                domain = "student"
            elif "shopkeeper" in relative_path.lower():
                domain = "shopkeeper"
            else:
                domain = "general"

        description = jsdoc_meta.get("description", f"React component for {name}")
        capabilities = jsdoc_meta.get("capabilities", [])
        author = jsdoc_meta.get("author", "Nexus Registry")

        # Extract props interface
        props_interface_name, props = self._extract_props(raw_code, name)

        # Extract hooks usage
        hooks = self._extract_hooks(raw_code)

        # Extract dependencies
        dependencies = self._extract_dependencies(raw_code)

        # Extract exports
        exports = self._extract_exports(raw_code)

        # Clean code representation
        clean_code = clean_semantic_tsx(raw_code)

        # Compute stable hashes
        raw_code_sha256 = self.compute_sha256(raw_code)
        
        # Build representations
        summary_card = self._build_summary_card(
            name=name,
            domain=domain,
            description=description,
            capabilities=capabilities,
            props=props,
            hooks=hooks,
        )

        interface_signature = self._build_interface_signature(
            name=name,
            props_interface_name=props_interface_name,
            props=props,
            exports=exports,
        )

        # Semantic hash is based on clean code + summary card + interface
        semantic_payload = f"{summary_card}\n---\n{interface_signature}\n---\n{clean_code}"
        semantic_sha256 = self.compute_sha256(semantic_payload)

        composite_representation = self._build_composite_representation(
            summary_card=summary_card,
            interface_signature=interface_signature,
            clean_code=clean_code,
        )

        component_id = f"{domain}/{name}"

        return ComponentMetadata(
            component_id=component_id,
            name=name,
            file_path=relative_path,
            domain=domain,
            description=description,
            capabilities=capabilities,
            author=author,
            exports=exports,
            props_interface_name=props_interface_name,
            props=props,
            hooks=hooks,
            dependencies=dependencies,
            raw_code_sha256=raw_code_sha256,
            semantic_sha256=semantic_sha256,
            summary_card=summary_card,
            interface_signature=interface_signature,
            clean_semantic_code=clean_code,
            composite_representation=composite_representation,
        )

    def _extract_jsdoc(self, code: str) -> Dict[str, Any]:
        result = {}
        jsdoc_match = re.search(r"/\*\*\s*([\s\S]*?)\*/", code)
        if not jsdoc_match:
            return result

        content = jsdoc_match.group(1)
        for line in content.splitlines():
            line = line.strip().lstrip("*").strip()
            if not line.startswith("@"):
                continue

            tag_match = re.match(r"@([a-zA-Z0-9_-]+)\s+(.*)", line)
            if tag_match:
                tag, val = tag_match.group(1).lower(), tag_match.group(2).strip()
                if tag == "name":
                    result["name"] = val
                elif tag == "domain":
                    result["domain"] = val
                elif tag == "description":
                    result["description"] = val
                elif tag == "capability" or tag == "capabilities":
                    # Split comma or space separated capabilities
                    caps = [c.strip() for c in re.split(r"[,\s]+", val) if c.strip()]
                    result.setdefault("capabilities", []).extend(caps)
                elif tag == "author":
                    result["author"] = val

        return result

    def _extract_props(self, code: str, component_name: str) -> Tuple[Optional[str], List[PropDefinition]]:
        pattern = rf"(?:export\s+)?(?:interface|type)\s+({component_name}Props|[A-Za-z0-9_]*Props)\s*(?:=\s*)?\{{"
        match = re.search(pattern, code)
        if not match:
            return None, []

        interface_name = match.group(1)
        start_pos = match.end() - 1  # opening '{'

        # Balanced curly brace scan
        depth = 0
        end_pos = -1
        for idx in range(start_pos, len(code)):
            char = code[idx]
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end_pos = idx
                    break

        body = code[start_pos + 1:end_pos] if end_pos != -1 else code[start_pos + 1:]
        props: List[PropDefinition] = []

        lines = body.splitlines()
        accumulated = ""
        brace_depth = 0
        paren_depth = 0

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue

            accumulated += (" " + stripped if accumulated else stripped)
            brace_depth += stripped.count("{") - stripped.count("}")
            paren_depth += stripped.count("(") - stripped.count(")")

            if brace_depth <= 0 and paren_depth <= 0 and (accumulated.endswith(";") or line == lines[-1]):
                clean_stmt = accumulated.rstrip(";").strip()
                prop_match = re.match(r"^([a-zA-Z0-9_]+)(\??)\s*:\s*(.+)$", clean_stmt)
                if prop_match:
                    prop_name = prop_match.group(1)
                    is_optional = bool(prop_match.group(2))
                    type_sig = prop_match.group(3).strip().rstrip(";")
                    props.append(
                        PropDefinition(
                            name=prop_name,
                            type_signature=type_sig,
                            is_optional=is_optional,
                        )
                    )
                accumulated = ""
                brace_depth = 0
                paren_depth = 0

        return interface_name, props

    def _extract_hooks(self, code: str) -> List[HookUsage]:
        hooks: List[HookUsage] = []

        # Find useState: const [x, setX] = useState...
        for m in re.finditer(r"const\s*\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*useState", code):
            var_name, setter = m.group(1), m.group(2)
            rest = code[m.end():].lstrip()
            type_arg = None
            if rest.startswith("<"):
                depth = 0
                for idx, ch in enumerate(rest):
                    if ch == "<":
                        depth += 1
                    elif ch == ">":
                        depth -= 1
                        if depth == 0:
                            type_arg = rest[1:idx].strip()
                            break

            hooks.append(
                HookUsage(
                    hook_type="useState",
                    state_variable=var_name,
                    setter_name=setter,
                    inferred_type=type_arg,
                    inferred_purpose=f"Local state for {var_name}",
                )
            )

        # Find useEffect
        if re.search(r"useEffect\s*\(", code):
            hooks.append(
                HookUsage(
                    hook_type="useEffect",
                    inferred_purpose="Lifecycle and interval/side-effect subscription",
                )
            )

        # Find useMemo
        for m in re.finditer(r"const\s*(?:\{([^}]+)\}|([a-zA-Z0-9_]+))\s*=\s*useMemo\s*\(", code):
            destructured, single_var = m.groups()
            var_name = destructured.strip() if destructured else (single_var.strip() if single_var else "memoizedValue")
            hooks.append(
                HookUsage(
                    hook_type="useMemo",
                    state_variable=var_name,
                    inferred_purpose=f"Computed memoized value for {var_name}",
                )
            )

        # Find useCallback
        for m in re.finditer(r"const\s*([a-zA-Z0-9_]+)\s*=\s*useCallback\s*\(", code):
            cb_name = m.group(1)
            hooks.append(
                HookUsage(
                    hook_type="useCallback",
                    state_variable=cb_name,
                    inferred_purpose=f"Memoized handler callback for {cb_name}",
                )
            )

        # Find useRef
        for m in re.finditer(r"const\s+([a-zA-Z0-9_]+)\s*=\s*useRef", code):
            ref_name = m.group(1)
            hooks.append(
                HookUsage(
                    hook_type="useRef",
                    state_variable=ref_name,
                    inferred_purpose=f"Mutable reference for {ref_name}",
                )
            )

        return hooks

    def _extract_dependencies(self, code: str) -> List[str]:
        deps: List[str] = []
        for m in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", code):
            deps.append(m.group(1))
        return sorted(set(deps))

    def _extract_exports(self, code: str) -> List[str]:
        exports: List[str] = []
        for m in re.finditer(r"export\s+(?:const|function|class)\s+([a-zA-Z0-9_]+)", code):
            exports.append(m.group(1))
        for m in re.finditer(r"export\s+default\s+([a-zA-Z0-9_]+)", code):
            exports.append(f"default:{m.group(1)}")
        return sorted(set(exports))

    def _build_summary_card(
        self,
        name: str,
        domain: str,
        description: str,
        capabilities: List[str],
        props: List[PropDefinition],
        hooks: List[HookUsage],
    ) -> str:
        caps_str = ", ".join(capabilities) if capabilities else "none"
        props_str = ", ".join([f"{p.name}{'?' if p.is_optional else ''}: {p.type_signature}" for p in props[:6]])
        states = [h.state_variable for h in hooks if h.hook_type == "useState" and h.state_variable]
        states_str = ", ".join(states) if states else "none"

        return (
            f"Component: {name}\n"
            f"Domain: {domain}\n"
            f"Description: {description}\n"
            f"Capabilities: {caps_str}\n"
            f"Key Props: {props_str}\n"
            f"Key State: {states_str}"
        )

    def _build_interface_signature(
        self,
        name: str,
        props_interface_name: Optional[str],
        props: List[PropDefinition],
        exports: List[str],
    ) -> str:
        props_lines = [f"  {p.name}{'?' if p.is_optional else ''}: {p.type_signature};" for p in props]
        interface_block = f"interface {props_interface_name or f'{name}Props'} {{\n" + "\n".join(props_lines) + "\n}"
        exports_block = f"Exports: {', '.join(exports)}"
        return f"{interface_block}\n{exports_block}"

    def _build_composite_representation(
        self,
        summary_card: str,
        interface_signature: str,
        clean_code: str,
    ) -> str:
        """
        Assemble composite representation for dense neural embedding.
        Zhong et al. (2025) and Hu et al. (2024) SEA demonstrate that placing
        high-level semantic intent ahead of schema and clean code yields superior
        retrieval alignment with natural language queries.
        """
        # Strip duplicate top JSDoc and top imports from code to avoid token waste,
        # retaining the full functional logic and UI return elements.
        code_without_jsdoc = re.sub(r"^/\*\*[\s\S]*?\*/", "", clean_code).strip()
        code_lines = [l for l in code_without_jsdoc.splitlines() if not l.strip().startswith("import ")]
        concise_code = "\n".join(code_lines[:160]).strip()

        return (
            f"### COMPONENT SUMMARY\n{summary_card}\n\n"
            f"### INTERFACE & CONTRACT\n{interface_signature}\n\n"
            f"### SEMANTIC LOGIC & STRUCTURE\n{concise_code}"
        )

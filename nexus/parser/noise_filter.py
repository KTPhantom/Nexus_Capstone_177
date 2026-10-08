"""
Noise filter module for React/TSX source code.
Strips utility CSS (Tailwind classes), inline styling, and SVG path boilerplate
to produce clean, high-density semantic representations (Zhong et al. 2025).
"""

import re


def strip_tailwind_classes(code: str) -> str:
    """
    Remove className attributes with static strings, template literals, or ternary expressions.
    Retains the semantic JSX structure without styling noise.
    """
    # Replace className={`...`} with template strings
    cleaned = re.sub(r'className=\{`[^`]*`\}', '', code)
    # Replace className="..." or className='...'
    cleaned = re.sub(r'className="[^"]*"', '', cleaned)
    cleaned = re.sub(r"className='[^']*'", '', cleaned)
    # Replace className={...}
    cleaned = re.sub(r'className=\{[^{}]*\}', '', cleaned)
    # Replace style={{...}}
    cleaned = re.sub(r'style=\{\{[^{}]*\}\}', '', cleaned)
    return cleaned


def strip_svg_boilerplate(code: str) -> str:
    """
    Replace verbose <svg ...>...</svg> blocks with compact <Icon /> placeholder.
    """
    cleaned = re.sub(r'<svg[\s\S]*?</svg>', '<Icon />', code)
    return cleaned


def normalize_whitespace(code: str) -> str:
    """
    Normalize indentation and eliminate redundant blank lines.
    """
    lines = [line.rstrip() for line in code.splitlines()]
    result = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                result.append(line)
                prev_blank = True
        else:
            result.append(line)
            prev_blank = False
    return "\n".join(result).strip()


def clean_semantic_tsx(raw_code: str) -> str:
    """
    Execute full noise filtering pipeline on TSX source code.
    Produces high-fidelity semantic logic representation for embedding models.
    """
    code = strip_svg_boilerplate(raw_code)
    code = strip_tailwind_classes(code)
    # Remove excessive blank lines resulting from attribute removal
    code = re.sub(r'<\s*([a-zA-Z0-9_.-]+)\s+>', r'<\1>', code)
    code = normalize_whitespace(code)
    return code

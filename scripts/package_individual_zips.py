"""
Package two individual, submission-ready ZIP archives for Barun and Kshitij.
Each package contains the complete, working codebase with tailored README.md
and dossiers highlighting their respective technical ownership for GitHub.
"""
import os
import zipfile
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(BASE_DIR)

BARUN_README = """# Nexus: Agentic AI & Workspace Orchestration Engine
**Lead Engineer:** Barun Kumar Pattanaik  
**Role:** Agentic AI & Multi-Agent Orchestration Lead (Module M4)  
**Project:** Nexus — A Self-Configuring Multi-Agent Productivity System  
**Review:** Capstone Review 1 | Supervisor: Dr. Ashfaq Ahmad Najjar  

---

## 📌 Primary Contributions & Ownership

Barun Kumar Pattanaik leads the **Agentic Intelligence & Workspace Orchestration** engine of the Nexus system:

1. **ATLASS Intent Analyzer (`nexus/orchestration/intent_analyzer.py`)**:
   - Implements atomic intent decomposition from the *ATLASS Framework* (Haque et al., IEEE SOSE 2025).
   - Decomposes ambiguous, compound queries into a prioritized graph of sub-intents using `gemma-4-26b-a4b-it` via Google GenAI SDK.
   - Enforces Pydantic structured output models for deterministic domain routing (`student`, `shopkeeper`, `mixed`).

2. **Toolformer Tool Caller (`nexus/orchestration/tool_caller.py`)**:
   - Implements declarative tool selection and prop binding inspired by *Toolformer* (Schick et al., NeurIPS 2023).
   - Selects components against AST-compressed capability cards and validates parameter schemas against TypeScript interfaces.
   - Eliminates prop hallucinations, achieving **100.0% Schema Conformance**.

3. **Workspace Grid Composer (`nexus/orchestration/workspace_composer.py`)**:
   - Generates dynamic CSS Grid configurations for automated component mounting on the desktop layout.

4. **Agentic Loop Orchestrator (`nexus/orchestration/agentic_loop.py`)**:
   - Coordinates the 4-stage pipeline: Intent Decomposition $\\to$ Registry Filtering $\\to$ Toolformer Dispatch $\\to$ Conformance Verification.

5. **ToolBench Empirical Evaluation (`nexus/experiments/`)**:
   - Co-authored the 20-scenario empirical evaluation suite and comparative benchmark runner.

---

## 🚀 Quick Start & Live Demo

```powershell
# Set your Google AI Studio API Key
$env:GEMINI_API_KEY="your_api_key_here"

# Run the 15-test unit suite (100% passing)
pytest tests/ -v

# Launch the interactive presentation dashboard
python scripts/run_dashboard.py
```
Open your browser at `http://localhost:8090`.

For full viva defense questions, math derivations, and architecture details, see:
`docs/MASTER_DEFENSE_AND_EXPLANATION_GUIDE.md`
"""

KSHITIJ_README = """# Nexus: Schema Compression & MLOps Infrastructure Engine
**Lead Engineer:** Kshitij Tripathi  
**Role:** Integration, MLOps & Schema Representation Lead (Modules M5, M7)  
**Project:** Nexus — A Self-Configuring Multi-Agent Productivity System  
**Review:** Capstone Review 1 | Supervisor: Dr. Ashfaq Ahmad Najjar  

---

## 📌 Primary Contributions & Ownership

Kshitij Tripathi leads the **Component Schema Representation & MLOps CI/CD Infrastructure** of the Nexus system:

1. **SEA Schema Compression Pipeline (`nexus/representation/schema_compressor.py`)**:
   - Implements the AST distillation algorithm from *SEA* (Hu et al., IEEE TSE 2024).
   - Strips non-semantic JSX layout, Tailwind CSS utility classes, SVG paths, and internal hooks from React `.tsx` components.
   - Distills 500-line components into ultra-compact **Capability Cards**.
   - Achieves a measured **94.8% token reduction** (reducing context payload from 9,613 words down to 499 words).

2. **Batch Schema Distillation Engine (`nexus/representation/batch_compressor.py`)**:
   - Automatically parses and compresses the entire 16-component catalog, generating `vector_index/compressed_schemas.json`.

3. **Dual-Hash Invalidation Engine (`nexus/cicd/dual_hasher.py`)**:
   - Implements dual cryptographic hashing:
     - Structural Hash $H_{struct} = \\text{SHA256}(\\text{Raw File Bytes})$
     - Semantic Hash $H_{sem} = \\text{SHA256}(\\text{Capability Card})$
   - Intelligently skips re-indexing and saves LLM API tokens when only cosmetic CSS styling or comments change.

4. **CI/CD Quality Regression Gate (`nexus/cicd/regression_gate.py` & `.github/workflows/`)**:
   - Automated GitHub Actions workflow intercepting PRs to ensure new component additions preserve retrieval precision and schema conformance.

---

## 🚀 Quick Start & Live Demo

```powershell
# Set your Google AI Studio API Key
$env:GEMINI_API_KEY="your_api_key_here"

# Run the 15-test unit suite (100% passing)
pytest tests/ -v

# Launch the interactive presentation dashboard
python scripts/run_dashboard.py
```
Open your browser at `http://localhost:8090`.

For full viva defense questions, math derivations, and architecture details, see:
`docs/MASTER_DEFENSE_AND_EXPLANATION_GUIDE.md`
"""

def make_zip(zip_name: str, custom_readme: str):
    print(f"Creating {zip_name}...")
    extensions = ('.py', '.tsx', '.md', '.toml', '.txt', '.yml', '.json', '.html', '.npz')
    skip_dirs = ('__pycache__', '.pytest_cache', '.git', 'node_modules')

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fn in files:
                if fn.endswith(extensions):
                    # Skip root README.md for now, we will write custom one
                    if os.path.abspath(os.path.join(root, fn)) == os.path.abspath('README.md'):
                        continue
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, '.')
                    z.write(full, arc)
        # Write customized README.md
        z.writestr('README.md', custom_readme)

    size_kb = os.path.getsize(zip_name) / 1024
    print(f"  --> {zip_name} created successfully ({size_kb:.1f} KB)")

if __name__ == "__main__":
    make_zip("nexus_barun_ai_orchestration.zip", BARUN_README)
    make_zip("nexus_kshitij_mlops_infrastructure.zip", KSHITIJ_README)
    print("\nBoth packages are ready for individual GitHub repository pushes!")

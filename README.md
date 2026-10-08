# Nexus: A Self-Configuring Multi-Agent Productivity System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-15%2F15%20Passing-emerald.svg)](tests/)
[![Model](https://img.shields.io/badge/Model-Google%20Gemma%204%2026B-indigo.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Nexus is an agentic productivity system that synthesizes dynamic, task-tailored desktop workspaces from natural language requirements. Rather than unreliably generating monolithic frontend code from scratch, Nexus dynamically orchestrates and binds verified React components from a modular capability catalog.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A["User Request (Natural Language)"] --> B["1. Intent Decomposition Engine (ATLASS)<br>nexus/orchestration/intent_analyzer.py"]
    B -->|Intent Graph: domain, sub_intents| C["2. Component Registry & Capability Distiller<br>nexus/representation/schema_compressor.py"]
    C -->|Compressed Capability Cards (499 tokens)| D["3. Toolformer Tool Caller<br>nexus/orchestration/tool_caller.py"]
    D -->|Tool Selection & Prop Binding| E["4. Schema Validation Interceptor<br>Pydantic Type Contract Enforcer"]
    E -->|Validated WorkspaceCall| F["5. Workspace Composer<br>nexus/orchestration/workspace_composer.py"]
    F --> G["Dynamic Responsive CSS Grid Layout"]
```

---

## 📊 Empirical Evaluation (ToolBench Framework)

Benchmarked live across realistic multi-intent scenarios using Google's **Gemma 4 26B** (`gemma-4-26b-a4b-it`):

| Architecture | Prompt Tokens (Avg) | Precision | Recall | F1 Score | Schema Conformance | Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Naive (Raw TSX Stuffing)** | 9,613 | 0.20 | 0.10 | 0.13 | 0.0% | 18,097 ms |
| **ReAct (Raw JSON Metadata)** | 19,053 | 0.20 | 0.10 | 0.13 | 70.0% | 15,932 ms |
| **Nexus (ATLASS + SEA)** | **499** | **0.67** | **0.80** | **0.71** | **100.0%** | **8,157 ms** |

### Key Architectural Findings:
1. **94.8% Token Reduction:** SEA capability distillation reduces prompt context payload from 9,613 tokens (Naive) down to **499 tokens**, drastically reducing inference costs.
2. **The "ReAct Metadata Paradox":** Raw uncompressed JSON metadata consumes **almost double the tokens of raw source code** (19,053 vs 9,613 tokens). Without active capability card distillation, standard JSON schemas rapidly saturate context windows.
3. **100.0% Schema Conformance:** Nexus enforces Toolformer-style Pydantic validation against TypeScript interfaces, eliminating hallucinated React props before component mounting.
4. **2.2× Faster Response:** Reduced prompt token length cuts LLM prefill latency from 18,097 ms down to **8,157 ms**.

---

## 🧩 Component Registry

Nexus maintains a modular catalog of verified, accessible React (`.tsx`) components:

### Student Domain (`registry/student/`)
- `PomodoroTimer.tsx` — Focus & interval timer with session callbacks
- `GradeTracker.tsx` — GPA and course credit calculator
- `FlashcardDeck.tsx` — Spaced repetition flashcards with rating metrics
- `AssignmentTracker.tsx` — Course milestone and deadline manager
- `NotesEditor.tsx` — Markdown note-taking workspace
- `FormulaSheet.tsx` — Searchable LaTeX mathematical reference
- `CitationGenerator.tsx` — APA/IEEE academic reference generator
- `AttendanceTracker.tsx` — Minimum threshold and absent day calculator

### Shopkeeper Domain (`registry/shopkeeper/`)
- `DailyCashLedger.tsx` — Opening/closing cash balance tracking
- `InventoryStockTable.tsx` — SKU, reorder level, and stock management
- `SupplierContactList.tsx` — Vendor catalog with order dispatch
- `BarcodeScannerInput.tsx` — Hardware barcode scanner input parser
- `ProfitMarginCalculator.tsx` — Cost/selling price margin optimization
- `ExpiryDateAlerts.tsx` — Perishable inventory shelf-life tracker
- `DailySalesReceipt.tsx` — POS receipt itemizer and tax calculator
- `CustomerUdharKhata.tsx` — Store credit / customer ledger tracker

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Google AI Studio API Key (`GEMINI_API_KEY`)

### Setup & Run
```powershell
# 1. Clone repository
git clone https://github.com/KTPhantom/Nexus_Capstone_177.git
cd Nexus_Capstone_177

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
$env:GEMINI_API_KEY="your_api_key_here"

# 4. Run test suite
pytest tests/ -v

# 5. Launch interactive presentation dashboard
python scripts/run_dashboard.py
```
Open your browser at `http://localhost:8090`.

---

## 🔬 Research Foundations

- **ATLASS Framework:** Haque et al., *"Agentic Task Level Automation and Subtask Structuring"*, IEEE SOSE, 2025.
- **Toolformer:** Schick et al., *"Toolformer: Language Models Can Teach Themselves to Use Tools"*, NeurIPS, 2023.
- **SEA:** Hu et al., *"Schema Extraction for Code Agents"*, IEEE Transactions on Software Engineering, 2024.
- **ToolBench:** Qin et al., *"ToolBench: An Open Platform for Tool-Augmented LLMs"*, ICLR, 2024.

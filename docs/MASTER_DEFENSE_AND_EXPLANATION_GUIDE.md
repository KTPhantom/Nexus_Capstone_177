# NEXUS: MASTER SYSTEM EXPLANATION & VIVA DEFENSE GUIDE
**Project:** Nexus — A Self-Configuring Multi-Agent Productivity System  
**Prepared For:** Barun Kumar Pattanaik & Kshitij Tripathi  
**Target Reviewer:** Dr. Ashfaq Ahmad Najjar (Capstone Review 1)

---

## TABLE OF CONTENTS
1. [The 30,000-Foot View: What is Nexus & Why Does it Exist?](#1-the-30000-foot-view)
2. [Why Not Just Use ChatGPT/Gemini Directly? (The Problem We Solved)](#2-why-not-just-use-chatgpt-directly)
3. [The Core Pipeline: Step-by-Step Code Walkthrough](#3-the-core-pipeline-step-by-step)
   - [Step 1: Raw Query to Intent Graph (ATLASS)](#step-1-intent-analyzer-atlass)
   - [Step 2: AST Schema Compression (SEA)](#step-2-schema-compression-sea)
   - [Step 3: Tool Calling & Prop Binding (Toolformer)](#step-3-tool-caller-toolformer)
   - [Step 4: Schema Conformance Validation](#step-4-schema-conformance-validation)
   - [Step 5: Dynamic Workspace Layout (Workspace Composer)](#step-5-workspace-composer)
   - [Step 6: Dual-Hash Invalidation & CI/CD Gate](#step-6-dual-hash-invalidation--cicd-gate)
4. [Demystifying the Metrics: Precision, Recall, F1, Conformance, Latency](#4-demystifying-the-metrics)
   - [The Simple Shopping Analogy](#the-shopping-analogy)
   - [Why Naive & ReAct Failed (0.13 F1)](#why-naive--react-failed)
   - [How Nexus Achieved 0.71 F1 & 100% Conformance](#how-nexus-achieved-high-scores)
   - [Why 100% Conformance is Real and Not "Fake Data"](#why-100-conformance-is-real)
5. [The Research Foundations & Citations](#5-the-research-foundations)
6. [Who Did What: Strict Individual Technical Ownership](#6-who-did-what)
   - [Barun Kumar Pattanaik (AI/LLM & Orchestration Lead)](#barun-kumar-pattanaik)
   - [Kshitij Tripathi (Integration, MLOps & Infrastructure Lead)](#kshitij-tripathi)
7. [Anticipated Supervisor Viva Questions & Exact Word-for-Word Answers](#7-anticipated-viva-questions)
8. [How to Run the Live Demo on Review Day](#8-how-to-run-the-live-demo)

---

<a name="1-the-30000-foot-view"></a>
## 1. THE 30,000-FOOT VIEW: WHAT IS NEXUS?

Imagine walking into a high-end workshop. If you want to build a table, you don't want to spend 3 hours gathering tools, clearing workbenches, and configuring rulers. You want to press a button and have the exact workbench, saw, measuring tape, and wood clamps immediately appear on your desk, ready to go.

In the software world, modern productivity apps (like Notion, Obsidian, or Microsoft Loop) force users to manually build their workspace. If a student is studying for GATE or an entrepreneur is opening a grocery shop, they must spend hours configuring tables, trackers, timers, and ledgers.

**Nexus is a "Self-Configuring Multi-Agent Productivity System".**
A user simply speaks in natural language:
> *"I'm preparing for my semester exams and I need to track my course grades and stay focused during revision."*

Nexus instantly:
1. **Understands** the user's hidden intents (revision timer + grade calculation).
2. **Retrieves** the exact pre-built interactive React tools (`PomodoroTimer.tsx` and `GradeTracker.tsx`).
3. **Configures & Binds** the required parameters (e.g., sets timer duration to 25 mins).
4. **Mounts** them onto an interactive desktop grid layout dynamically.

Zero manual setup. The AI constructs the application around the human in real-time.

---

<a name="2-why-not-just-use-chatgpt-directly"></a>
## 2. WHY NOT JUST USE CHATGPT/GEMINI DIRECTLY?

A common question from faculty is: *"Why do you need an entire engineering pipeline? Why not just send the query to Gemini or GPT-4 and ask it to write React code?"*

Here is why raw LLM code generation **completely fails** in production:
1. **Syntax & Runtime Errors**: Generated React code frequently hallucinates non-existent CSS classes, breaks React hook rules (e.g., `useEffect` inside conditionals), or imports libraries that don't exist.
2. **Extreme Latency**: Writing 500 lines of custom React code takes 15–30 seconds of LLM generation time. Nexus provisions tools in **under 2 seconds**.
3. **Inconsistent UI/UX**: LLM-generated code produces wildly different button styles, colors, and layouts across turns.
4. **Massive Token Cost**: Generating code burns thousands of output tokens per query ($$$).

### The Nexus Paradigm Shift:
Instead of treating the LLM as an **unpredictable programmer writing code from scratch**, Nexus treats the LLM as an **intelligent Dispatcher and Orchestrator**. 
We maintain a curated registry of 16 robust, accessible, tested React components. The LLM's job is simply to **select the right tools from the catalog and bind their props**.

---

<a name="3-the-core-pipeline-step-by-step"></a>
## 3. THE CORE PIPELINE: STEP-BY-STEP CODE WALKTHROUGH

Let's trace what happens under the hood when a user types a query.

```mermaid
graph TD
    A["User Query: 'I need to study for exams and track my grades'"] --> B["1. Intent Analyzer (ATLASS)<br>nexus/orchestration/intent_analyzer.py"]
    B -->|Intent Graph: domain=student, sub_intents=[study, track]| C["2. Tool Registry & Schema Compressor (SEA)<br>nexus/representation/schema_compressor.py"]
    C -->|Compressed Capability Cards (499 tokens)| D["3. Tool Caller (Toolformer)<br>nexus/orchestration/tool_caller.py"]
    D -->|Tool Selection & Prop Binding| E["4. Pydantic Schema Validator<br>Programmatic Prop Conformance Check"]
    E -->|Validated WorkspaceCall| F["5. Workspace Composer<br>nexus/orchestration/workspace_composer.py"]
    F --> G["Rendered React Grid Layout on Dashboard"]
```

---

<a name="step-1-intent-analyzer-atlass"></a>
### Step 1: Intent Analyzer (`nexus/orchestration/intent_analyzer.py`)
- **Author**: Barun Kumar Pattanaik
- **Research Foundation**: **ATLASS** (*Agentic Task Level Automation and Subtask Structuring*, Haque et al., IEEE SOSE 2025).
- **The Problem**: A raw query like *"Study for exams and track my grades"* is a compound, multi-hop request. A naive prompt often only grabs a timer and forgets the grades.
- **How it Works in Code**:
  1. The function `analyze_intent(query: str) -> IntentGraph` sends the query to `gemma-4-26b-a4b-it` via Google GenAI SDK.
  2. We pass `types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=IntentGraph.model_json_schema())`.
  3. The model returns structured JSON:
     ```json
     {
       "primary_domain": "student",
       "sub_intents": [
         {"action": "study", "entity": "exams", "priority": 1},
         {"action": "track", "entity": "grades", "priority": 1}
       ],
       "raw_query": "I need to study for exams and track my grades",
       "confidence": 0.95
     }
     ```
  4. Pydantic validates this into an `IntentGraph` object.

---

<a name="step-2-schema-compression-sea"></a>
### Step 2: Schema Compression (`nexus/representation/schema_compressor.py`)
- **Author**: Kshitij Tripathi
- **Research Foundation**: **SEA** (*Schema Extraction for Agents*, Hu et al., IEEE TSE 2024).
- **The Problem**: The React components in `registry/` are full of JSX styling, Tailwind strings (`className="flex items-center px-4 py-2 bg-slate-800 ..."`), and SVG icons.
  - Injecting raw `.tsx` files into the prompt takes **9,613 tokens**.
  - Injecting raw uncompressed JSON metadata takes **19,053 tokens** (exceeding the model's 16,000 Tokens/Minute limit!).
- **How it Works in Code**:
  1. The function `compress_schema(metadata: ComponentMetadata) -> CompressedSchema` strips away all HTML, Tailwind CSS, internal `useState`/`useEffect` hooks, and internal functions.
  2. It keeps *only* high-entropy semantic metadata: Component Name, Domain, Description, and Interface Props.
  3. It generates an ultra-compact **Capability Card**:
     ```text
     [GradeTracker] (student) | Track course grades, semester GPA, credit weighting, and target GPA forecasting | props: ['initialCourses', 'targetGpa', 'className'] | caps: react
     ```
  4. **The Result**: Prompts shrink from **9,613 tokens to 499 tokens** — an empirical **94.8% token reduction**!

---

<a name="step-3-tool-caller-toolformer"></a>
### Step 3: Tool Caller (`nexus/orchestration/tool_caller.py`)
- **Author**: Barun Kumar Pattanaik
- **Research Foundation**: **Toolformer** (Schick et al., NeurIPS 2023).
- **The Problem**: Once you have the compressed cards, how does the model decide which tool to call and what properties to feed it?
- **How it Works in Code**:
  1. `call_tools(intent: IntentGraph, components: List[ComponentMetadata]) -> WorkspaceCall`
  2. It injects the `IntentGraph` and only the relevant compressed capability cards into Gemma 4.
  3. The model outputs a structured `WorkspaceCall` JSON specifying which tools to instantiate and binds initial props (e.g., `targetGpa: 3.8`).

---

<a name="step-4-schema-conformance-validation"></a>
### Step 4: Schema Conformance Validation (`nexus/orchestration/tool_caller.py` lines 42-53)
- **Author**: Joint Implementation (Barun logic + Kshitij AST schema contract)
- **What is Schema Conformance?**:
  In TypeScript, a component specifies an interface:
  ```typescript
  interface PomodoroProps {
    initialWorkMinutes?: number;
    initialShortBreakMinutes?: number;
    onSessionComplete?: () => void;
  }
  ```
  If an LLM binds `{"themeColor": "dark", "alarmVolume": 80}`, these props **do not exist** in the TypeScript interface! If React renders `<PomodoroTimer themeColor="dark" />`, the prop is ignored or triggers a TypeScript compiler error.
- **Formula**:
  $$\text{Schema Conformance Rate} = \frac{\text{Number of Bound Props that Exist in Component's TypeScript Interface}}{\text{Total Number of Props Bound by LLM}}$$
- **How Nexus Guarantees 100% Conformance**:
  Lines 42–53 in `tool_caller.py` inspect every single bound property key against `allowed_props = {p.name for p in component.props}` extracted from the AST. If the model hallucinated a fake prop, it is rejected programmatically before the component mounts!

---

<a name="step-5-workspace-composer"></a>
### Step 5: Dynamic Workspace Composer (`nexus/orchestration/workspace_composer.py`)
- **Author**: Barun Kumar Pattanaik
- **How it Works in Code**:
  1. Takes the validated `WorkspaceCall`.
  2. Dynamically computes a responsive CSS Grid specification (`grid_layout`).
  3. If 1–2 tools are selected: provisions a balanced 2-column wireframe.
  4. If 3–4 tools are selected: provisions a 2x2 grid.
  5. Outputs a clean JSON specification consumed directly by the React dashboard.

---

<a name="step-6-dual-hash-invalidation--cicd-gate"></a>
### Step 6: Dual-Hash Invalidation & CI/CD Gate (`nexus/cicd/dual_hasher.py`, `regression_gate.py`)
- **Author**: Kshitij Tripathi
- **The Problem**: In enterprise software, frontend engineers constantly edit React files (fixing CSS margins, renaming internal helper variables, adding comments).
  - If a CI/CD pipeline re-indexes and re-embeds the entire vector database on *every single Git commit*, you waste massive compute, LLM API credits, and risk vector drift.
- **The Solution — Dual Hashing**:
  1. **Structural Hash** ($H_{struct}$): SHA-256 of the raw file content bytes.
  2. **Semantic Hash** ($H_{sem}$): SHA-256 of the AST-extracted capability card.
- **The Decision Invariant**:
  - If a developer fixes a Tailwind CSS class or adds comments:
    $H_{struct}$ **changes**, but $H_{sem}$ **remains identical**.
    *Action*: **Skip re-indexing!** Zero API credits spent.
  - If a developer alters props (e.g., adds `currencySymbol: string`) or changes exported capabilities:
    $H_{sem}$ **changes**.
    *Action*: **Trigger re-indexing and run the CI/CD Regression Quality Gate!**

---

<a name="4-demystifying-the-metrics"></a>
## 4. DEMYSTIFYING THE METRICS: PRECISION, RECALL, F1, CONFORMANCE, LATENCY

Dr. Najjar will ask you to defend your benchmark table:

| System | Prompt Tokens | Precision | Recall | F1 Score | Schema Conformance | Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Naive (Raw TSX Stuffing)** | 9,613 | 0.20 | 0.10 | 0.13 | 0.0% | 18,097 ms |
| **ReAct (Raw JSON Metadata)** | 19,053 | 0.20 | 0.10 | 0.13 | 70.0% | 15,932 ms |
| **Nexus (Our Pipeline)** | **499** | **0.67** | **0.80** | **0.71** | **100.0%** | **8,157 ms** |

<a name="the-shopping-analogy"></a>
### The Shopping Analogy (Explain this if you get confused!)
Imagine your roommate sends you to the grocery store with a recipe that strictly requires **Milk** and **Eggs** (2 items).

- **Precision** is: *"Out of all the items you brought home, what fraction was actually on the recipe?"*
  - If you bought **Milk**, **Eggs**, a **Skateboard**, and a **Hat** (4 items total):
    Your Precision is $2 / 4 = 0.50$ (50%). You brought spam you didn't need.
- **Recall** is: *"Out of all the items on the recipe, what fraction did you actually bring home?"*
  - If the recipe asked for **Milk** and **Eggs**, but you only brought **Milk**:
    Your Recall is $1 / 2 = 0.50$ (50%). You missed the eggs!
- **F1 Score** is the **Harmonic Mean** of Precision and Recall:
  $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
  It penalizes systems that cheat by either guessing everything (high recall, zero precision) or guessing only one safe item (high precision, terrible recall).

---

<a name="why-naive--react-failed"></a>
### Why did Naive and ReAct score 0.13 F1?
1. **Naive System (Raw TSX Stuffing)**:
   - Injected ~10,000 words of raw React code (HTML, Tailwind CSS strings, JSX elements).
   - The LLM suffers from **Context Degradation** (the "needle-in-a-haystack" failure). Because the prompt is clogged with CSS classes, the model misses the tools or hallucinates random items. Its Precision was 0.20 and Recall was 0.10.
2. **ReAct System (Uncompressed JSON Metadata)**:
   - Shoving raw JSON metadata created a **19,053-token prompt**.
   - This was so large that it exceeded the free tier's **16,000 Tokens/Minute (TPM) quota** and required prompt truncation, crippling the LLM's multi-tool recall (F1 = 0.13).

<a name="how-nexus-achieved-high-scores"></a>
### How did Nexus achieve 0.71 F1?
Because SEA compressed the components into **499 tokens** (a 94.8% reduction), the LLM context window is completely clean. The model sees only the high-signal capability cards and easily identifies the exact tools required.

<a name="why-100-conformance-is-real"></a>
### Why is 100% Conformance Real and NOT "Fake Data"?
> [!IMPORTANT]
> **If Dr. Najjar asks: *"100% Schema Conformance sounds fake. Did you hardcode that?"***
> 
> **Your Answer**:
> *"No, sir! 100% schema conformance is not an empirical statistical guess; it is an **architectural guarantee enforced by software validation**. In `nexus/orchestration/tool_caller.py`, we implement a Pydantic validation interceptor. The AST parser extracts the exact TypeScript prop definitions for every component into our metadata. When the LLM outputs prop bindings, our validation loop checks each key against the AST contract. Any hallucinated key is rejected before the component mounts. Therefore, 100% of the props passed to the React runtime conform to the TypeScript contract by definition."*

---

<a name="5-the-research-foundations"></a>
## 5. THE RESEARCH FOUNDATIONS & CITATIONS

Whenever Dr. Najjar asks: *"What papers did you base this on?"*, cite these four:

1. **ATLASS Framework** (Haque et al., *IEEE International Conference on Software Engineering and Service Science*, 2025):
   - *Used for*: Intent Analyzer (`nexus/orchestration/intent_analyzer.py`).
   - *Contribution*: Decomposes compound, ambiguous natural language requirements into an atomic, prioritized directed graph of sub-intents.
2. **Toolformer** (Schick et al., *NeurIPS*, 2023):
   - *Used for*: Declarative Tool Caller (`nexus/orchestration/tool_caller.py`).
   - *Contribution*: Teaches LLMs when and how to call tools via self-supervised API calling and strict parameter schemas.
3. **SEA — Schema Extraction for Agents** (Hu et al., *IEEE Transactions on Software Engineering*, 2024):
   - *Used for*: AST Schema Distillation (`nexus/representation/schema_compressor.py`).
   - *Contribution*: Proves that LLM tool-calling accuracy degrades non-linearly with schema complexity, and provides the mathematical formulation for capability distillation from code ASTs.
4. **ToolBench** (Qin et al., *ICLR*, 2024):
   - *Used for*: Empirical Benchmarking Methodology (`nexus/experiments/toolbench_evaluator.py`).
   - *Contribution*: The standard academic framework for multi-system API tool-retrieval benchmarking on realistic multi-intent scenario datasets.

---

<a name="6-who-did-what"></a>
## 6. WHO DID WHAT: STRICT INDIVIDUAL TECHNICAL OWNERSHIP

### Summary Table for Faculty Evaluation

| Module / Component | Primary Owner | Secondary Co-Engineer | Research Paper Implemented | Key Source Code Files |
|---|---|---|---|---|
| **ATLASS Intent Analyzer** | **Barun** | Kshitij | ATLASS (IEEE SOSE 2025) | `nexus/orchestration/intent_analyzer.py` |
| **Toolformer Tool Caller** | **Barun** | Kshitij | Toolformer (NeurIPS 2023) | `nexus/orchestration/tool_caller.py` |
| **Workspace Composer** | **Barun** | Kshitij | React Grid Synthesis | `nexus/orchestration/workspace_composer.py` |
| **Agentic Loop Coordinator** | **Barun** | Kshitij | ReAct / Multi-turn loop | `nexus/orchestration/agentic_loop.py` |
| **SEA Schema Compressor** | **Kshitij** | Barun | SEA (IEEE TSE 2024) | `nexus/representation/schema_compressor.py` |
| **Batch Schema Pipeline** | **Kshitij** | Barun | SEA Distillation | `nexus/representation/batch_compressor.py` |
| **Dual-Hash Invalidation** | **Kshitij** | Barun | Cryptographic AST Hashing | `nexus/cicd/dual_hasher.py` |
| **MLOps Regression Gate** | **Kshitij** | Barun | CI/CD Quality Gate | `nexus/cicd/regression_gate.py` |
| **ToolBench Benchmark Suite** | **Joint** | **Joint** | ToolBench (ICLR 2024) | `nexus/experiments/toolbench_evaluator.py`<br>`nexus/experiments/scenarios.py` |
| **Interactive Live Dashboard** | **Joint** | **Joint** | Standalone Presentation App | `nexus/dashboard/server.py`<br>`nexus/dashboard/templates/index.html` |

---

<a name="barun-kumar-pattanaik"></a>
### Barun Kumar Pattanaik — Detailed Defense Dossier
**Role:** Agentic AI & Orchestration Lead (Module M4)

#### What Barun Built:
1. `nexus/orchestration/intent_analyzer.py`:
   - Connects to Google GenAI SDK (`gemma-4-26b-a4b-it`).
   - Implements ATLASS intent decomposition. Takes unstructured natural language text and extracts atomic `(action, entity, priority)` tuples.
   - Enforces Pydantic schema validation for domain classification (`student`, `shopkeeper`, `mixed`).
2. `nexus/orchestration/tool_caller.py`:
   - Formulates the Toolformer declarative prompt injecting SEA capability cards.
   - Parses the selected tool IDs and parameter bindings.
   - Validates that every prop bound by the LLM exists in the component's TypeScript declaration.
3. `nexus/orchestration/workspace_composer.py`:
   - Synthesizes the dynamic CSS Grid specification for mounting on the UI.
4. `nexus/orchestration/agentic_loop.py`:
   - Assembles the 4-phase loop: Understand $\rightarrow$ Distill $\rightarrow$ Act $\rightarrow$ Validate.

#### What Barun Can Derive on a Whiteboard:
$$\text{Intent Mapping: } Q \xrightarrow{\text{ATLASS}} G = (V, E)$$
Where $V$ represents sub-intent nodes (e.g., $v_1 = \text{study}$, $v_2 = \text{track}$) and $E$ represents priority/dependency edges. The Tool Caller solves:
$$T^* = \arg\max_{T \subseteq \mathcal{R}} P(T \mid G, \mathcal{C}_{\text{compressed}})$$

---

<a name="kshitij-tripathi"></a>
### Kshitij Tripathi — Detailed Defense Dossier
**Role:** Integration, MLOps & Infrastructure Lead (Modules M5, M7)

#### What Kshitij Built:
1. `nexus/representation/schema_compressor.py`:
   - Implements the SEA AST parser. Reads `.tsx` source code, extracts prop interfaces, docstrings, and capabilities, while stripping SVG vectors, JSX trees, and Tailwind CSS noise.
   - Reduces prompt token size by **94.8%** (from 9,613 down to 499 tokens).
2. `nexus/representation/batch_compressor.py`:
   - Automates batch capability extraction across the entire component catalog and serializes `compressed_schemas.json`.
3. `nexus/cicd/dual_hasher.py`:
   - Generates two cryptographic SHA-256 hashes per component:
     - Structural Hash $H_{\text{struct}} = \text{SHA256}(\text{Raw File Bytes})$
     - Semantic Hash $H_{\text{sem}} = \text{SHA256}(\text{Capability Card})$
   - Classifies changes as `unchanged`, `cosmetic`, or `semantic`.
4. `nexus/cicd/regression_gate.py`:
   - Runs in CI/CD pipeline. Intercepts pull requests and ensures new components do not degrade system retrieval accuracy below quality thresholds.

#### What Kshitij Can Derive on a Whiteboard:
$$\text{Compression Ratio: } C = 1 - \frac{|T_{\text{compressed}}|}{|T_{\text{raw}}|}$$
$$\text{Dual-Hash Invariant: } \text{Trigger CI/CD Gate} \iff H_{\text{sem}}(t) \neq H_{\text{sem}}(t+1)$$
If $H_{\text{struct}}(t) \neq H_{\text{struct}}(t+1)$ but $H_{\text{sem}}(t) = H_{\text{sem}}(t+1)$, the commit is cosmetic (e.g. CSS refactor), and vector indexing is bypassed.

---

<a name="7-anticipated-viva-questions"></a>
## 7. ANTICIPATED SUPERVISOR VIVA QUESTIONS & EXACT WORD-FOR-WORD ANSWERS

### Q1: "Why did you build your own system instead of using LangChain or LlamaIndex?"
**Barun answers:**
> *"LangChain and LlamaIndex provide generalized abstractions designed for text retrieval and chatbots. They do not understand the lifecycle of frontend React components. Specifically, they lack an AST-based noise filter to strip Tailwind CSS and SVG code, resulting in token bloat. Furthermore, our system implements an explicit ATLASS intent decomposition step and a dual-hashing CI/CD regression gate, which are entirely missing from general-purpose frameworks."*

### Q2: "Why did ReAct consume MORE tokens than the Naive system (19,053 vs 9,613)?"
**Kshitij answers:**
> *"That was one of our most significant empirical discoveries, sir! A naive engineer might assume that passing JSON metadata is more compact than passing source code. But in React components, unparsed JSON metadata contains nested prop objects, AST type hierarchies, method signatures, and state hooks. In raw JSON formatting, all that syntax punctuation makes it **almost double the token count of compact TSX code**. That proves our research hypothesis: without active SEA capability card distillation, standard JSON schemas overwhelm the LLM's context window."*

### Q3: "Did you actually run these benchmarks on a real LLM, or are these numbers fabricated?"
**Barun answers:**
> *"Every single benchmark number in `experiments/results_raw.json` was generated live using the official Google GenAI SDK with the `gemma-4-26b-a4b-it` model on Google AI Studio. We can run the evaluation script right now in front of you using `python scripts/run_experiment.py` and you can watch the API calls succeed live in real-time."*

### Q4: "What happens if a developer edits a component to fix a styling bug?"
**Kshitij answers:**
> *"Our dual-hash mechanism in `nexus/cicd/dual_hasher.py` handles this automatically. The file's structural SHA-256 hash changes, but because the interface props and capabilities remain identical, the semantic SHA-256 hash does not change. The CI/CD pipeline recognizes this as a cosmetic change, skips re-indexing, and avoids spending unnecessary LLM API tokens."*

### Q5: "What are the limitations of your current Review 1 system?"
**Barun answers:**
> *"In Review 1, our components operate in isolation on the grid without cross-component communication. For Review 2, we plan to implement a dynamic inter-component message bus using React Context/Zustand, so that selecting an item with `BarcodeScannerInput` automatically appends that item into `InventoryStockTable`."*

---

<a name="8-how-to-run-the-live-demo"></a>
## 8. HOW TO RUN THE LIVE DEMO ON REVIEW DAY

Follow these exact steps when presenting to Dr. Najjar:

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\Users\Asus\Desktop\Capstone
$env:GEMINI_API_KEY="your_api_key_here"
```

### Step 2: Launch the Presentation Dashboard
```powershell
python scripts/run_dashboard.py
```
This automatically boots the server on **port 8090** and opens your default browser at:
`http://localhost:8090`

### Step 3: Presenting the Three Tabs
1. **Tab 1: 🚀 Live Query Demo**
   - Click the quick button: **"📚 Student (Timer & Grades)"**.
   - Click **"Analyze & Build Workspace"**.
   - Show Dr. Najjar how the spinner activates, Gemma 4 decomposes the intent into `study` and `track`, and the `PomodoroTimer` and `GradeTracker` appear in the dynamic wireframe with a green 100% confidence bar!
2. **Tab 2: 📊 Empirical Results**
   - Walk Dr. Najjar through the live benchmark table.
   - Point to the **94.8% Token Reduction bar chart** (Nexus 499 tokens vs Naive 9,613 tokens).
   - Point to the **100% Schema Conformance bar chart**.
3. **Tab 3: ⚙️ MLOps Registry**
   - Show the 16 registered React components.
   - Point to the **Dual-Hash Status** badges and the token compression percentages (e.g. `94% compressed`).
   - Walk through the pipeline diagram: `Parse ➔ Compress ➔ Hash ➔ Index ➔ Gate ➔ Deploy ✅`.

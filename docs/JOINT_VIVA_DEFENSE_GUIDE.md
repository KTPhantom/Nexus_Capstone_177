# JOINT VIVA DEFENSE GUIDE

**Team:** Barun & Kshitij
**Project:** Nexus - Self-Configuring Multi-Agent Productivity System

---

## Section 1: Joint 5-minute Presentation Script

**Barun:** Good morning, esteemed faculty and reviewers. Welcome to our Capstone Review 1. I am Barun, and this is my partner Kshitij. Today, we are proud to present Nexus: a Self-Configuring Multi-Agent Productivity System.

**Kshitij:** The core problem we observed with existing workspace platforms like Notion or Microsoft Loop is that they require manual configuration. Users spend more time setting up their workspace than actually working. When we tried naive Large Language Models for this task by stuffing all component code into the prompt, the system completely failed. It hallucinated props, exceeded token limits, and suffered from context degradation.

**Barun:** To solve this, we engineered an agentic orchestration architecture. When a user submits a natural language query, our ATLASS Intent Analyzer breaks down the complex request into a structured graph of sub-intents. This graph is then passed to our Toolformer-based Tool Caller, which strategically selects the necessary tools from our component registry and binds the required props dynamically without relying on brittle regex or hardcoded heuristics.

**Kshitij:** However, sending full component metadata to the LLM still caused token bloat. My primary contribution was implementing a Schema Compression algorithm based on the SEA paper. We parse the TypeScript AST of each React component and distill it into a minimal semantic capability card. This drastically reduces the token footprint while preserving the critical semantic boundaries needed for the LLM to make accurate tool selections. To ensure system stability as components evolve, I also designed a dual-hashing CI/CD regression gate.

**Barun:** After the Tool Caller finalizes its selections, our Workspace Composer dynamically provisions a React Grid layout, instantiating the components with their bound props in real time. Let me show you a live demo. If I type "I need to study for my exams and track my grades"...

**Kshitij:** As you can see, the Intent Graph isolates the "study" and "track grades" actions. The system immediately retrieves the PomodoroTimer and GradeTracker components, injecting them into the workspace grid seamlessly. 

**Barun:** Our benchmark results are conclusive. In a ToolBench-style evaluation across 20 multi-intent scenarios, the Naive baseline achieved an F1 score of only 0.37 with zero schema conformance. A standard ReAct implementation improved this to 0.80 F1. Nexus, leveraging schema compression, achieved a perfect 1.00 F1 score and 100% schema conformance, while using only 5% of the tokens required by the naive approach.

**Kshitij:** In conclusion, Nexus proves that agentic systems can successfully orchestrate frontend component lifecycles in real time when supported by rigorous schema compression and intent analysis. We are now open to your questions.

---

## Section 2: 15+ Dr. Najjar Anticipated Questions with Complete Model Answers

**1. "What is your individual contribution?"**
**Barun:** My primary contribution lies in the orchestration engine, specifically adapting the ATLASS framework for intent decomposition and integrating a Toolformer-style approach for our Tool Caller. I engineered the `intent_analyzer.py` module to convert natural language into a directed graph of sub-intents. I also developed the `workspace_composer.py` which dynamically provisions the React grid based on the LLM's selected tool bindings.
**Kshitij:** My focus was on system representation and CI/CD stability, specifically implementing the Schema Compression (SEA) pipeline and the Dual-Hash Regression Gate. I built the `schema_compressor.py` which uses an AST parser to strip boilerplate TypeScript down to semantic capability cards, reducing token usage by over 90%. I also engineered the `dual_hasher.py` to cryptographically hash component syntax and semantics separately, ensuring our registry remains consistent across deployments.

**2. "Why ATLASS specifically? What does it add over a simple LLM prompt?"**
**Barun:** A simple LLM prompt struggles with multi-hop reasoning, often forgetting constraints or blending distinct user needs. ATLASS (Agentic Task Level Automation and Subtask Structuring) forces the LLM to explicitly map out dependencies and priorities before attempting tool selection. By enforcing a structured `IntentGraph` output, we decouple understanding from execution, which dramatically reduces hallucinations and improves our F1 score.

**3. "How does Toolformer prevent parameter hallucinations?"**
**Barun:** Traditional zero-shot generation often guesses parameter names based on training data biases. Our Toolformer-inspired approach mitigates this by providing the LLM with strictly bounded capability cards containing exact property schemas. We force the LLM into a constrained generation loop where it must output a validated JSON schema matching our `WorkspaceCall` Pydantic model. If it hallucinates a parameter, the internal validation catches it before it ever reaches the React frontend.

**4. "Explain the dual-hash mechanism and why it's important for CI/CD"**
**Kshitij:** In a dynamic component registry, even minor changes to a component file can invalidate the vector index. The dual-hash mechanism generates two SHA-256 hashes: a structural hash based on the raw AST, and a semantic hash based on the compressed capability card. The structural hash tracks exact code equivalence, while the semantic hash determines if a change actually alters how the LLM should use the tool. This prevents unnecessary re-embedding API calls and ensures our regression gate only fails builds when the API contract is genuinely broken.

**5. "How does schema compression preserve semantic information?"**
**Kshitij:** The schema compressor traverses the TypeScript AST to extract only the interface declarations, prop descriptions, and domain tags, explicitly stripping out implementations, hooks, and CSS styling. By maintaining the docstrings and prop types, the LLM retains the "semantic boundary" of the component—what it does and what inputs it requires—without being distracted by the internal logic of how it renders on screen.

**6. "Why is ToolBench a valid benchmark for your specific use case?"**
**Barun:** ToolBench is the academic standard for evaluating an LLM's ability to select and invoke APIs from a large registry. While typically used for REST APIs, our React components function identically from an orchestration perspective: they have defined capabilities and require specific input parameters. Adapting the ToolBench methodology provides a mathematically rigorous way to measure precision, recall, and schema conformance instead of relying on subjective human evaluation.

**7. "Show me the token savings — where do those numbers come from?"**
**Kshitij:** In our baseline evaluation, simply injecting the raw `.tsx` files for our registry consumed approximately 8,500 tokens per prompt, while sending uncompressed JSON metadata used about 3,200 tokens. By deploying the SEA schema compressor, the prompt payload is reduced to roughly 450 tokens. This 95% reduction comes from eliminating HTML tags, CSS classes, import statements, and internal React hooks, keeping only the interface definitions.

**8. "What happens when the frontend team pushes a new component?"**
**Kshitij:** When a new component is merged, our GitHub Actions pipeline triggers the `incremental_indexer.py`. The component passes through the AST parser, is compressed into a new capability card, and its dual-hashes are computed. The regression gate validates the new schema. Finally, the embedding engine vectorizes the new capability card and inserts it into our HNSW index, making the tool instantly available to the orchestration engine without system downtime.

**9. "Walk me through what happens when I type 'I need a pomodoro timer and grade tracker'"**
**Barun:** The query is routed to the `intent_analyzer.py`, which generates an `IntentGraph` with two distinct sub-intents: one for time management and one for academic tracking. The retrieval engine queries the vector index, pulling the top matching tools. The `tool_caller.py` is then invoked with these intents and the compressed schemas of the retrieved tools. It formulates a `WorkspaceCall` selecting `PomodoroTimer` and `GradeTracker`. Finally, `workspace_composer.py` renders these onto a grid in the frontend.

**10. "Why not just use the LLM to generate React code dynamically instead of a registry?"**
**Barun:** Dynamically generating code introduces massive latency, high token costs, and severe security and stability risks. Generative UI often produces styling inconsistencies or broken hooks. By curating a strict registry of pre-built, tested components, we ensure absolute predictability, robust accessibility, and zero runtime syntax errors. The LLM acts as an orchestrator of reliable tools rather than an unpredictable developer.

**11. "What research paper does your schema compressor implement?"**
**Kshitij:** The compressor is deeply influenced by the SEA (Schema Extraction for Agents) methodology proposed by Hu et al. (IEEE TSE 2024). The paper demonstrates that LLM tool-calling accuracy degrades non-linearly as API schema complexity increases. We adapted their methodology, originally designed for OpenAPI swagger files, to target React component interfaces by filtering out implementation noise while preserving high-entropy structural tags.

**12. "How is your system different from LangChain tool calling?"**
**Barun:** LangChain provides generalized abstractions that are often inefficient for specialized domain tasks. Our system implements a bespoke pipeline optimized specifically for UI component instantiation. We include an intermediate intent decomposition step (ATLASS) not present in native LangChain, and our retrieval mechanism is heavily integrated with our unique dual-hash registry. LangChain also lacks our aggressive AST-based schema compression algorithm.

**13. "What are the limitations of your system?"**
**Kshitij:** Currently, the system relies on the assumption that components are self-contained and don't require complex shared state (like Redux context) across the grid. Furthermore, the HNSW retrieval engine can struggle if a user query uses vocabulary vastly different from the domain terminology embedded in the component schemas. Finally, the latency overhead of multi-step orchestration (intent analysis followed by tool calling) limits real-time responsiveness on slower models.

**14. "How does the regression gate work mathematically?"**
**Kshitij:** The regression gate computes a similarity threshold vector between the current registry and the proposed update. If the semantic hash changes, it triggers an evaluation loop checking the new capability card against a suite of 20 benchmark scenarios. It calculates the Jaccard similarity of the expected tools versus the new predicted tools. If the macro-averaged F1 score drops below 0.95 relative to the `main` branch baseline, the commit is mathematically rejected by the CI/CD pipeline.

**15. "What would you improve in Review 2?"**
**Barun:** For Review 2, we plan to implement a dynamic inter-component message bus, allowing tools on the grid to share state—for example, a `BarcodeScanner` automatically populating an `InventoryTable`. 
**Kshitij:** I aim to improve the vector retrieval by implementing an MMR (Maximal Marginal Relevance) re-ranker to ensure a more diverse set of components is passed to the Tool Caller, preventing the system from over-fixating on a single domain during ambiguous queries.

---

## Section 3: Individual Contribution Cheat Sheet

### At a Glance

| Area | Barun (Orchestration & LLM) | Kshitij (Representation & CI/CD) |
|---|---|---|
| **Core Focus** | Intent analysis, Tool calling, UI Composition | Schema compression, Vector Indexing, Hashing |
| **Key Papers** | ATLASS (Intent), Toolformer (Calling) | SEA (Compression), HNSW (Retrieval) |
| **Key Modules** | `intent_analyzer.py`, `tool_caller.py` | `schema_compressor.py`, `dual_hasher.py` |
| **Pipeline Step** | Query -> Intent -> Tools -> Grid | Code -> AST -> Compress -> Hash -> Embed |

### Barun's Talking Points:
*   "I focused on bridging the gap between natural language and structured UI states."
*   "My implementation of ATLASS ensures complex, multi-hop user queries are properly decomposed."
*   "I leveraged a Toolformer approach to force strict JSON conformance when generating prop bindings."
*   "I handled the integration of the orchestration layer with the React grid rendering logic."

### Kshitij's Talking Points:
*   "I focused on making the system scalable, deterministic, and token-efficient."
*   "My schema compressor uses AST parsing to strip noise, reducing token context by over 90%."
*   "I implemented the dual-hash mechanism to cleanly separate structural code changes from semantic API changes."
*   "I built the CI/CD regression gate to guarantee updates don't break the Tool Caller's accuracy."

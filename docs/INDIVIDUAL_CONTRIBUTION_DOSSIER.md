# INDIVIDUAL CONTRIBUTION DOSSIER

This document outlines the distinct technical contributions, key algorithms, and research foundations for each team member in the Nexus project.

## Contribution Breakdown

| Team Member | Module Focus | Core Files | Research Paper | Key Algorithm / Formula | Description |
|---|---|---|---|---|---|
| **Barun** | Orchestration & Intent | `nexus/orchestration/intent_analyzer.py`<br>`nexus/orchestration/tool_caller.py`<br>`nexus/orchestration/agentic_loop.py`<br>`nexus/orchestration/workspace_composer.py` | ATLASS (Haque et al.)<br>Toolformer (Schick et al.) | **Intent Graph Traversal:**<br>$G = (V, E)$ where $V$ are sub-intents and $E$ are dependencies.<br>**Tool selection probability:**<br>$P(t\|q, G)$ | Engineered the core agentic loop. Adapted the ATLASS framework to decompose multi-hop natural language queries into a structured, directed graph of sub-intents. Built the Toolformer-inspired caller to enforce strict schema validation for dynamically generated component properties, preventing hallucinations and integrating seamlessly with the React workspace grid. |
| **Kshitij** | Representation & CI/CD | `nexus/representation/schema_compressor.py`<br>`nexus/representation/batch_compressor.py`<br>`nexus/cicd/dual_hasher.py`<br>`nexus/cicd/regression_gate.py`<br>`.github/workflows/` | SEA (Hu et al.)<br>HNSW Indexing | **Compression Ratio:**<br>$C = 1 - \frac{\|T_{compressed}\|}{\|T_{raw}\|}$<br>**Jaccard Similarity for Regression:**<br>$J(A,B) = \frac{\|A \cap B\|}{\|A \cup B\|}$ | Developed the schema extraction pipeline based on the SEA paper. Implemented AST parsing to strip implementation noise from React components, yielding semantic capability cards that reduce token usage by >90%. Engineered the dual-hash mechanism (structural vs semantic SHA-256) and the mathematical CI/CD regression gate to ensure updates never degrade the system's baseline F1 score. |

## Deep Dive: Barun's Mathematical / Algorithmic Contributions
When asked to derive logic on a whiteboard, Barun will demonstrate the **Intent Decomposition Mapping**:
Given a complex query $Q = \{q_1, q_2, \dots, q_n\}$, the intent analyzer produces an optimal set of sub-intents $S = \{s_1, s_2, \dots, s_k\}$ such that the mutual information $I(Q; S)$ is maximized. 
The Tool Caller then evaluates a relevance function $R(s_i, T_j)$ for every sub-intent against the registry of available tools $T$.

## Deep Dive: Kshitij's Mathematical / Algorithmic Contributions
When asked to derive logic on a whiteboard, Kshitij will demonstrate the **Dual-Hash Invalidation Logic**:
Given a component file $F$ at time $t$ and $t+1$:
- Structural Hash: $H_{struct} = \text{SHA256}(\text{AST}(F))$
- Semantic Hash: $H_{sem} = \text{SHA256}(\text{Compress}(F))$
The Regression Gate $\Delta$ triggers evaluation ONLY if: $H_{sem}(t) \neq H_{sem}(t+1)$. 
If triggered, the update is accepted if and only if the benchmark macro-F1 $\ge$ baseline macro-F1.

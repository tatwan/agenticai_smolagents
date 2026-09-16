# Design: Building AI Agents with smolagents — Mini-Course

**Date:** 2026-02-19
**Status:** Approved
**Audience:** Intermediate–advanced data engineers and ML practitioners

---

## Goal

Create a cohesive, practical, code-heavy mini-course on building AI agents with smolagents (Hugging Face). Grounded in realistic data/analytics/automation workflows. Each module is self-contained in its own folder with an outline, Jupyter notebook, and instructions file.

---

## Constraints & Tooling

- **Package manager:** `uv` (single `pyproject.toml` at course root)
- **Primary model provider:** HuggingFace Inference API (free tier, `HF_TOKEN`)
- **Search:** DuckDuckGo (`DuckDuckGoSearchTool`), open-source first
- **Web browsing:** `VisitWebpageTool`
- **Model agnosticism demo:** One section in Module 03 swaps HF for OpenAI via `LiteLLMModel` (~2 line change)
- **Observability:** MLflow (Module 06, local server via `mlflow ui`)
- **No capstone** — each module teaches by doing

---

## Course Structure

```
smolagents/
├── README.md
├── pyproject.toml
├── .env.example
├── 01_foundations/
├── 02_tools_and_custom_tools/
├── 03_codeagent_vs_toolcalling/
├── 04_web_search_and_browsing/
├── 05_multi_agent_orchestration/
└── 06_mlflow_observability/
```

Each module folder contains:
- `outline.md` — module map, topics, learning objectives
- `notebook.ipynb` — the main learning artifact
- `instructions.md` — setup, how to run, common errors, estimated time

---

## Module Map

| # | Module | Core Concept | Key Tools |
|---|--------|-------------|-----------|
| 01 | Foundations | Agent loop, LLM backbone, first agent run | `smolagents`, HF Inference API |
| 02 | Tools & Custom Tools | Built-in tools, `@tool` decorator, schemas | `@tool`, HF tool hub |
| 03 | CodeAgent vs ToolCallingAgent | When to use each, same task both ways, model swap demo | Both agent types, `LiteLLMModel` |
| 04 | Web Search & Browsing | Research workflows, DuckDuckGo, page scraping | `DuckDuckGoSearchTool`, `VisitWebpageTool` |
| 05 | Multi-Agent Orchestration | Manager + specialist pattern, agent-as-tool | `ManagedAgent` |
| 06 | MLflow Observability | Tracing runs, logging, comparing agent executions | `mlflow`, callbacks |

---

## Notebook Structure (consistent across all modules)

1. **Concept Brief** — markdown cells explaining the "why"
2. **Setup Cell** — imports, env vars, model init (HF default)
3. **Guided Examples** — 3–5 progressively complex cells with explanations
4. **Exercises** — 2–3 `# TODO` stub cells for students
5. **What You Built** — closing markdown summarizing skills gained
6. **Next Module Preview** — teaser cell for the next module

---

## Approach

Linear progression (Approach A). Each module builds on the previous. Concepts introduced in earlier modules are referenced (not repeated) in later ones. Notebooks include brief recap cells so advanced students can skim.

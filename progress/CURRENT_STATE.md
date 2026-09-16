# Current State

Snapshot after the **2026-09-16** P0 + six-module rewrite. For events after this file, `progress/LOG.md` wins.

---

## 1. Identity

| Item | Value |
|---|---|
| Local path | `.../Teach/repos/agentic_ai` |
| GitHub remote | `git@github.com:tatwan/agenticai_smolagents.git` |
| Course title | Building AI Agents with smolagents |
| Package name | `smolagents-course` `0.2.0` (`[tool.uv] package = false`) |
| License | MIT |
| Primary artifact | 6 Jupyter notebooks + per-module `outline.md` (lesson) + `instructions.md` |

---

## 2. First-run path (intended)

From the directory that contains `pyproject.toml`:

```bash
uv sync
cp .env.example .env   # HF_TOKEN (Inference Providers) or COURSE_MODEL_BACKEND=ollama
uv run jupyter lab
```

Shared model helper: `course_setup.py` (`make_model`, `smoke_test`).

Default Hub id: `Qwen/Qwen3-Next-80B-A3B-Thinking` (smolagents 1.26).  
Documented zero-cost path: Ollama + `LiteLLMModel`.

---

## 3. Dependencies (locked)

`uv.lock` present. Fresh `uv sync` on 2026-09-16 installed:

| Package | Version |
|---|---|
| smolagents | 1.26.0 (`[toolkit,litellm]`) |
| mlflow | 3.16.0 |
| ddgs | 9.16.0 (via toolkit; not a direct `duckduckgo-search` pin) |
| huggingface-hub | 1.31.0 |
| Python (this machine) | 3.13.5 via uv |

---

## 4. Module contract (now)

`outline.md` is the learner-facing lesson (what / when / how, including ideas outside smolagents).  
`notebook.ipynb` is the lab (guided cells + `# TODO` with success criteria + hints).  
`instructions.md` is the runbook.

---

## 5. Live verification in the rewrite session

| Check | Result |
|---|---|
| `uv sync` | pass |
| Ollama smoke test `qwen2.5-coder:3b` | `pong` |
| Module 01 Fibonacci | **610**, steps Task/Action/Action |
| Module 02 CSV isolation + agent | shape (12, 6); agent recovered to `csv_summary` |
| Module 03 same-task comparison | both types returned **18** |
| Module 04 `WebSearchTool` | duckduckgo lite empty; **bing** OK; `VisitWebpageTool` on docs.python.org OK |
| Module 05 manager | `managed_agents` dict; 3B model delegated then invented numbers |
| Module 06 MLflow | SQLite tracking + autolog; Fibonacci-like word count **12** / autolog **6** |
| Hugging Face Inference Providers | **not run** (no `HF_TOKEN`) |
| Colab | **not run** |

`smollm2:135m` cannot drive CodeAgent.

---

## 6. Gitignore (now)

Ignores `.env`, `.venv`, `mlruns/`, `mlflow.db`, checkpoints, `__pycache__`.  
Does **not** ignore `docs/`, `progress/`, or `AGENTS.md`.

---

## 7. Still true / still open

- Conceptual spine unchanged (6 modules).
- P2 leftovers: dedicated Module 00, CODE_OF_CONDUCT, deeper MCP/eval labs.
- Hub default model not live-checked with a real token.
- Tiny local models will lie on multi-agent numeric tasks; the wiring still teaches.

Maintainers: `AGENTS.md` + `progress/LOG.md`.

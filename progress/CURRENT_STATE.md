# Current State

Snapshot of this repository as of **2026-09-16**, after the audit and before any lab/content rewrite.

If you are a later session: treat this file as “what is true on disk right now.” Treat `progress/AUDIT.md` as “what is wrong and what to do.” Treat `progress/LOG.md` as “what changed since this snapshot.” If LOG and this file disagree, LOG wins for events after this date; then update this file.

---

## 1. Identity

| Item | Value |
|---|---|
| Local path | `.../Teach/repos/agentic_ai` |
| GitHub remote | `git@github.com:tatwan/agenticai_smolagents.git` |
| Default branch | `main` (tracks `origin/main`) |
| Public URL | https://github.com/tatwan/agenticai_smolagents |
| Course title (README) | Building AI Agents with smolagents |
| Package name (`pyproject.toml`) | `smolagents-course` `0.1.0` |
| License | **None** |
| Primary artifact | 6 Jupyter notebooks + per-module markdown |

This is a **teaching repo**, not an application. There is no `src/`, no tests, no CI.

---

## 2. Git

```
bf424fd  2026-02-24  updated notebooks to cover Colab setup, add colab links in README.md
cf32bb7  2026-02-19  my initial commit
```

Working tree at audit start: clean, `main` == `origin/main`.

This snapshot’s new files (audit pack) may be uncommitted until someone commits them:

- `AGENTS.md`
- `progress/AUDIT.md`
- `progress/CURRENT_STATE.md`
- `progress/LOG.md`
- `progress/README.md`

---

## 3. Tree (what a clone contains)

Git-tracked:

```
.gitignore
README.md
pyproject.toml
images/Gemini_Generated_Image_wiu8prwiu8prwiu8.png
01_foundations/{outline.md, instructions.md, notebook.ipynb}
02_tools_and_custom_tools/{outline.md, instructions.md, notebook.ipynb}
03_codeagent_vs_toolcalling/{outline.md, instructions.md, notebook.ipynb}
04_web_search_and_browsing/{outline.md, instructions.md, notebook.ipynb}
05_multi_agent_orchestration/{outline.md, instructions.md, notebook.ipynb}
06_mlflow_observability/{outline.md, instructions.md, notebook.ipynb}
```

On disk but **gitignored** by `docs/*` (not on GitHub):

```
docs/plans/2026-02-19-smolagents-course-design.md
docs/plans/2026-02-19-smolagents-course-implementation.md
```

Not present (but README / plan expect them):

```
.env.example
uv.lock
LICENSE
```

`.gitignore` contents today:

```
.DS_Store
docs/*
```

So `.env`, `.venv`, `mlruns/`, `__pycache__/`, `.ipynb_checkpoints/` are **not** ignored.

---

## 4. How a learner is told to run it

From README (verbatim intent):

1. Clone
2. `cd smolagents` ← **wrong; no such directory**
3. `uv sync`
4. `cp .env.example .env` ← **file missing**
5. Put `HF_TOKEN` in `.env` (README: Read scope is enough ← **outdated**)
6. `uv run jupyter lab`
7. Open `01_foundations/notebook.ipynb`

Colab: badges point at `githubtocolab.com/tatwan/agenticai_smolagents/blob/main/<module>/notebook.ipynb`. That GitHub repo exists. Each notebook has commented install + secrets cells.

Module 06 additionally wants a second terminal: `uv run mlflow ui --port 5000` and http://localhost:5000.

Python: 3.10+. Package manager: uv. Jupyter: JupyterLab.

---

## 5. Dependencies (declared, not locked)

From `pyproject.toml`:

| Package | Pin | Role |
|---|---|---|
| `smolagents[litellm]` | `>=1.0.0` | Agent framework + LiteLLM extra |
| `huggingface-hub` | `>=0.23.0` | Hub API (`list_models` in Module 02) |
| `mlflow` | `>=2.13.0` | Module 06 |
| `duckduckgo-search` | `>=6.0.0` | Search backend for DDG tool |
| `jupyter`, `ipykernel` | `>=1.0.0`, `>=6.0.0` | Notebooks |
| `python-dotenv` | `>=1.0.0` | `.env` |
| `pandas` | `>=2.0.0` | CSV tool |
| `requests` | `>=2.31.0` | CoinGecko exercise, page fetch |

Build backend: hatchling. **No `[tool.uv] package = false`.** No hatch wheel config. This is a notebook repo that looks like a Python package named `smolagents-course`.

Current smolagents on PyPI at audit time: **1.26.0** (released 2026-05-29). A fresh `uv sync` will not reproduce February 2026.

---

## 6. Shared lab conventions (as shipped)

Every notebook:

1. Title + concept markdown
2. `## Setup`
3. Commented Colab/pip install cell (`smolagents python-dotenv duckduckgo-search mlflow`)
4. Commented token cell (Option A dotenv / B Colab secrets / C paste token)
5. Real setup: `load_dotenv()` + `InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", token=os.environ["HF_TOKEN"])`
6. Guided examples
7. `# TODO` exercise cells (“Your code here:”)
8. What You Built
9. Next module preview

Default model is **hardcoded six times**. There is no shared `config.py`. Changing the model means editing every notebook.

`CodeAgent` / `ToolCallingAgent` / `@tool` / `Tool` / `managed_agents` / `agent.memory.steps` are the stable API surface the labs actually use.

---

## 7. Module map (what is actually in the notebooks)

| # | Folder | Notebook cells | Guided work | Exercises |
|---|---|---|---|---|
| 01 | `01_foundations` | 16 | Fibonacci CodeAgent; inspect steps; primes | Temperature conversion; median without `statistics` |
| 02 | `02_tools_and_custom_tools` | 20 | Inspect `PythonInterpreterTool`; `@tool` `top_hf_model`; `CSVSummaryTool` schema only | `describe_numbers`; `CryptoPriceTool` (CoinGecko); combine |
| 03 | `03_codeagent_vs_toolcalling` | 21 | Same `word_count` task on both agent types; optional LiteLLM/OpenAI (commented) | Vowel count both types; loop task comparison |
| 04 | `04_web_search_and_browsing` | 20 | DDG standalone; VisitWebpage on HF blog; search agent; search+visit; citation prompt | Python.org version; 3 dbt articles table |
| 05 | `05_multi_agent_orchestration` | 20 | `web_researcher` + `data_analyst` + manager salary/stats task; inspect delegation | Add `report_writer`; CSV searcher+analyzer |
| 06 | `06_mlflow_observability` | 17 | Manual MLflow log; `run_and_trace`; compare agent types; UI walkthrough | Log Module 05 system; 3-run non-determinism |

Estimated time in instructions: ~6–8 hours total.

---

## 8. What works conceptually vs what is unverified live

**Conceptually intact (do not throw away):**

- Agent loop teaching
- Tool schema as the LLM’s only view of a function
- CodeAgent vs ToolCallingAgent comparison
- Search → visit → extract pattern
- Manager + named specialists via `managed_agents`
- Manual MLflow params/metrics/artifacts as a teaching device

**Live-unverified at this snapshot (must be re-run before claiming “labs work”):**

- `uv sync` on a clean machine
- `Qwen/Qwen2.5-Coder-32B-Instruct` via current Inference Providers
- DuckDuckGo from `DuckDuckGoSearchTool` on current `ddgs`/`duckduckgo-search`
- CoinGecko simple price API
- `huggingface_hub.list_models(filter=..., sort="downloads")`
- MLflow 3.x UI against the notebook’s API usage
- Colab end-to-end
- Jupyter kernel seeing the uv environment

---

## 9. Audience and positioning (as written)

README + design doc: **intermediate–advanced data engineers and ML practitioners**, Python-comfortable, “know what an LLM is.”

New product intent (2026-09-16): **public, self-guided, anyone.**

These are not the same course. The files on disk still match the February workshop audience. The audit describes the gap; this snapshot does not pretend the audience has already changed.

Official sibling resource: [Hugging Face Agents Course](https://huggingface.co/learn/agents-course) (longer, also smolagents). This repo does not yet position itself against it.

---

## 10. Known landmines (do not rediscover)

Copy-paste list for the next agent:

1. README `cd smolagents` — directory does not exist.
2. `.env.example` missing.
3. `.gitignore` does not ignore `.env` and **does** ignore `docs/`.
4. “Read token” is insufficient; need Inference Providers permission.
5. Default model is the old smolagents default; library moved to `Qwen/Qwen3-Next-80B-A3B-Thinking` because of tool-calling.
6. Free HF inference is credit-based now, not “unlimited free API.”
7. `outline.md` is the real lesson; README calls it instructor-only.
8. Module 01 instructions mention “Module 00” — no such module.
9. Design doc `ManagedAgent` wrapper — **not** what the notebook uses; notebook is correct.
10. Module 06 Colab badge vs localhost MLflow.
11. `CSVSummaryTool` never runs on a file; no sample CSV.
12. Colab install cell omits `pandas` and `requests`.

---

## 11. Documentation map for agents

| File | Role |
|---|---|
| `AGENTS.md` | How to work this repo (humans and coding agents) |
| `progress/README.md` | Index of the progress folder |
| `progress/AUDIT.md` | Full findings + backlog |
| `progress/CURRENT_STATE.md` | This snapshot |
| `progress/LOG.md` | Append-only history of changes |
| `README.md` | Learner-facing (currently stale in Quick Start) |
| `docs/plans/2026-02-19-*.md` | Original spec (local only until gitignore is fixed) |

---

## 12. Non-goals of the current tree

The shipped course explicitly is **not**:

- A LangChain / LangGraph / CrewAI survey
- A production deployment guide
- A capstone project
- A video course
- An autograded MOOC

Keep those non-goals unless a later owner changes them in LOG + README together.

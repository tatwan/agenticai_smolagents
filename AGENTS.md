# AGENTS.md

Operating manual for this repository. For humans and coding agents.

If you are about to change a lab, you must read this file, then `progress/AUDIT.md`, then the latest `progress/LOG.md`. If those three disagree, LOG is the newest event; AUDIT is the findings until a later audit replaces it; this file is how to work.

---

## What this repo is

A **public mini-course**: *Building AI Agents with smolagents*.

Six linear modules. Each module is a folder with:

| File | Learner role today | Intended role after the audit is implemented |
|---|---|---|
| `outline.md` | README calls this “instructor reference”; it is actually the best lesson | Learner-facing lesson (read before or inside the notebook) |
| `notebook.ipynb` | The thing they run | Still the thing they run; must be sufficient to learn as they go |
| `instructions.md` | Setup, time, errors | Same; must match README commands exactly |

Framework: [smolagents](https://github.com/huggingface/smolagents) (Hugging Face).  
Remote: https://github.com/tatwan/agenticai_smolagents  
Local folder name may be `agentic_ai`; **there is no `smolagents/` subdirectory.**

This is a teaching repo. It is not an app. Do not add a web service, a package API, or a second agent framework unless the owner asks.

---

## Current truth (do not ignore)

As of **2026-09-16** P0 (first-run path) is in the tree and Module 01 has been rewritten. Modules 02–06 may still be the February labs until this session finishes them.

- Canonical commands: repo root (no `cd smolagents`), `uv sync`, `cp .env.example .env`.
- Default Hub model: `Qwen/Qwen3-Next-80B-A3B-Thinking` via `course_setup.py`. Ollama is the documented zero-cost path.
- Full evidence and ordered backlog: `progress/AUDIT.md`.
- Disk snapshot: `progress/CURRENT_STATE.md`. Treat `progress/LOG.md` as newer than the snapshot.

Do not claim the **whole course** is refreshed until Modules 02–06 match Module 01’s contract and LOG records a live Module 01 run.

---

## Goals (what “excellent” means here)

A stranger with Python 3.10+, `uv`, and a free afternoon can:

1. Clone, install, configure a token **or** a local model, without a mentor.
2. Finish Module 01 and *see* the agent loop in `memory.steps`.
3. Build a custom tool, compare CodeAgent vs ToolCallingAgent, do a web research run, run a manager+specialist, and log a run.
4. Understand *why* each step exists, not only which function to call.
5. Hit a documented error table when something fails (token, rate limit, model with no tool calling, DDG block, MLflow port).

Audience stretch: originally intermediate data/ML; owner now wants **public self-guided**. Write for a sharp beginner who can read Python, and keep a clearly marked “intermediate” stretch in exercises. Do not require prior smolagents or LangChain.

---

## Layout

```
AGENTS.md                 ← you are here
README.md                 ← learner-facing; must stay true
pyproject.toml            ← uv project; notebook-only (not a publishable package)
progress/                 ← audit, snapshot, log (not learner curriculum)
docs/plans/               ← 2026-02-19 design (may be gitignored; fix that)
01_foundations/
02_tools_and_custom_tools/
03_codeagent_vs_toolcalling/
04_web_search_and_browsing/
05_multi_agent_orchestration/
06_mlflow_observability/
images/
```

Do not invent Module 07 as required work until P0/P1 from the audit ship.

---

## Module contract (keep this consistent)

Every module folder keeps the triad. Every notebook keeps this rhythm:

1. Concept brief (enough to run the next cells without the outline — or the outline is explicitly step 0)
2. Setup (one local path, one Colab path, not two conflicting dotenv cells)
3. Guided examples that run as-is
4. Exercises as `# TODO` with **success criteria** (and later: hints/solutions)
5. What You Built
6. Next module preview (Module 06: course wrap-up instead)

Shared setup facts belong in **one** place conceptually (README + a short “environment” section). If you change the default `model_id`, token permission, or install extra, you must update **README and all six notebooks** (today the model id is copy-pasted six times). Prefer introducing a tiny shared snippet or a clearly identical setup cell over drifting copies.

### APIs we teach (do not churn without cause)

Keep teaching these unless upstream removes them:

- `CodeAgent`, `ToolCallingAgent`
- `InferenceClientModel`, `LiteLLMModel`
- `@tool`, `Tool` + `forward()`
- `agent.run()`, `agent.memory.steps`
- `managed_agents=` with `name` and `description` **on the agent** (not a separate `ManagedAgent` wrapper — the Feb design doc is stale on this)
- `VisitWebpageTool`
- Search: current docs prefer `WebSearchTool`; labs still say `DuckDuckGoSearchTool`. When you touch Module 04+, migrate deliberately and update README/outlines/instructions together.

### APIs / stories we must stop teaching as-is

- “HuggingFace Inference API (free, unlimited, Read token)”
- Hardcoded `Qwen/Qwen2.5-Coder-32B-Instruct` as *the* default without a live check
- `cd smolagents`
- `cp .env.example .env` until the file exists
- Module 01 instructions referencing “Module 00”
- “Read scope is sufficient”

---

## How to change content

### Order of work

1. **P0 first** (audit §11): first-run path, gitignore, env template, packaging, honest token/model/cost story, pinned deps. Live-run Module 01.
2. **Then P1:** learner-facing explanations, setup cell cleanup, exercise success bars, Module 06 without a mandatory extra terminal, year/model string refresh.
3. **Then P2:** Module 00, sandbox note, MCP/eval pointers, LICENSE if not done in P0.

Do not polish Module 05 prose while Module 01 cannot run.

### Pedagogical rules

- **Show, then ask.** Guided cell before TODO.
- **The LLM only sees the tool schema.** That sentence stays in Module 02.
- **Same task, two agent types** stays the center of Module 03.
- **Descriptions are the manager’s routing table** stays the center of Module 05.
- Prefer one working path over five commented options.
- Colab is optional. Local uv is canonical. If a module cannot work in Colab (MLflow UI), say so in README and instructions — do not leave a badge that lies.
- Outlines must not contradict notebooks. After any API rename, grep the whole repo.

### Files you should grep together

When renaming a class, model id, or install extra:

```
README.md
pyproject.toml
*/notebook.ipynb
*/outline.md
*/instructions.md
```

### Do not

- Commit `.env`, tokens, notebook outputs that contain secrets, or `mlruns/`
- Broaden `.gitignore` to ignore `progress/` or `AGENTS.md`
- Leave `docs/*` ignored if we want the design plans on GitHub
- Add LangChain as a dependency “for completeness”
- Rewrite all six outlines into a different course structure in one PR
- Execute exercise stubs for the learner (leave TODO cells as student work; you may add *separate* solutions files)
- Claim a notebook is verified without running it

---

## Commands

Canonical (once P0 fixes README — until then these are the *intended* commands, not what README currently prints):

```bash
# from repo root (the directory that contains pyproject.toml)
uv sync
cp .env.example .env   # then edit HF_TOKEN
uv run jupyter lab
uv run python -c "import smolagents; print(smolagents.__version__)"
uv run mlflow ui --port 5000   # module 06, optional once file-store works
```

There is no test suite. Verification is:

1. `uv sync` on a clean tree
2. Module 01 setup cell + Fibonacci `agent.run()`
3. Grep for leftover stale strings (`cd smolagents`, `Qwen2.5-Coder-32B`, `Read scope`, `api-inference.huggingface.co`)

---

## Environment and secrets

- Required cloud path: `HF_TOKEN` with **Make calls to Inference Providers** (fine-grained). Not “Read.”
- Optional: `OPENAI_API_KEY` only for Module 03 optional cell.
- Preferred zero-cost path to document: Ollama + `LiteLLMModel` (already sketched in FAQ / Module 03).
- Never put tokens in notebooks. Option C (“paste token in cell”) should be removed or labeled unsafe.

Hugging Face credits are **not** an unlimited free LLM. Document that. Provide a local fallback so the “public, free to complete” promise can be true.

---

## Progress folder protocol

| Event | Update |
|---|---|
| Research / audit | `progress/LOG.md` |
| Implement backlog items | LOG + code; if the snapshot is now wrong, `CURRENT_STATE.md` |
| Finish a “labs actually run” milestone | LOG with evidence; bump CURRENT_STATE |
| Owner changes audience or framework | LOG + README + this file |

`progress/` is for maintainers. Learners should not need it. After P1, README can link “maintainers: see AGENTS.md” once.

---

## Original design docs

`docs/plans/2026-02-19-smolagents-course-design.md` and `...-implementation.md` are the approved Feb 2026 spec. Useful for intent. **Not** gospel for APIs:

- They still say `ManagedAgent`; shipped notebooks correctly use `name`/`description` on the agent.
- They promised `.env.example` and MLflow callbacks; those did not fully ship.
- They assume free HF Inference API.

When design and a working notebook disagree on API shape, **trust the current smolagents docs + a live run**, then update the design note in LOG.

---

## Relationship to other courses

[Hugging Face Agents Course](https://huggingface.co/learn/agents-course) is the long official track. This repo should stay a **short lab sequence** (one day / six focused notebooks), not a clone of that course. Position it in README when you touch README.

---

## Definition of done for a content change

A module change is done only if:

- [ ] Notebook, outline, and instructions agree on class names, model setup, and commands
- [ ] README module map still accurate if tools/names changed
- [ ] Guided cells (not exercises) were run, or you explicitly log that they were not
- [ ] `progress/LOG.md` has an entry
- [ ] No new secrets, no `cd smolagents`, no instructions pointing at missing files

A **course-wide** refresh is done only if audit P0 success criteria pass (`AUDIT.md` §12).

# Change log

Append-only. Newest entries at the **top**.

Every improvement session must add an entry before it finishes, even if the session only researched. If you change labs, name the files. If you verify a live run, paste the evidence (command, model id, pass/fail) — not “should work.”

Format:

```
## YYYY-MM-DD — short title

- **Who:** human or agent
- **Why:** one or two sentences
- **Changed:** bullet list of paths
- **Verified:** what was actually run, or "not executed"
- **Follow-up:** what the next session should pick up
```

---

## 2026-09-16 — P0 first-run path + Module 01 lesson rewrite

- **Who:** coding agent (Grok 4.6)
- **Why:** Audit P0 blockers made Quick Start unusable. Module 01 notebook was a demo, not a self-guided lesson.
- **Changed:**
  - `.gitignore` — ignore `.env`, `.venv`, `mlruns/`, checkpoints; stop ignoring `docs/`
  - `.env.example` — HF Inference Providers permission + Ollama zero-cost path
  - `pyproject.toml` — `[tool.uv] package = false`, `smolagents[toolkit,litellm]>=1.26,<2`, drop frozen `duckduckgo-search`
  - `uv.lock` — resolved smolagents 1.26.0, mlflow 3.16.0, ddgs 9.16.0
  - `LICENSE` — MIT
  - `course_setup.py` — shared `make_model()` / `smoke_test()`
  - `README.md` — clone-root commands, honest credits, outline-as-lesson
  - `data/sample_sales.csv` — for Modules 02/05
  - `01_foundations/{outline.md,instructions.md,notebook.ipynb}` — learner-facing lesson + lab
  - `docs/plans/*` now trackable
- **Verified:**
  - `uv sync` on this machine: smolagents 1.26.0, Python 3.13.5
  - `course_setup.smoke_test` against `ollama_chat/qwen2.5-coder:3b` → `pong`
  - Module 01 Fibonacci `CodeAgent(tools=[], max_steps=8)` → **610**, steps `TaskStep, ActionStep, ActionStep`
  - `smollm2:135m` cannot drive CodeAgent (parse failures) — do not recommend it
  - Hugging Face cloud path **not** live-run (no `HF_TOKEN` in this environment)
- **Follow-up:** Modules 02–06 on the same contract (outline = lesson, shared setup, current APIs). `WebSearchTool` in 04. `mlflow.smolagents.autolog()` in 06.

---

## 2026-09-16 — Full course audit; progress pack + AGENTS.md

- **Who:** coding agent (Grok 4.6), at repo owner request
- **Why:** Course last updated 2026-02-24. Owner wants a public self-guided intro to building AI agents. Audit first; lab rewrites deferred to a new session.
- **Changed:**
  - `AGENTS.md` (new) — operating manual for this teaching repo
  - `progress/README.md` (new) — index
  - `progress/AUDIT.md` (new) — formal audit
  - `progress/CURRENT_STATE.md` (new) — snapshot
  - `progress/LOG.md` (new) — this file
- **Not changed:** any module notebook, outline, instructions, README, or `pyproject.toml`. Design docs still gitignored.
- **Verified:**
  - Read every module file and both plan docs
  - `git log`, `git ls-files`, `.gitignore` behavior (`docs/*` ignores plans; `.env` not ignored)
  - Confirmed `.env.example`, `uv.lock`, `LICENSE` absent
  - Cross-checked smolagents 1.26.0 docs, Inference Providers auth, default model change, `WebSearchTool` / `ddgs`, `mlflow.smolagents.autolog()`
  - **Did not** run `uv sync`, `agent.run()`, Colab, or MLflow UI
- **Follow-up:** Next session executes `progress/AUDIT.md` §11 **P0** (first-run path, token/model story, dependency pins) and live-runs Module 01 before any prose polish. Do not start at Module 05.

---

## 2026-02-24 — Colab setup cells and README badges

- **Who:** repo owner (`bf424fd`)
- **Why:** Let people open notebooks in Google Colab
- **Changed:** all six `notebook.ipynb` (install + secrets cells); `README.md` Colab badges to `tatwan/agenticai_smolagents`
- **Verified:** unknown (no test notes in repo)
- **Follow-up:** Colab install still commented by default; Module 06 still assumes localhost MLflow

---

## 2026-02-19 — Initial course

- **Who:** repo owner (`cf32bb7`)
- **Why:** Ship the 6-module smolagents mini-course from the 2026-02-19 design/implementation plans
- **Changed:** README, `pyproject.toml`, six module triads, hero image
- **Not shipped vs plan:** `.env.example`; Module 00; MLflow autolog/callbacks; `uv.lock`
- **Verified:** unknown
- **Follow-up:** see audit

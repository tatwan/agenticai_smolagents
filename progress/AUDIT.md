# Audit Report: Building AI Agents with smolagents

| Field | Value |
|---|---|
| **Date** | 2026-09-16 |
| **Scope** | Entire repository: README, `pyproject.toml`, all 6 modules (`outline.md`, `instructions.md`, `notebook.ipynb`), design/implementation plans, git history, and current smolagents / Hugging Face / MLflow / search-tool APIs |
| **Course last content update** | 2026-02-24 (Colab badges and setup cells). Core curriculum written 2026-02-19 |
| **Audit lag** | ~7 months |
| **Intended purpose (as designed)** | A 6-module, code-heavy mini-course teaching Hugging Face **smolagents** to intermediate data engineers and ML practitioners, using free-tier APIs |
| **Intended purpose (as now requested)** | A public, self-guided intro to building AI agents that anyone can learn from |
| **Overall verdict** | **The curriculum skeleton is good. The course is not currently shippable as a public self-guided resource.** A motivated intermediate Python user who already knows Hugging Face could still learn the agent loop, tools, CodeAgent vs ToolCallingAgent, web research, manager/specialist orchestration, and basic logging — *if* they fight through a broken first-run path and outdated inference/search APIs. A public learner following the README today is likely to fail before Module 01. |

This report is the source of truth for a later improvement session. Do not start rewriting labs until the P0 blockers in [§11](#11-prioritized-improvement-backlog) are sequenced.

---

## 1. Executive summary

### What still works

- The **learning arc is coherent and still the right intro shape**: agent loop → tools → two agent architectures → live retrieval → multi-agent → observability.
- Each module has a consistent triad: `outline.md` (rich), `instructions.md` (runbook + errors), `notebook.ipynb` (do the work).
- Outlines are the best writing in the repo. They explain *why*, not just *how*.
- Exercises exist in every module and actually practice the skill just taught.
- The course stays small, code-first, and open-source-first. That is still a differentiator versus LangChain-heavy surveys.

### What is broken or misleading

1. **A new learner cannot complete Quick Start as written.** `.env.example` does not exist. README says `cd smolagents`. `.gitignore` does not ignore `.env`. `pyproject.toml` is not a reliable `uv sync` project. There is no `uv.lock`.
2. **The default model and the “free Hugging Face Inference API” story are from early 2026.** Hugging Face retired the old serverless Inference API (`api-inference.huggingface.co`). Inference now goes through **Inference Providers** (`router.huggingface.co`). Tokens need **“Make calls to Inference Providers”**, not Read. Free accounts now get a **tiny monthly credit** (~$0.10 as of Sep 2026), not an unlimited free LLM. smolagents itself replaced `Qwen/Qwen2.5-Coder-32B-Instruct` as the default because that model’s common providers **do not support tool calling**.
3. **Search tooling drifted.** Official smolagents docs now lead with `WebSearchTool`. `duckduckgo-search` was frozen and renamed to `ddgs`. The course still installs and teaches `DuckDuckGoSearchTool` + `duckduckgo-search>=6.0.0`.
4. **Self-guided quality is uneven.** The notebooks are thinner than the outlines, and the README tells learners that `outline.md` is an *instructor* document. Exercises are `# TODO` stubs with no hints, expected outputs, or solutions. Setup cells are duplicated and contradictory (Colab vs local).
5. **Audience mismatch.** The design doc targets intermediate data/ML practitioners. Opening this to “anyone” without a gentler on-ramp, a working setup, and visible expected output will drop beginners immediately.

### Scores (1–10)

| Dimension | Score | Why |
|---|---|---|
| Curriculum design / sequencing | 8 | Linear, each module earns the next, no capstone bloat |
| Conceptual accuracy (agent loop, tools, two agent types) | 8 | Still correct; a few internals have moved |
| Self-guided completeness | 5 | Outlines yes, notebooks + exercises only partly |
| First-run reliability | 2 | Missing env template, wrong `cd`, packaging, token story |
| API / dependency currency (Sep 2026) | 3 | Model, HF inference, search package, MLflow autolog, token scopes |
| Relevance to “intro to building AI agents” | 7 conceptual / 4 ecosystem | Teaches the right primitives; omits MCP, eval, sandboxing, memory |
| Public accessibility | 4 | Intermediate assumed; Colab path incomplete; no license |
| Observability module vs current practice | 4 | Manual MLflow is still useful; official `mlflow.smolagents.autolog()` is missing |
| Repo hygiene for a public course | 3 | `.gitignore` is dangerous; design docs are gitignored; no LICENSE |

**Composite: 4.5 / 10 as a public self-guided course in September 2026.**  
**Composite: 7 / 10 as a private workshop for people you can unstick in person, if the default model still routes.**

---

## 2. What this course is trying to do

From `docs/plans/2026-02-19-smolagents-course-design.md` (approved, 2026-02-19) and the README:

- Teach **smolagents**, not “agents in the abstract.”
- Stay **code-heavy**: notebooks over slides.
- Use **open-source + free-tier** so cost is not a barrier.
- Linear 6 modules, no capstone.
- Audience: **intermediate–advanced data engineers and ML practitioners**.
- Each module folder: outline + notebook + instructions.
- Notebook rhythm: Concept Brief → Setup → Guided Examples → Exercises → What You Built → Next Preview.

That intent is still valid. smolagents remains a good first framework because the abstractions are few (`CodeAgent`, `ToolCallingAgent`, `Tool`, `managed_agents`, a `Model` protocol).

What has changed since February 2026 is not the *idea* of the course. It is:

- the **inference product** Hugging Face sells,
- the **default model** smolagents recommends,
- the **search tool** the library documents,
- the **observability** API MLflow now ships for smolagents,
- and the **public-learner** bar you now want.

---

## 3. Method

Read, did not rewrite:

- README, `pyproject.toml`, `.gitignore`
- All 6 `outline.md`, `instructions.md`, `notebook.ipynb` (every cell)
- `docs/plans/2026-02-19-smolagents-course-design.md`
- `docs/plans/2026-02-19-smolagents-course-implementation.md`
- git history (2 commits: 2026-02-19, 2026-02-24), `git ls-files`, ignore rules
- Current smolagents docs (v1.26.0 as of 2026-05-29; still latest as of this audit): `InferenceClientModel`, `WebSearchTool` / `DuckDuckGoSearchTool`, `managed_agents`, MLflow autolog
- Hugging Face Inference Providers docs (token permission, router, free credits)
- `huggingface_hub.list_models` current signature
- Public GitHub repo `tatwan/agenticai_smolagents` (Colab links target this)

**Not executed in this audit:** live `uv sync`, live `agent.run()`, Colab, or MLflow UI. First-run failures below are from missing files and documented API changes, not from a failed notebook execution. The next improvement session **must** run Module 01 end-to-end against a current `HF_TOKEN` before claiming the labs work.

---

## 4. Repository-level findings

### 4.1 First-run path is broken

README Quick Start:

```
2. cd smolagents
3. uv sync
4. cp .env.example .env
5. uv run jupyter lab
```

| Step | Actual state | Impact |
|---|---|---|
| `cd smolagents` | Repo root **is** the course. There is no `smolagents/` subdirectory. GitHub clone is `agenticai_smolagents`. Local folder is `agentic_ai`. | Immediate confusion. Instructions.md still says `cd /path/to/smolagents`. Module 06 says `cd smolagents` then `mlflow ui`. |
| `uv sync` | `pyproject.toml` uses hatchling as build backend, project name `smolagents-course`, **no Python package**, no `[tool.uv] package = false`, **no `uv.lock`**. | High chance `uv sync` fails trying to build a wheel, or installs an unpinned, moving set of packages. |
| `cp .env.example .env` | **`.env.example` is not in the tree.** It was specified in the implementation plan and never committed. | Setup stops. |
| Token guidance | “Read access is sufficient.” | **Wrong in 2026.** Inference Providers require a fine-grained token with **Make calls to Inference Providers**. |
| `.gitignore` | Only `.DS_Store` and `docs/*`. **`.env` is not ignored.** | Learners who create `.env` can commit secrets. Design docs are also gitignored (see 4.2). |

### 4.2 Design docs are local-only

`.gitignore` contains `docs/*`, so:

- `docs/plans/2026-02-19-smolagents-course-design.md`
- `docs/plans/2026-02-19-smolagents-course-implementation.md`

exist on disk and are **not on GitHub**. Public learners and future agents cloning the remote never see the original spec. That spec is still the best statement of intent.

Also missing from git: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, `.env.example`, `uv.lock`.

`.claude/settings.local.json` is correctly untracked (global gitignore). It should stay untracked.

### 4.3 Packaging

```toml
[project]
name = "smolagents-course"
requires-python = ">=3.10"
dependencies = [
    "smolagents[litellm]>=1.0.0",
    "huggingface-hub>=0.23.0",
    "mlflow>=2.13.0",
    "duckduckgo-search>=6.0.0",
    ...
]
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Problems:

- Floor pins (`>=1.0.0`) on a library that is now **1.26.0** and still experimental. A fresh install in Sep 2026 is not the library the notebooks were written against in Feb 2026.
- Extra is `[litellm]` but search/browse need the **toolkit** extra (`smolagents[toolkit]` in current docs).
- `duckduckgo-search` is a frozen package; maintained successor is `ddgs`.
- No `[tool.uv] package = false` for a notebook-only repo.
- No Python version upper bound; 3.10+ is still fine, but 3.12/3.13 should be tested.

### 4.4 Hugging Face inference: the silent P0

Course language everywhere: “HuggingFace Inference API (free tier).”

Reality as of this audit:

- Legacy `https://api-inference.huggingface.co` returns **410 Gone**.
- Current path: **Inference Providers** via `https://router.huggingface.co`.
- `InferenceClientModel` still exists and still accepts `token=` / `api_key=` / `HF_TOKEN`. The **class name is current**. The **product behind it is not** what the course describes.
- Default smolagents model is now `Qwen/Qwen3-Next-80B-A3B-Thinking` (changed because `Qwen/Qwen2.5-Coder-32B-Instruct` providers often **lack tool calling**). This course hardcodes the old default in **every notebook**.
- Token: fine-grained + Inference Providers permission.
- Billing: free users have a **small monthly credit**, then pay-as-you-go or hard stop. Advertising “no paid subscriptions required to complete the core curriculum” is no longer honest without a local/Ollama fallback as the *default* free path.

This is the single most important content bug. If Module 01 `agent.run()` fails, the whole course fails.

### 4.5 Colab path is half-done

Added 2026-02-24:

- README Colab badges → `githubtocolab.com/tatwan/agenticai_smolagents/...` (repo exists).
- Every notebook has a commented install cell and a commented secrets cell.

Gaps:

- Local setup cell still calls `load_dotenv()` **after** the Colab secrets cell. Harmless if dotenv is installed; confusing as a procedure.
- Colab install uses `!uv pip install` **and** `!pip install`, both commented. Learners who skip the README will run nothing and then hit `ModuleNotFoundError`.
- Module 06 requires `localhost:5000` MLflow UI. **That does not work in Colab** without a tunnel or switching to file-based tracking (`mlruns/`). Unmentioned.
- Colab install line omits `pandas`, `requests`, `huggingface-hub` (Module 02 needs all three).

### 4.6 License and public posture

No LICENSE. A public course needs an explicit license (code: MIT or Apache-2.0; prose: CC-BY is common). Without it, people cannot legally be sure they may copy notebooks into their own teaching.

No statement of estimated total time (sum of modules: ~6–8 hours). No “who this is / is not for” beyond one README sentence.

### 4.7 Notebooks have no saved outputs

All notebooks are source-only. For self-guided learning, a *few* representative outputs (one successful Fibonacci run, one step dump) dramatically reduce “is this broken or am I broken?” anxiety. Full executed notebooks are heavy and leak tokens; a middle ground (screenshots in `instructions.md`, or a `expected_output.md`) is missing.

---

## 5. Pedagogy: is it self-guided?

### 5.1 The split that hurts public learners

README:

> `outline.md` — instructor reference and planning document  
> `notebook.ipynb` — the main learning artifact  
> `instructions.md` — setup, run, common errors

**The outlines are where the teaching happens.** Architecture, decision frameworks, schema tables, security notes, “when not to use multi-agent” — that content is in `outline.md`, not in the notebook the learner is told to open.

Notebook concept briefs are 1–3 short paragraphs. They are not enough to *learn as you go* unless the learner already knows the ideas.

For a public self-guided course, pick one:

- **A.** Tell learners to read `outline.md` first, then the notebook (rename it “lesson”, not “instructor reference”).
- **B.** Fold the outline’s explanations into the notebook markdown cells so the notebook is sufficient.
- **C.** Keep outlines as instructor notes and write a real student-facing lesson file.

Today the repo accidentally chose “instructor notes + thin lab,” which is a workshop format, not a self-guided format.

### 5.2 Learn-as-you-go: what is present

Every module has:

- A “why this exists” opener
- A working guided example before exercises
- Step inspection (`memory.steps`) starting in Module 01 and reused
- “What You Built” + next-module teaser
- Common errors in `instructions.md` (quality varies; Module 01 is the best)

That is the right shape.

### 5.3 Learn-as-you-go: what is missing

| Gap | Why it matters for self-guided |
|---|---|
| No Module 00 / setup lab | Token, `uv`, Jupyter kernel, “hello model” smoke test all dumped into README + Module 01 |
| Exercises are empty `# TODO` cells | No scaffold, no assert, no “if you see X you succeeded” |
| No solutions / hints | Public learners stall; workshop instructor can walk the room |
| CSVSummaryTool never runs on a file | Module 02 defines it, tests only schema; Module 05 Ex 2 assumes it works |
| No sample data | No CSV in the repo |
| `add_base_tools=True` underexplained in the notebook | Outline mentions interpreter + search; notebook says “Python interpreter” |
| Security of CodeAgent mentioned in outline 03, never demonstrated | Public 2026 audience will ask “is this safe?” |
| No recap that is actually a recap | Later modules assume 01–0N but do not re-show a 5-line cheat sheet |
| No estimated time on the README module map | Only inside each `instructions.md` |

### 5.4 Cognitive load and audience

Claimed audience: intermediate Python + “know what a language model is.”

That is realistic for:

- `CodeAgent` vs `ToolCallingAgent`
- tool schemas
- manager/specialist
- MLflow params/metrics/artifacts

It is **not** realistic for “open to anyone” without:

- a plain-language 10-minute “what is an agent” before code,
- a guaranteed working model path (Ollama *or* a currently-routable HF model *or* a documented paid fallback),
- and solutions they can peek at after trying.

### 5.5 Consistency of the 6-section notebook contract

Design required: Concept Brief, Setup, Guided Examples, Exercises, What You Built, Next Preview.

**All 6 notebooks follow this.** After the 2026-02-24 Colab pass, Setup became 3 cells (install + token + model) instead of 1. That is fine, but the token cell comments out Option A (`load_dotenv`) while the next cell always `load_dotenv()`s. Learners following comments literally will think they must pick one cell and skip the other.

---

## 6. Per-module audit

Scoring key for each module: **Context** (enough explanation), **Doable** (a solo learner can finish), **Current** (APIs/models/tools), **Relevant** (serves the course goal).

### Module 01 — Foundations

**Files:** 16 notebook cells. Outline is excellent (agent loop diagram, MultiStepAgent / CodeAgent / ToolCallingAgent, model table, `memory.steps` types). Instructions are the best runbook in the repo (token errors, 429s, old smolagents without `memory`).

**What is taught well**

- Chatbot vs agent.
- Think → Act → Observe, `final_answer()`, `max_steps`.
- First `CodeAgent` on Fibonacci, then primes, then inspect steps.
- Exercises (temperature conversion, median without `statistics`) are the right difficulty.

**Gaps**

- Notebook does not explain `InferenceClientModel` vs other model classes; outline does.
- `add_base_tools=True` with `tools=[]` is shown, not unpacked. A CodeAgent already has a Python interpreter; base tools also inject search. Learners will not know why Fibonacci works.
- Step type table (`TaskStep`, `ActionStep`, `FinalAnswerStep`) lives only in the outline.
- `reset=False` for multi-turn is only in the outline.
- Default model is the stale Qwen 2.5 Coder 32B.
- No smoke test that the token can actually call a chat model before `agent.run()`.

**Self-guided?** Almost, if setup worked. Conceptually the notebook is a demo, not a lesson.

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 6 (outline 9) | 5 | 3 | 9 |

### Module 02 — Tools & Custom Tools

**Taught well**

- Schema anatomy: `name`, `description`, `inputs`, `output_type`.
- “The LLM never sees your source.” This is the most important tool lesson and it is in both outline and notebook.
- `@tool` with type hints + Google-style `Args:`.
- `Tool` subclass with `forward()`.
- Inspecting `PythonInterpreterTool`.
- Three stacked exercises (stats tool, CoinGecko subclass, combine).

**Gaps**

- `top_hf_model` uses `list_models(filter=task, sort="downloads", direction=-1)`. `filter=` for tasks has been on a deprecation path in `huggingface_hub`; current docs prefer `pipeline_tag=` / `filter` still documented but learners may see warnings. No `limit=1`, so it can crawl. Should pass `token=`.
- `CSVSummaryTool` is never executed against a CSV. No sample file. Module 05 Ex 2 depends on it.
- CoinGecko is a real external API with rate limits and occasional 429s; no backup (static JSON fixture) for when the API fails.
- Outline mentions `DuckDuckGoSearchTool` / `VisitWebpageTool` / `SpeechToTextTool` as built-ins; notebook only inspects `PythonInterpreterTool`.
- `super().__init__()` is stressed in instructions, not shown in the CSV example (CSV has no custom `__init__`, so it is easy to miss).

**Self-guided?** The decorator vs subclass split is clear. Exercises need more scaffolding for a public audience (especially HTTP error handling).

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 7 | 6 | 6 | 9 |

### Module 03 — CodeAgent vs ToolCallingAgent

**Taught well**

- This is the **best module pedagogically**. Same tool, same task, two architectures, then read the steps.
- Decision framework is correct and still current.
- Optional LiteLLM / OpenAI / Ollama / Anthropic swap is the right “model-agnostic” demo and is clearly optional.
- Instructions warn that ToolCallingAgent needs native function calling — critical, and now *more* critical given the default-model change.

**Gaps**

- Optional models are dated: `gpt-4o-mini`, `claude-3-5-sonnet-latest`, `ollama_chat/llama3.2`. Still illustrative; names should be refreshed and marked “example IDs, check current docs.”
- Outline discusses CodeAgent sandbox / E2B / Docker; notebook never shows a sandbox. For 2026, a one-cell “this runs on your machine” warning is the minimum.
- No mention that some HF-routed models cannot do tool calling (the exact failure that made smolagents change its default).

**Self-guided?** Yes for intermediates. The comparison is the course’s unique value.

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 8 | 7 | 5 | 10 |

### Module 04 — Web Search & Browsing

**Taught well**

- Closed vs open information.
- Search → select → visit → extract → reason.
- Standalone tool calls before wrapping in an agent (good lab design).
- Rate limits, bot blocking, citation hallucination — instructions are practical.
- Verifiable-agent cell asks for a source URL.

**Gaps (currency)**

- Hard dependency on `DuckDuckGoSearchTool` + `duckduckgo-search`. Current smolagents docs and the official HF Agents Course have been moving to `WebSearchTool` (engine=`duckduckgo` by default, plus Bing/Exa options in later versions).
- Search query `"smolagents huggingface 2024"` is a year stale.
- Visit target `https://huggingface.co/blog/smolagents` is still a reasonable page but should be treated as “may move.”
- Exercise 2 (3 dbt articles, visit each, comparison table, `max_steps=10`) is **hard** and flaky (rate limits + blocked pages). Fine as a stretch; not fine as the only second exercise with no fallback topic.

**Self-guided?** The pattern is teachable. Reliability of DuckDuckGo from notebooks has always been the weak point; 7 months later it is weaker, not stronger.

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 8 | 5 | 4 | 9 |

### Module 05 — Multi-Agent Orchestration

**Taught well**

- Manager with **no tools**, specialists with `name` + `description`.
- Description-as-routing-table is the right mental model and is repeated (good).
- Mixed types: `ToolCallingAgent` researcher + `CodeAgent` analyst.
- Delegation inspection loop.
- “When NOT to use multi-agent” in the outline is mature and should be in the notebook.
- `managed_agents` API used here matches **current** smolagents (`name`/`description` on the agent, not a separate `ManagedAgent` wrapper). Design doc still says `ManagedAgent`; **the notebook is more current than the design doc.** Keep the notebook pattern.

**Gaps**

- Combined task (US senior data engineer salary 2024 + local stats) is dated and web-flaky.
- Exercise 2 requires copying `CSVSummaryTool` from Module 02 and downloading a CSV from a URL the searcher found. That is a lot of moving parts (web + pandas + network CSV + manager passing a URL as a string). Needs a local sample CSV path as a fallback.
- No discussion of token cost / latency of nested agents — outline mentions it; notebook does not.
- `manager.managed_agents.values()` is correct for current smolagents (dict keyed by name). Worth a one-line comment so learners who print the list are not surprised.

**Self-guided?** Concept yes. The live run will fail often because it depends on Modules 01+04 remaining green.

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 8 | 5 | 6 | 9 |

### Module 06 — MLflow Observability

**Taught well**

- Why agents need observability (non-determinism).
- Manual `start_run` / params / metrics / artifacts is still valuable teaching even if autolog exists — you should understand the record you are writing.
- `run_and_trace()` helper is a good extraction.
- Compare CodeAgent vs ToolCallingAgent in the UI.
- Exercise 2 (same task 3 times) is the right empirical lesson.

**Gaps**

- Implementation plan promised “automatic tracing with smolagents callbacks.” Shipped notebook is **manual only**.
- Current smolagents + MLflow: `mlflow.smolagents.autolog()` (documented in smolagents `inspect_runs`). **Not mentioned.** A 2026 course that teaches MLflow and ignores the first-party integration looks outdated.
- MLflow pin `>=2.13.0` will install MLflow 3.x on a fresh machine. UI and APIs have moved; “experiment already exists / create_experiment” advice may be stale. Must be re-verified.
- Two-terminal `mlflow ui --port 5000` is correct locally; **Colab-incompatible**; README still offers a Colab badge for this module.
- Tracking URI is hardcoded. File store (`mlflow.set_tracking_uri("file:./mlruns")`) would make the module work without a server for the first half, then optionally open the UI.
- No `.gitignore` for `mlruns/`.
- Wrap-up “where to go next” is thin: Gradio, Ollama, Slack bot. Missing: MCP, evaluation, tracing backends (Phoenix / OTel — also in current smolagents docs), HF Agents Course unit mapping.

**Self-guided?** Local intermediate: yes. Public / Colab: no.

| Context | Doable | Current | Relevant |
|---|---|---|---|
| 7 | 4 | 4 | 8 |

---

## 7. Design vs shipped

| Design / plan item | Shipped? | Notes |
|---|---|---|
| 6 modules, triad of files | Yes | Consistent |
| `pyproject.toml` + uv | Partial | File exists; lock, package flag, extras wrong |
| `.env.example` | **No** | Specified in Task 1, never committed |
| README module map + FAQ | Yes | Then Colab-updated; `cd smolagents` never fixed |
| Notebook 6-section structure | Yes | |
| Module 00 setup | Referenced in Module 01 instructions (“Prerequisites: Module 00”) | **Does not exist** |
| `ManagedAgent` wrapper | Design says yes | Notebook uses native `name`/`description` — **correct, keep** |
| LiteLLM optional demo | Yes | |
| MLflow callbacks / auto tracing | Plan yes | Notebook manual only |
| No capstone | Yes | Fine; wrap-up is enough if links are current |
| Free-tier only core path | Claimed | **No longer true** without a local model default |

---

## 8. Currency matrix (September 2026)

| Course artifact | Feb 2026 assumption | Sep 2026 reality | Action |
|---|---|---|---|
| `InferenceClientModel` | Current name (replaced `HfApiModel`) | Still current | Keep class; rewrite the product story |
| `token=os.environ["HF_TOKEN"]` | Valid | Valid; `api_key=` alias also works; env fallback exists | Keep; add permission docs |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | smolagents default | **Not the default**; tool-calling often missing on routed providers | Replace; document 2–3 working IDs + `provider=` |
| “Read token is enough” | Plausible | **False** | Fine-grained + Inference Providers |
| “Free tier, no paid needed” | Plausible | **~$0.10/mo credits then stop** | Ollama/local as documented free path; HF as optional cloud |
| `DuckDuckGoSearchTool` | Primary search tool | Still exists; docs lead with `WebSearchTool` | Teach `WebSearchTool`, mention DDG as engine |
| `duckduckgo-search>=6` | Right package | Frozen; use `ddgs` / toolkit extra | Change dependency |
| `managed_agents=[...]` with `name`/`description` | Current | Current | Keep |
| `agent.memory.steps` | Current | Current | Keep |
| `@tool` + Google docstring | Current | Current | Keep |
| `mlflow.set_experiment` + `log_param/metric/text/dict` | Current | Current, plus **`mlflow.smolagents.autolog()`** | Add autolog as the modern path; keep manual as pedagogy |
| `LiteLLMModel` | Current | Current | Keep; refresh example model IDs |
| `OpenAIServerModel` (outline 03) | Listed | Library also has `OpenAIModel` naming in places | Verify name before teaching |
| Year-stamped prompts (“2024”, “salary in 2024”) | Fine then | Stale | Use “current” / current year |
| Python 3.10+ | Fine | Fine | Test 3.12 |
| JupyterLab via uv | Fine | Fine | Add ipykernel registration note |

---

## 9. Relevance to “intro to building AI agents”

### Still the right spine

A 2026 intro still needs:

1. The loop (reason, act, observe, stop)
2. Tools as the contract with the model
3. Code-as-action vs JSON-as-action
4. Retrieval beyond weights
5. Decomposition into specialists
6. Traces you can compare

This course has all six, in that order. That is why it is worth refreshing rather than throwing away.

### What a 2026 public intro is missing

These are not required to keep the course “smolagents-shaped,” but a learner leaving in 2026 will notice their absence:

| Topic | Why learners expect it | Fit |
|---|---|---|
| **MCP / external tool servers** | Dominant 2025–2026 integration story | Optional Module 07 or a “where next” with one cell |
| **Evaluation** | “How do I know it’s good?” — Module 06 is traces, not scores | Small eval loop (3 golden tasks, pass/fail) in 06 or new module |
| **Sandboxing CodeAgent** | Security is a first question | One cell: local interpreter limits + pointer to E2B/Docker/Blaxel |
| **Memory beyond one `run()`** | `reset=False` is hidden in outline 01 | Promote into 01 or 05 |
| **Streaming / UI** | Gradio is mentioned only at the end | Optional, not core |
| **Skills / structured playbooks** | How production agents encode procedures | Out of scope; mention in wrap-up |
| **Position vs HF Agents Course** | Same library, official free course exists | README should say: this is a short lab track; that is the long course |

Do **not** turn this into a survey of LangGraph, CrewAI, and AutoGen. The value is depth in one small stack. Add a single “other frameworks” paragraph so public learners do not think smolagents is the only way.

---

## 10. Self-guided learner walkthrough (predicted)

A public learner on 2026-09-16:

1. Clones `tatwan/agenticai_smolagents`.
2. README says `cd smolagents` — already lost, or they ignore it.
3. `cp .env.example .env` — **file not found**.
4. Creates `.env` anyway, puts a Read token in it (as documented).
5. `uv sync` — may fail on hatchling packaging, or succeed and pull smolagents 1.26.
6. Opens Module 01, leaves Colab cells commented, runs setup.
7. `InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")` — likely **401/403** (wrong token permission), **no provider**, or **no tool calling** later in Module 03/05.
8. If they used Colab: install cell still commented unless they read README carefully.
9. If they reach Module 04: DDG rate limit or missing toolkit extra.
10. Module 06 Colab badge is a dead end.

**Conclusion:** the course does not currently contain enough *working* context to be self-guided. It contains enough *conceptual* context if a mentor unblocks setup.

---

## 11. Prioritized improvement backlog

This is the input for the next session. Order is load-bearing: do not rewrite Module 05 prose before Module 01 can run.

### P0 — Door is locked (do first, together)

1. **Fix the first-run path**
   - Add `.env.example`
   - Ignore `.env`, `.venv`, `__pycache__`, `.ipynb_checkpoints`, `mlruns/`, `.DS_Store`
   - Stop ignoring `docs/` (or move plans under a tracked path)
   - README: clone-root commands, not `cd smolagents`
   - `[tool.uv] package = false` (or equivalent) so `uv sync` does not build a fake package
   - Commit `uv.lock` after a known-good resolve
   - LICENSE

2. **Rewrite the model + token story in README + every setup cell**
   - Fine-grained token + Inference Providers permission
   - Honest credit/cost paragraph
   - Default `model_id` that **tool-calls on a current provider** (verify live; do not guess from this audit alone)
   - Show `provider=` and a fallback list
   - Document Ollama / LiteLLM as the **zero-cost** path, not a FAQ afterthought
   - One-cell smoke test: `model([{role, content}])` or a tiny `agent.run` with `max_steps=1`

3. **Dependencies**
   - `smolagents[toolkit,litellm]` at a **pinned minor** (e.g. `>=1.26,<2`) once labs pass
   - Replace `duckduckgo-search` with whatever the pinned smolagents toolkit actually imports (`ddgs`)
   - Pin `mlflow` to a verified major

### P1 — Self-guided enough to finish without a teacher

4. **Promote outlines into the learner path**  
   Either retitle `outline.md` → lesson and put it first in README, or merge the decision tables into notebook markdown. Do not leave the best teaching labeled “instructor only.”

5. **Unify setup cells**  
   One setup pattern for local, one clearly marked Colab block. Stop commenting out `load_dotenv` in a cell that is immediately followed by `load_dotenv()`.

6. **Exercise support**
   - After each `# TODO`, a “You succeeded if…” line
   - `solutions/` or collapsed hint cells at the bottom (clearly marked)
   - Sample CSV for `CSVSummaryTool`
   - Module 04 Ex 2: smaller default + stretch variant

7. **Module 06 runs without heroics**
   - File-based tracking works with zero extra terminal
   - `mlflow ui` as optional
   - Colab: disable the badge or document a Colab-specific path
   - Teach `mlflow.smolagents.autolog()` **after** the manual example

8. **Stale strings**  
   Years, salary prompts, `gpt-4o-mini` / Claude IDs, “Inference API (serverless).”

### P2 — Make it an excellent public resource (after P0/P1)

9. Module 00: 15-minute environment lab (uv, token, smoke test, Jupyter kernel).
10. CodeAgent safety cell (local interpreter limits; link to official sandbox backends).
11. `reset=False` / short memory note in Module 01 notebook.
12. Wrap-up: map to HF Agents Course units; one paragraph on MCP; one paragraph on eval.
13. Optional: 3 golden-task eval notebook using traces from 06.
14. README: total time, who it is for, who should start at HF Agents Course instead, changelog link to `progress/`.
15. Consider `WebSearchTool` as the taught name, with engine explained.
16. Accessibility: alt text for the hero image; consistent heading levels.

### Out of scope (do not sneak in)

- Rewriting the course onto LangGraph / CrewAI / a new framework
- A seventh required module before P0/P1 ship
- Video production
- Auto-grading infrastructure

---

## 12. Recommended next-session plan

A later agent/session should:

1. Read `AGENTS.md`, this file, `progress/CURRENT_STATE.md`.
2. Execute P0 against a live HF token **and** a local Ollama fallback.
3. Run each notebook top-to-bottom **except** exercise stubs; paste evidence of pass/fail into `progress/LOG.md`.
4. Only then fold outline teaching into learner-facing files (P1.4).
5. Keep the 6-module spine. Refresh APIs in place. Do not redesign the arc unless a P0 finding forces it (e.g. ToolCallingAgent cannot run on any free model — then demote ToolCallingAgent to “optional if your model supports it,” which Module 03 already half-does).

Success criteria for that session (minimum):

- A stranger can clone, `uv sync`, copy `.env.example`, run Module 01 Fibonacci, and see steps.
- Module 03 comparison runs on the documented default model **or** the notebook refuses clearly with “this model cannot tool-call; switch to X.”
- README does not mention a file or directory that does not exist.
- `.env` cannot be committed by accident.

---

## 13. Appendix A — File inventory (git-tracked)

```
.gitignore
README.md
pyproject.toml
images/Gemini_Generated_Image_wiu8prwiu8prwiu8.png
01_foundations/{outline.md,instructions.md,notebook.ipynb}
02_tools_and_custom_tools/{outline.md,instructions.md,notebook.ipynb}
03_codeagent_vs_toolcalling/{outline.md,instructions.md,notebook.ipynb}
04_web_search_and_browsing/{outline.md,instructions.md,notebook.ipynb}
05_multi_agent_orchestration/{outline.md,instructions.md,notebook.ipynb}
06_mlflow_observability/{outline.md,instructions.md,notebook.ipynb}
```

**Present locally, not tracked:** `docs/plans/*` (ignored by `docs/*`).

**Specified in the 2026-02-19 plan, missing:** `.env.example`.

**Added this audit (2026-09-16), not part of the original course:** `AGENTS.md`, `progress/`.

## 14. Appendix B — Sources checked

- In-repo design + implementation plans (2026-02-19)
- smolagents PyPI / GitHub: v1.26.0 (2026-05-29)
- https://huggingface.co/docs/smolagents (guided tour, default tools, inspect runs / MLflow autolog, models reference)
- https://huggingface.co/docs/inference-providers (auth permission, router)
- huggingface_hub `list_models` reference
- HF forum threads on `api-inference.huggingface.co` 410 Gone and Qwen2.5-Coder-32B-Instruct
- smolagents PR #1813 (default model change away from Qwen2.5-Coder-32B-Instruct)
- duckduckgo-search freeze / `ddgs` rename; smolagents `WebSearchTool` docs
- GitHub `tatwan/agenticai_smolagents`

## 15. Appendix C — Module time (as claimed)

| Module | Claimed | Likely for a public beginner after P0/P1 |
|---|---|---|
| 01 | 45–60 min | 90 min including setup |
| 02 | 60–75 | 75–90 |
| 03 | 60–75 | 60 |
| 04 | 60–75 | 90 (flaky web) |
| 05 | 75–90 | 90–120 |
| 06 | 75–90 | 90 |
| **Total** | **~6–8 h** | **~8–11 h** |

---

*End of audit. Next writing: `progress/CURRENT_STATE.md` (snapshot), `progress/LOG.md` (change log), `AGENTS.md` (how to work this repo).*

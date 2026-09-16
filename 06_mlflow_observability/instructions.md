# Module 06: Observability — how to run this lab

**Module:** 06 of 06 (wrap-up)  
**Read first:** [`outline.md`](outline.md)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

- Explain params vs metrics vs artifacts/traces in words that work for Phoenix or LangSmith too
- Log a run **without** starting `mlflow ui`
- Use a helper `run_and_trace()` and then `mlflow.smolagents.autolog()`
- Compare two runs from Python (`search_runs`) or, optionally, the UI
- Know Colab cannot host `localhost:5000`

---

## Prerequisites

- Modules 01–05 conceptually (you can log a Module 01 Fibonacci agent if 05 is tired)
- `mlflow` from `uv sync` (3.x is expected)

---

## Estimated time

75–90 minutes

---

## How to run

```bash
uv run jupyter lab 06_mlflow_observability/notebook.ipynb
```

**No second terminal is required** for the guided cells. Tracking goes to `sqlite:///mlflow.db` in the repo root (MLflow 3.16 no longer wants a bare `./mlruns` file store).

Optional UI, from the repo root:

```bash
uv run mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db
```

Then http://localhost:5000. If port 5000 is busy, pick another (`--port 5001`).

**Colab:** skip the UI. Run `mlflow.search_runs()` as in the notebook. The Colab badge is for the logging cells only.

---

## Common errors

### 1. `mlflow ui` connection refused

You never started the server, or you are in Colab. Use the file store + `search_runs`. The course is complete without the UI.

### 2. Empty experiment / cannot find runs

Tracking URI does not match. Print `mlflow.get_tracking_uri()`. Start the UI from the **repo root** so it sees `mlflow.db`. You can pass `--backend-store-uri sqlite:///mlflow.db`.

### 3. `create_experiment` / “already exists”

`set_experiment("smolagents-course")` is enough. Do not also `create_experiment` with the same name.

### 4. Huge `steps_trace.json`

Truncate `str(step)[:500]`. Web page observations will explode the file.

### 5. Autolog shows nothing

Call `mlflow.smolagents.autolog()` **before** `agent.run()`. Compatible range (MLflow 3.16): smolagents 1.22–1.26. Tool-calling details may be missing — fall back to manual logs.

---

## Tips

- Log failures too (`status` as a param).
- One `run_name` per idea (`codeagent-wordcount`, `toolcalling-wordcount`).
- Do not commit `mlruns/`.

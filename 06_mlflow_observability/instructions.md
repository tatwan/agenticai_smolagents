# Module 06: MLflow Observability

## Learning Objectives

By the end of this module you will be able to:

1. Start a local MLflow tracking server and connect to it from a notebook
2. Log agent runs with params (configuration), metrics (measurements), and artifacts (outputs)
3. Capture step-level traces as JSON artifacts for deep debugging
4. Compare runs in the MLflow UI to measure agent performance differences
5. Apply observability to multi-agent systems by tracking specialist-level metrics

---

## Prerequisites

- **All previous modules completed** (01 through 05)
- MLflow installed — it is already declared in `pyproject.toml`; no separate install step needed
- A valid `HF_TOKEN` in your `.env` file

---

## Estimated Time

75–90 minutes

---

## How to Run

This module requires two terminals running simultaneously.

**Terminal 1 — Start the MLflow tracking server:**
```bash
cd smolagents
uv run mlflow ui --port 5000
```

Leave this terminal running for the entire session.

**Terminal 2 — Start the notebook:**
```bash
uv run jupyter lab 06_mlflow_observability/notebook.ipynb
```

**Browser — Open the MLflow UI:**

Navigate to http://localhost:5000

You should see the MLflow home screen. The `smolagents-course` experiment will appear after you run the first code cell that calls `mlflow.set_experiment()`.

---

## Common Errors

### 1. Port 5000 already in use

**Symptom:** `OSError: [Errno 48] Address already in use` when starting the MLflow server.

**Fix:** Use a different port:
```bash
uv run mlflow ui --port 5001
```
Then update the tracking URI in the notebook Setup cell:
```python
mlflow.set_tracking_uri("http://localhost:5001")
```

---

### 2. Experiment already exists

**Symptom:** Warning or error when calling `mlflow.create_experiment()`.

**Fix:** Always use `mlflow.set_experiment()` instead. It creates the experiment if it does not exist, or retrieves it if it does. Never use `mlflow.create_experiment()` in notebook code.

---

### 3. "Run already active" error

**Symptom:** `MlflowException: Run with UUID ... is already active.`

**Fix:** This happens when you nest `mlflow.start_run()` calls without ending the outer run. Make sure every `with mlflow.start_run():` block is properly closed before starting a new one. If you interrupted a cell mid-run, call `mlflow.end_run()` in a new cell to reset the state.

---

### 4. Artifacts not showing in the UI

**Symptom:** You called `mlflow.log_text()` or `mlflow.log_dict()` but no artifacts appear in the MLflow UI.

**Fix:** Both calls require an active run context. Make sure they are inside a `with mlflow.start_run():` block. Calling them outside a run context silently fails in some MLflow versions.

---

### 5. Steps serialization error

**Symptom:** `TypeError` or `ValueError` when calling `mlflow.log_dict()` with step data.

**Fix:** The `str(step)` representation of a smolagents step object may contain characters that are not JSON-safe (e.g., embedded newlines in code blocks, Unicode characters from web pages). Always truncate with `[:500]` before adding to the dict:
```python
"content": str(step)[:500]
```
This keeps the artifact manageable in size and avoids serialization failures.

# Module 06: Observability — traces you can compare

**Read this first**, then run `notebook.ipynb`. This is also the **course wrap-up**.

**Time:** 75–90 minutes · **Depends on:** Modules 01–05 · **Colab:** logging works; the MLflow **UI** does not (no `localhost:5000`)

---

## 1. What is observability for agents?

An agent is a **non-deterministic program**. Same prompt, different hop counts, different tools, different wording, sometimes different facts.

If you cannot answer “what did it do?”, you cannot improve it. Observability is not a dashboard fetish. It is:

| Question | You log |
|---|---|
| What did I intend? | params (model id, agent type, `max_steps`, task) |
| What happened numerically? | metrics (duration, step count, tokens if you have them) |
| What did it actually say and call? | artifacts / traces (result text, `memory.steps`) |

This is the same split as classical ML experiments (MLflow, W&B) and as production tracing (OpenTelemetry, Phoenix, Langfuse, LangSmith). **Params / metrics / traces.** The vendor changes. The three buckets do not.

smolagents’ own docs instrument via OpenTelemetry and show Phoenix, MLflow autolog, and Langfuse. We use MLflow because it is local, open source, and already in this repo. The *habit* transfers.

---

## 2. When to log (always) vs when to open a UI

Log **every** run you might want to compare — including failures.

Open a UI when you need to *diff* two runs visually. You do **not** need a UI to learn this module. A file store plus `mlflow.search_runs()` is enough. That is what works in Colab.

Evaluation (pass/fail on golden tasks) is **related but different**. Tracing says what happened. Eval says whether it was good. We stay on traces here; the wrap-up points at eval as a next step.

---

## 3. How we log in this course

### Local SQLite first (no extra terminal)

MLflow 3.16 put the classic `./mlruns` filesystem backend in maintenance mode. A **SQLite** URI is the current local default and still needs no server:

```python
from pathlib import Path
import mlflow

db = Path("mlflow.db").resolve()
mlflow.set_tracking_uri(f"sqlite:///{db}")
mlflow.set_experiment("smolagents-course")
```

`mlflow.db` and `mlruns/` (artifact files) are gitignored. Do not commit them.

If you truly need the old file store, MLflow requires `MLFLOW_ALLOW_FILE_STORE=true`. We do not.

### Manual record (you should understand this even if autolog exists)

```python
import time, json

with mlflow.start_run(run_name="fibonacci-codeagent"):
    mlflow.log_params({"agent_type": "CodeAgent", "max_steps": 8, "model_id": model.model_id})
    t0 = time.perf_counter()
    result = agent.run(task)
    mlflow.log_metrics({
        "duration_seconds": time.perf_counter() - t0,
        "steps_taken": len(agent.memory.steps),
    })
    mlflow.log_text(str(result), "result.txt")
    steps = [{"i": i, "type": type(s).__name__, "text": str(s)[:500]}
             for i, s in enumerate(agent.memory.steps)]
    mlflow.log_dict({"steps": steps}, "steps_trace.json")
```

### Then autolog (the 2026 one-liner)

```python
mlflow.smolagents.autolog()  # compatible with smolagents 1.22–1.26 as of MLflow 3.16
agent.run(task)              # traces appear without a with-block
```

MLflow’s autolog note: **async APIs and some tool-calling details may not record.** Manual logs remain the teaching device and the backup.

### Optional UI

```bash
uv run mlflow ui --port 5000
# http://localhost:5000
```

Colab cannot open that. Use `mlflow.search_runs()` in the notebook instead.

---

## 4. What to compare

- **steps_taken** — gave up vs looped
- **duration_seconds** — slow tools vs slow models
- **result.txt** — same facts, different wording, or a miss
- **steps_trace.json** — where two agent types diverged (Module 03, now with evidence)

Three identical tasks in a row is the non-determinism lab. Expect variance. That is the point.

---

## 5. Exercises

1. Wrap a Module 05-style manager run (even analyst-only) with `run_and_trace()`; log specialist step counts if you can reach them.
2. Same agent + task, three runs; compare `steps_taken` and the three `result.txt`s. Are they identical?

---

## 6. Course wrap-up — what you can now do

| Module | Capability |
|---|---|
| 01 | See the loop in a trace |
| 02 | Give the model a schema, not source |
| 03 | Pick code-as-action vs JSON-as-action |
| 04 | Retrieve open information; cite for real |
| 05 | Route on descriptions |
| 06 | Compare runs with data |

Those six are the spine of *any* agent stack.

### Where next (not this repo)

- **Longer curriculum:** [Hugging Face Agents Course](https://huggingface.co/learn/agents-course) — same library, more units.
- **MCP:** `ToolCollection.from_mcp` / `MCPClient` in smolagents — tools from an external server. One paragraph, not a seventh required module.
- **Eval:** three golden tasks, pass/fail against traces. Phoenix/Langfuse if you outgrow files.
- **Sandbox:** `executor_type` for CodeAgent the moment tools leave “tutorial.”
- **Other frameworks:** LangGraph, CrewAI, raw tool-calling APIs. Different org charts, same loop.

You do not need another framework to be done. You need a task, a tight tool list, and traces.

---

## 7. What you should be able to say out loud

- Observability is params + metrics + traces. The product name is optional.
- Autolog is convenient; manual logs teach you what “a run” is.
- I will not ship a multi-agent system I cannot diff.

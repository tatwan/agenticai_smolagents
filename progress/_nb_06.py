from _write_nb import ROOT, SETUP_CODE, SETUP_COLAB_INSTALL, SETUP_COLAB_SECRETS, SETUP_MD, write

cells = [
    (
        "md",
        """# Module 06: Observability (and course wrap-up)

This notebook is the **lab**. The lesson is [`outline.md`](outline.md).

Agents are non-deterministic programs. **Params / metrics / traces** are how you compare two of them. MLflow is the local implementation; Phoenix, Langfuse, and LangSmith are the same buckets with different UIs.

**You do not need `mlflow ui` to finish this module.** We log to a local SQLite file, then query it from Python. The UI is optional and **does not work in Colab**.

Errors: [`instructions.md`](instructions.md).
""",
    ),
    ("md", SETUP_MD),
    ("code", SETUP_COLAB_INSTALL),
    ("code", SETUP_COLAB_SECRETS),
    ("code", SETUP_CODE),
    (
        "md",
        """## Local SQLite tracking (no extra terminal)

MLflow 3.16 retired the default filesystem store. SQLite is still local and UI-optional.
""",
    ),
    (
        "code",
        r'''from pathlib import Path
import json
import time
import mlflow
from smolagents import CodeAgent, tool

db = (ROOT / "mlflow.db").resolve()
mlflow.set_tracking_uri(f"sqlite:///{db}")
mlflow.set_experiment("smolagents-course")
print("tracking URI:", mlflow.get_tracking_uri())
print("mlflow", mlflow.__version__)
''',
    ),
    (
        "md",
        """## Manual log — you should see the three buckets

A tiny `@tool` plus CodeAgent so this module does not depend on the web.
""",
    ),
    (
        "code",
        r'''@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words.

    Args:
        text: Sentence to count.
    """
    return len(text.split())

agent = CodeAgent(tools=[word_count], model=model, max_steps=8)
task = "How many words in 'observability is how we improve agents'? Double it."

with mlflow.start_run(run_name="manual-wordcount"):
    mlflow.log_params({
        "agent_type": "CodeAgent",
        "max_steps": 8,
        "model_id": getattr(model, "model_id", type(model).__name__),
        "task": task[:120],
    })
    t0 = time.perf_counter()
    result = agent.run(task)
    mlflow.log_metrics({
        "duration_seconds": time.perf_counter() - t0,
        "steps_taken": float(len(agent.memory.steps)),
    })
    mlflow.log_text(str(result), "result.txt")
    trace = [
        {"i": i, "type": type(s).__name__, "text": str(s)[:500]}
        for i, s in enumerate(agent.memory.steps)
    ]
    mlflow.log_dict({"steps": trace}, "steps_trace.json")
    print("result:", result)
    print("run_id:", mlflow.active_run().info.run_id if mlflow.active_run() else "(closed)")
''',
    ),
    (
        "md",
        """## Helper: `run_and_trace`

Same record, reusable. Use this in the exercises.
""",
    ),
    (
        "code",
        r'''def run_and_trace(agent, task: str, run_name: str, extra_params: dict | None = None):
    extra_params = extra_params or {}
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "agent_type": type(agent).__name__,
            "max_steps": getattr(agent, "max_steps", None),
            "model_id": getattr(getattr(agent, "model", None), "model_id", ""),
            "task": task[:120],
            **extra_params,
        })
        t0 = time.perf_counter()
        result = agent.run(task)
        duration = time.perf_counter() - t0
        mlflow.log_metrics({
            "duration_seconds": duration,
            "steps_taken": float(len(agent.memory.steps)),
        })
        mlflow.log_text(str(result), "result.txt")
        mlflow.log_dict(
            {
                "steps": [
                    {"i": i, "type": type(s).__name__, "text": str(s)[:500]}
                    for i, s in enumerate(agent.memory.steps)
                ]
            },
            "steps_trace.json",
        )
        return result, duration, len(agent.memory.steps)

fresh = CodeAgent(tools=[word_count], model=model, max_steps=8)
res, dur, n = run_and_trace(fresh, task, "helper-wordcount")
print(res, "steps", n, "s", round(dur, 2))
''',
    ),
    (
        "md",
        """## Autolog (after you understand the record)

One line, then run as usual. Inspect with `search_runs` — no UI required.
""",
    ),
    (
        "code",
        r'''mlflow.smolagents.autolog()
auto_agent = CodeAgent(tools=[word_count], model=model, max_steps=8)
auto_result = auto_agent.run("Count the words in 'autolog should still show a trace'.")
print("autolog result:", auto_result)

runs = mlflow.search_runs(experiment_names=["smolagents-course"])
print(runs[["run_id", "status", "metrics.steps_taken", "params.agent_type"]].head())
''',
    ),
    (
        "md",
        """## Optional UI

Local only:

```bash
uv run mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db
```

Open http://localhost:5000 → experiment `smolagents-course` → compare two runs. In Colab, skip this; `search_runs` above is the equivalent.
""",
    ),
    (
        "md",
        """## Exercises
""",
    ),
    (
        "code",
        r'''# TODO Exercise 1: trace a manager-style run
# Rebuild a tiny Module 05 manager (data_analyst on data/sample_sales.csv is enough).
# Wrap manager.run(...) with run_and_trace.
# If you can, also mlflow.log_metric("specialist_steps", len(data_analyst.memory.steps)).
#
# You succeeded if:
#   - search_runs shows a run named like "manager-sales"
#   - that run has steps_taken >= 2
#   - an artifact result.txt exists conceptually (you logged it)

# Your code here:
''',
    ),
    (
        "code",
        r'''# TODO Exercise 2: non-determinism, three times
# Same CodeAgent class + same task, three run_and_trace calls with names run-a/b/c.
# Print steps_taken and the three results.
#
# You succeeded if:
#   - three rows appear in search_runs for those names
#   - you wrote one sentence: identical / same facts different wording / disagreed
#   - you did not treat variance as a failed install

# Your code here:
''',
    ),
    (
        "md",
        """## Hints

<details>
<summary>search_runs filter</summary>

```python
mlflow.search_runs(experiment_names=["smolagents-course"], filter_string="attributes.run_name LIKE 'run-%'")
```

</details>
""",
    ),
    (
        "md",
        """## What you built (this module)

- A file-store experiment you can query without a server
- Manual logs so you know what a “run” contains
- Autolog as the modern shortcut, with eyes open about its gaps

## What you built (the course)

The loop, the schema, two action languages, retrieval, routing, traces.

**Next outside this repo:** [HF Agents Course](https://huggingface.co/learn/agents-course) · MCP via `ToolCollection.from_mcp` · a 3-task eval harness · a real CodeAgent sandbox.

You are done when you can watch a trace and say *why* the next tool was called — in smolagents or anywhere else.
""",
    ),
]

write(ROOT / "06_mlflow_observability" / "notebook.ipynb", cells)

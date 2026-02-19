# Module 06: MLflow Observability — Outline

## 1. Why Observability for Agents?

- **Non-determinism is the core challenge**: the same prompt can produce 3 steps or 8 steps, a confident answer or a hallucination. You cannot reason about what you cannot observe.
- **Debugging without traces is guesswork**: in a multi-agent system, when something goes wrong, you need to know which agent failed, at which step, and why — not just that the final output was wrong.
- **Systematic improvement requires data**: to answer "Why did run B perform better than run A?", you need structured records of both runs. Logging turns anecdotal observation into reproducible evidence.
- **Enables iteration**: once you can measure duration, step count, and output quality across runs, you can make deliberate changes and verify whether they helped.

---

## 2. MLflow Concepts Refresher

### Core objects

| Concept | What it is | Agent analogy |
|---------|-----------|---------------|
| **Experiment** | A named project grouping related runs | `smolagents-course` |
| **Run** | One execution within an experiment | A single `agent.run()` call |
| **Params** | Configuration values (strings/numbers logged once) | `model_id`, `max_steps`, `agent_type` |
| **Metrics** | Numeric measurements (can be logged over time) | `duration_seconds`, `steps_taken` |
| **Artifacts** | Files attached to a run | `result.txt`, `steps_trace.json` |

### MLflow UI walkthrough

- **Experiment view**: left sidebar lists all experiments; clicking one shows a table of all runs with param and metric columns visible at a glance.
- **Run detail view**: click a run name to see its full params, metrics timeline, and artifacts panel.
- **Artifacts panel**: navigate the file tree; text and JSON files render inline.
- **Compare view**: select two or more runs and click "Compare" to get a side-by-side diff of params and a chart overlay of metrics.

---

## 3. Logging Agent Runs Manually

### Pattern
```python
with mlflow.start_run(run_name="descriptive-name"):
    mlflow.log_param("key", value)      # configuration
    result = agent.run(task)
    mlflow.log_metric("steps_taken", len(agent.memory.steps))
    mlflow.log_text(str(result), "result.txt")
```

### What to log for agents

| Category | What | Why |
|----------|------|-----|
| Params | `model_id`, `agent_type`, `max_steps`, `task` (truncated) | Reproduce the exact setup |
| Metrics | `duration_seconds`, `steps_taken` | Measure efficiency |
| Artifacts | Final result text, step trace JSON | Inspect outputs and reasoning |

### Key API calls
- `mlflow.start_run(run_name=...)` — context manager; auto-ends the run on exit
- `mlflow.log_param(key, value)` — single param; or `mlflow.log_params({...})` for a dict
- `mlflow.log_metric(key, value)` — numeric measurement
- `mlflow.log_text(text, filename)` — saves a string as a file artifact
- `mlflow.log_dict(dict, filename)` — saves a dict as a JSON artifact

---

## 4. Step-Level Tracing

### Why step traces matter

The final result tells you *what* the agent produced. Step traces tell you *how* it got there — every tool call, every intermediate thought, every error and retry.

### Capturing steps
```python
steps_data = []
for i, step in enumerate(agent.memory.steps):
    steps_data.append({
        "index": i,
        "type": type(step).__name__,
        "content": str(step)[:500],   # truncate to avoid JSON size issues
    })
mlflow.log_dict({"steps": steps_data}, "steps_trace.json")
```

### Serialization gotchas
- `agent.memory.steps` contains rich objects; `str(step)` is the safest serialization
- Long tool outputs (web pages, code results) can make the JSON huge — always truncate with `[:500]`
- `type(step).__name__` gives you the step class (e.g., `ActionStep`, `PlanningStep`) without importing smolagents internals

---

## 5. Comparing Runs

### What to compare

| Metric | What it reveals |
|--------|----------------|
| `steps_taken` | Which agent type is more efficient? |
| `duration_seconds` | Which configuration is faster? |
| `steps_trace.json` artifacts | Where did each agent diverge in reasoning? |

### MLflow UI comparison workflow

1. Open the experiment view
2. Check the boxes next to the runs you want to compare
3. Click the **Compare** button
4. The comparison page shows: a params diff table (highlight differences), metric bar charts side by side, and a scatter plot if you have many runs
5. Use the **Search** bar to filter runs by param values, e.g. `params.agent_type = 'CodeAgent'`

### What matters most for agent iteration
- **Steps taken** is the most diagnostic metric: too few steps may mean the agent gave up; too many may indicate looping or inefficiency
- **Duration** often correlates with steps but can also reveal slow tool calls
- **Artifacts** are essential when metrics look similar but outputs differ

---

## 6. Exercises

### Exercise 1: Observing Multi-Agent Systems
Re-create the manager + specialist setup from Module 05. Wrap the `manager.run()` call using the `run_and_trace()` helper. Add an additional challenge: also log specialist step counts as separate metrics inside a manual `mlflow.start_run()` block. Inspect the artifacts to see which specialist did what.

### Exercise 2: Non-Determinism Experiment
Run the same agent and task 3 times, logging each as a separate MLflow run. Compare `steps_taken` and `duration_seconds` across all 3 runs in the UI. Download `result.txt` from each run. Are the answers identical? Different wording but same facts? Completely different? This is the empirical demonstration of agent non-determinism.

---

## 7. Course Wrap-Up

### The full learning arc

| Module | Concept | Skill |
|--------|---------|-------|
| 01 Foundations | The agent loop | Run a CodeAgent, inspect steps |
| 02 Tools | Tool design | @tool decorator, Tool subclass, schema |
| 03 Agent Types | CodeAgent vs ToolCallingAgent | Choose the right agent for the job |
| 04 Web Search | Retrieval-augmented agents | DuckDuckGo, VisitWebpage, research workflows |
| 05 Multi-Agent | Orchestration | Manager + specialists, delegation patterns |
| 06 Observability | MLflow | Log, trace, compare, improve |

### The through-line

Each module added one capability layer: you can now build an agent that uses tools, browses the web, delegates to specialists, and produces structured logs you can analyze. The combination is a production-ready pattern for building and iterating on agentic systems.

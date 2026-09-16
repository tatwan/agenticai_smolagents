# Module 05: Multi-Agent Orchestration

**Read this first**, then run `notebook.ipynb`.

**Time:** 90–120 minutes · **Depends on:** Modules 01–04

---

## 1. What is a multi-agent system?

A **single** agent is one loop, one tool bag, one context window.

A **multi-agent** system is several loops, coordinated. The common teaching shape (and the one smolagents implements) is **manager + specialists**:

- The manager sees the user task.
- It does **not** hold every tool.
- It calls another agent the way it would call a tool: “you do this subtask,” then reads a string back.

This is older than the 2025 hype. It is how you already split work among people: a researcher, an analyst, a writer, a manager who only routes.

Other shapes you will meet later (not required here):

| Shape | Idea |
|---|---|
| Manager / specialist (this module) | One router, many workers |
| Sequential pipeline | A → B → C, no router |
| Peer debate | Two agents critique each other |
| Swarm / blackboard | Shared state, many writers |

MCP, “skills,” and sub-agents in coding tools are the same *idea*: **narrow workers + a policy for who runs when.**

---

## 2. When to split (and when not to)

Split when **one context window and one tool list would fight themselves**:

- Research (noisy web) vs arithmetic (must be exact)
- A writer who should not be allowed to search
- You want to inspect *which* specialist failed

Do **not** split when:

- One skill does the job
- The handoff cannot be a string (you need a shared object graph)
- Latency or token cost matters more than modularity — **each specialist call is more LLM calls**
- A Python script would do (ETL, a fixed pipeline)

Multi-agent is an organization chart. Organization charts have overhead. Draw one only when the work is actually different jobs.

---

## 3. How routing works: descriptions are the table

The manager does not get a secret `if` statement you wrote. It gets **text**:

```
You can also give tasks to team members.
- web_researcher: Searches the web and visits pages. Pass a specific question.
  Returns a short summary with source URLs.
- data_analyst: Analyzes a local CSV path. Pass the path and the question.
  Returns numbers, not prose.
```

That list is built from each specialist’s `name` and `description`. If the description is vague, routing is vague. This is Module 02’s schema lesson, one level up.

**Write descriptions that answer:**

1. What does this worker do?
2. What should the task string look like?
3. What comes back?

Specialists are **stateless across manager calls**. If the analyst needs a path, the manager must put that path in the task string every time.

Keep `max_steps` small on specialists (2–6). They should not wander. The manager can have a slightly higher budget.

---

## 4. How smolagents implements this

There is **no** `ManagedAgent` wrapper in current smolagents. (The February 2026 design doc is stale.) You set `name` and `description` **on the agent**, then pass the objects in:

```python
researcher = ToolCallingAgent(
    tools=[WebSearchTool(), VisitWebpageTool()],
    model=model,
    name="web_researcher",
    description=(
        "Web research specialist. Pass a specific factual question. "
        "Returns a short answer with source URLs."
    ),
    max_steps=6,
)

analyst = CodeAgent(
    tools=[csv_tool],
    model=model,
    name="data_analyst",
    description=(
        "Local CSV analyst. Pass a file path and a numeric question. "
        "Returns figures, not a blog post."
    ),
    max_steps=4,
)

manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[researcher, analyst],
    max_steps=10,
)
```

`manager.managed_agents` is a **dict keyed by name**. Iterate `.values()` if you want the objects.

Mix types on purpose: a JSON-calling researcher (no arbitrary code) and a CodeAgent analyst (needs pandas-via-tool). The manager can be either type; `CodeAgent` is a reasonable default so it can stitch numbers in Python after the handoffs.

---

## 5. Inspecting delegation

After `manager.run(...)`, walk `manager.memory.steps`. You are looking for tool calls whose names are `web_researcher` / `data_analyst`. Nested traces live on the specialist’s own `memory` **for that call** — print them if you need to debug a bad handoff.

Cost: manager tokens + every specialist run. Two specialists on a toy task can be 5–10× a single agent. That is why “when not to” is part of the lesson, not a footnote.

---

## 6. Exercises

1. Add `report_writer` (formatting only, no search). Confirm all three names appear in the manager trace.
2. Analyst on **`data/sample_sales.csv`** (do not depend on a URL the researcher “found”). Optional stretch: researcher finds a *public* CSV URL and the manager passes that string through — if the download fails, fall back to the local file.

---

## 7. What you should be able to say out loud

- Multi-agent is an org chart, not a smarter model.
- The manager routes on **descriptions**.
- Handoffs are strings. If it is not in the task, the specialist does not have it.
- I can name three reasons *not* to split.

**Next — Module 06.** Non-determinism plus nested calls means you need traces you can compare. Manual MLflow first, then `mlflow.smolagents.autolog()`.

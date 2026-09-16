# Module 05: Multi-Agent Orchestration — how to run this lab

**Module:** 05 of 06  
**Read first:** [`outline.md`](outline.md)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

- Build specialists with `name` and `description` on the agent (no `ManagedAgent` wrapper)
- Pass them to a manager via `managed_agents=`
- Treat descriptions as the routing table
- Inspect `manager.memory.steps` and `manager.managed_agents` (a dict)
- Decide when *not* to use multi-agent

---

## Prerequisites

- Modules 01–04
- `data/sample_sales.csv` in the repo
- Web specialist may flake (Module 04). The analyst path is local and should still run.

---

## Estimated time

90–120 minutes

---

## How to run

```bash
uv run jupyter lab 05_multi_agent_orchestration/notebook.ipynb
```

---

## Common errors

### 1. Manager never calls a specialist

The description did not match the user task, or `name` is missing. Print `manager.managed_agents.keys()`. Rewrite descriptions with “pass X, return Y.”

### 2. `ManagedAgent` import fails

That class is not what current smolagents uses. Put `name=` / `description=` on `CodeAgent` / `ToolCallingAgent`.

### 3. Specialist “forgets” the CSV path

Each call is stateless. The manager must include the path in the task string it sends.

### 4. Web researcher 429 / empty search

Same as Module 04. Use `engine="bing"` or skip the web half and still complete the analyst + manager wiring.

### 5. Analyst invents numbers (e.g. “1000 rows”)

Small local models often skip `csv_summary` and write a plausible report. The **wiring still worked** if `data_analyst` appears in the manager trace. Read `data_analyst.memory.steps`. Switch to the Hub default or a larger Ollama coder if you need the numbers to be true.

### 6. Token / latency blow-up

Lower `max_steps` on specialists. Do not give the manager the same tools the specialists have.

---

## Tips

- One responsibility per specialist.
- Manager `tools=[]` in the guided example on purpose.
- After a run: `list(manager.managed_agents)` should be the names you chose.

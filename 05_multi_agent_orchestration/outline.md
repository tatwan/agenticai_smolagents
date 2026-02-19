# Module 05: Multi-Agent Orchestration — Outline

## 1. Why Multi-Agent?

Single agents accumulate tools and responsibilities over time, making them difficult to manage and debug. Multi-agent systems solve this through:

- **Specialization**: Each agent does one job well. A web researcher focuses on retrieval; a data analyst focuses on computation. Neither is asked to do both.
- **Modularity**: Swap or upgrade a specialist without touching the manager or other specialists. If the web researcher needs a new tool, only that agent changes.
- **Easier debugging**: When something goes wrong, you can trace which agent failed. A specialist that returned bad data is easier to isolate than a monolithic agent with ten tools.

---

## 2. The Manager + Managed Agent Pattern

The core pattern in smolagents multi-agent systems:

- The **manager agent** has **no tools** of its own — only a `managed_agents` list.
- Each **managed agent** (specialist) has a `name` and `description` that the manager uses to decide who to call and with what task.
- The manager calls a specialist like a tool, passing a **task string** as the argument.
- The specialist runs its own internal loop and returns a result string.
- The manager incorporates that result and continues reasoning.

Key detail: `managed_agents` is a list passed at construction time. The manager cannot add or remove specialists at runtime.

---

## 3. Agent-as-Tool Concept

smolagents wraps each managed agent so that it appears to the manager as a callable tool:

- The specialist's `name` becomes the tool name.
- The specialist's `description` becomes the tool's docstring — the manager reads this to understand what the specialist does and what input to send.
- Calling the specialist with a task string triggers the specialist's full run loop.

The `name` and `description` on the specialist are critical. If the description is vague, the manager may route incorrectly, call the wrong specialist, or try to answer the task itself.

---

## 4. Designing Specialist Agents

### One Responsibility Rule
Each specialist should have a single, well-defined job. A specialist that researches, analyzes, and formats output is hard to debug and easy to misuse. Keep responsibilities narrow.

### Stateless Across Calls
Each call to a specialist is independent. The specialist does not retain memory between calls from the manager. Do not rely on a specialist remembering context from a previous invocation.

### Description Quality Drives Manager Decisions
The description should answer three questions:
1. What does this specialist do?
2. What format should the input (task string) be in?
3. What does it return?

Example of a strong description: "Searches the web and visits pages to retrieve factual, up-to-date information. Provide a specific research question as the task. Returns a concise summary with source URLs."

### Appropriate max_steps Per Specialist
Match `max_steps` to the complexity of the specialist's job:
- Web researcher: 5–8 steps (search, visit, synthesize)
- Data analyst: 2–4 steps (parse, compute, return)
- Report formatter: 2–3 steps (structure text, return)

Setting `max_steps` too low causes the specialist to time out before completing its task.

---

## 5. Information Flow Between Agents

- **Task in**: The manager passes a plain string to the specialist. This string should contain all context the specialist needs — the specialist cannot ask follow-up questions.
- **Result out**: The specialist returns a string (its final answer). The manager reads this string and incorporates it into its reasoning.
- **Context window limits**: Each specialist result is added to the manager's context window. If specialists return very long results, the manager's context fills quickly. Design specialists to return concise, structured summaries.
- **Passing structured data**: If the manager needs to pass numbers, dates, or other structured data to a specialist, it passes them as formatted strings (e.g., comma-separated values). The specialist is responsible for parsing them.

---

## 6. When NOT to Use Multi-Agent

Multi-agent adds overhead (latency, tokens, complexity). Avoid it when:

- **Single-task work**: The task requires only one skill (e.g., pure web search, pure calculation). A single agent with appropriate tools is simpler and faster.
- **Tight coupling between steps**: If step 2 depends on the exact intermediate state of step 1 in a way that cannot be expressed as a string, multi-agent handoffs become fragile.
- **Latency-sensitive use cases**: Each specialist call is a separate LLM invocation. Multi-agent systems are slower than single agents. If response time matters, prefer a single agent.
- **Simple, predictable tasks**: Multi-agent shines on open-ended, multi-domain tasks. Deterministic pipelines (e.g., ETL) are better served by code, not agents.

---

## 7. Exercises

### Exercise 1: Add a Report Writer Specialist
Add a third specialist (`report_writer`) to the existing manager + web_researcher + data_analyst system. The report writer should format findings into a structured markdown report with sections: Summary, Key Findings, Data Analysis, Conclusion. Run the manager on a combined research + analysis + formatting task and verify all three specialists are used.

### Exercise 2: Data Pipeline Multi-Agent System
Design a two-specialist system where the first specialist finds a public CSV dataset URL for a topic of your choice, and the second specialist analyzes that CSV using the `CSVSummaryTool` from Module 02. The challenge: can the first specialist's output (a URL string) be passed to the second specialist via the manager's task string? Experiment with how to structure the manager's task to make this work.

---

## 8. Summary + Module 06 Preview

### Summary
Multi-agent orchestration divides complex tasks between specialists coordinated by a manager. The manager has no tools — only other agents. Specialist descriptions are the manager's routing table. Each specialist is stateless, single-responsibility, and sized with appropriate `max_steps`.

### Module 06 Preview: MLflow Observability
Multi-agent systems are powerful but non-deterministic. The same prompt can take different paths, call different specialists, and produce different results. Module 06 adds MLflow to record every run: which model was used, which tools were called, how many steps each agent took, and how long it ran. This observability layer is how you iterate on agent design scientifically rather than by intuition.

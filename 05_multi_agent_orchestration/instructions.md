# Module 05: Multi-Agent Orchestration

## Learning Objectives

By the end of this module you will be able to:

1. Build a manager agent that delegates to specialist agents using `managed_agents`
2. Build specialist agents with focused single responsibilities and clear descriptions
3. Wire manager and specialists together and run a combined multi-domain task
4. Inspect `manager.memory.steps` to trace when and how delegation occurred
5. Apply multi-agent design principles: one-responsibility rule, stateless specialists, description quality, and appropriate `max_steps`

---

## Prerequisites

- Module 01: Foundations (agent basics, run loop, memory)
- Module 02: Tools and Custom Tools (custom `@tool` decorator, `CSVSummaryTool` used in Exercise 2)
- Module 03: CodeAgent vs ToolCallingAgent (know when to use each agent type)
- Module 04: Web Search and Browsing (`DuckDuckGoSearchTool`, `VisitWebpageTool` are used in the web_researcher specialist)

---

## Estimated Time

75–90 minutes

---

## How to Run

From the repository root, run:

```bash
uv run jupyter lab 05_multi_agent_orchestration/notebook.ipynb
```

Ensure your `.env` file contains a valid `HF_TOKEN` before starting.

---

## Common Errors and Fixes

### 1. Manager calls specialist with wrong format

**Symptom**: The manager passes a full paragraph or structured dict instead of a plain research question. The specialist produces an irrelevant or confused result.

**Cause**: The specialist's description does not explicitly tell the manager what format to use for the task string.

**Fix**: Add a sentence to the description that says exactly what to pass, for example: "Provide a specific research question as the task." The manager reads the description as its routing table — format instructions must be in there.

---

### 2. Specialist max_steps too low

**Symptom**: The specialist returns an incomplete or empty result. The manager's answer is thin or incorrect.

**Cause**: Web research requires multiple steps — at minimum: search query, visit page, extract information, synthesize. If `max_steps` is set to 2 or 3, the specialist runs out of steps before it can return a useful answer.

**Fix**: Set `max_steps` to at least 5–6 for any specialist that involves web search. Data analysts and formatters can use 2–4 steps.

---

### 3. Context window overflow

**Symptom**: An error about token limits, or the manager starts ignoring earlier specialist results.

**Cause**: Specialist results are added to the manager's context window. If a specialist returns a very long response (e.g., a full webpage), the manager's context fills quickly, especially when multiple specialists are called.

**Fix**: Design specialist descriptions to ask for concise summaries, not raw content. For example: "Returns a concise summary with source URLs" signals to the specialist that it should not dump full webpage text into its answer.

---

### 4. Manager not delegating

**Symptom**: The manager tries to answer the task from its own training knowledge instead of calling a specialist. The memory steps show no delegation.

**Cause**: The specialist descriptions are too generic. The manager does not recognize that the specialist is the right tool for this task.

**Fix**: Strengthen the specialist descriptions to be specific about what the specialist knows and does. For example, instead of "Helps with web tasks", use "Searches the web and visits pages to retrieve factual, up-to-date information. Provide a specific research question as the task. Returns a concise summary with source URLs." The manager is more likely to delegate when the description clearly maps to the task at hand.

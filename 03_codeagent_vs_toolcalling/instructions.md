# Module 03: CodeAgent vs ToolCallingAgent — how to run this lab

**Module:** 03 of 06  
**Read first:** [`outline.md`](outline.md)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

- Explain code-as-action vs JSON-as-action without naming smolagents
- Run the **same** tool and task on `CodeAgent` and `ToolCallingAgent` and describe the traces
- Choose an agent type with the decision framework
- Know what to do when a model cannot tool-call
- (Optional) Swap `InferenceClientModel` for `LiteLLMModel` / `OpenAIModel`

---

## Prerequisites

- Modules 01–02
- A model that can write Python (CodeAgent). ToolCallingAgent additionally needs **native tool calling**. Small Ollama checkpoints (3B) often fail that path — the notebook treats a clean failure as data, not a broken lab.

---

## Estimated time

60–75 minutes

---

## How to run

```bash
uv run jupyter lab 03_codeagent_vs_toolcalling/notebook.ipynb
```

The OpenAI / Anthropic cell is commented and optional. Skip it unless you have that key.

---

## Common errors

### 1. ToolCallingAgent emits no tool calls / parse errors

The model does not support native function calling, or the local checkpoint is too small.

Fix: switch to the Hub default (`Qwen/Qwen3-Next-80B-A3B-Thinking`) or a larger local coder (`qwen2.5-coder:7b` or 14b). If you cannot, **record the failure** in the comparison table and finish CodeAgent. Do not silently swap in CodeAgent and call it ToolCallingAgent.

### 2. Different step counts on two runs

Expected. Agents are non-deterministic. Compare *structure* (Python vs JSON), not exact hop counts.

### 3. Optional OpenAI cell raises `AuthenticationError`

Skip it, or set `OPENAI_API_KEY` in `.env` and restart the kernel.

### 4. `num_ctx` too small on Ollama

LiteLLM + Ollama defaults can truncate agent prompts. `course_setup.py` sets `num_ctx=8192`. If you instantiate `LiteLLMModel` yourself, pass `num_ctx=8192` or higher.

---

## Tips

- Print `type(step).__name__` and `step.tool_calls` for both agents on the **same** task before you theorize.
- CodeAgent “winning” a loop task is the intended observation, not a bug in ToolCallingAgent.
- If CodeAgent imports a library you did not allow, that is the sandbox working. Use a tool instead, or pass `additional_authorized_imports` deliberately.

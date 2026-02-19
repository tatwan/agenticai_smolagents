# Module 03: CodeAgent vs ToolCallingAgent

## Learning Objectives

By the end of this module you will be able to:

1. **Understand the CodeAgent execution model** — explain how CodeAgent generates Python code, executes it in a sandbox, and observes the result at each reasoning step
2. **Understand the ToolCallingAgent execution model** — explain how ToolCallingAgent generates structured JSON tool calls and relies on the framework to dispatch them
3. **Compare both agent types on identical tasks** — run the same tool and task through both agents and read the internal step logs to see the structural differences
4. **Apply the decision framework** — given a task description, choose the appropriate agent type using the criteria covered in the module
5. **Swap model providers** — replace `InferenceClientModel` with `LiteLLMModel` to run the same agent code against OpenAI, Anthropic, or Ollama

---

## Prerequisites

- Module 01 (Foundations) complete
- Module 02 (Tools and Custom Tools) complete
- `HF_TOKEN` set in your `.env` file

---

## Estimated Time

60–75 minutes

---

## How to Run

From the repository root:

```bash
uv run jupyter lab 03_codeagent_vs_toolcalling/notebook.ipynb
```

Run all cells in order from top to bottom. Cells marked **OPTIONAL** can be skipped if you do not have the relevant API key.

---

## Optional Section

The notebook includes one optional cell that demonstrates swapping to an OpenAI-backed model using `LiteLLMModel`. This cell:

- Is clearly marked with `# ── OPTIONAL: requires OPENAI_API_KEY in .env ──`
- Is commented out by default — nothing runs unless you explicitly uncomment it
- Is **not required** to complete any exercise or meet any learning objective

The module is **fully completable without an OpenAI API key**. The HuggingFace-backed cells cover all concepts.

---

## Common Errors

### 1. ToolCallingAgent with a model that does not support function calling

**Symptom:** The agent fails to produce valid tool call JSON, throws a parsing error, or calls no tools at all.

**Cause:** Not all models support native function/tool calling. ToolCallingAgent depends on the model's ability to emit structured JSON in the exact tool-call format.

**Fix:** Use `Qwen/Qwen2.5-Coder-32B-Instruct`, which supports function calling and is set as the default model in the setup cell. Do not swap to a model that lacks tool-calling support without verifying its capabilities first.

---

### 2. OPENAI_API_KEY not set

**Symptom:** A `KeyError` or `AuthenticationError` when running the optional OpenAI cell.

**Cause:** The optional cell reads `os.environ.get("OPENAI_API_KEY")`. If the key is not in your `.env` file, the value will be `None` and the API call will fail.

**Fix:** The cell is clearly marked optional — skip it. If you want to run it, add `OPENAI_API_KEY=sk-...` to your `.env` file and reload the environment with `load_dotenv()`.

---

### 3. Step count differs between runs

**Symptom:** You run the same agent twice and see a different number of steps in the output (e.g., 3 steps one time, 4 steps another time).

**Cause:** LLM agents are non-deterministic. The model may take a slightly different reasoning path on different runs even with the same prompt and tools. This is expected behaviour, not a bug.

**Fix:** No fix needed. The final answer should be consistent even if the path varies. Focus on the *type* of steps (code blocks vs. JSON calls) rather than the exact count.

---

## Key Insight

> **The same smolagents code works with any LLM backend — this is the library's biggest architectural win.**

The agent API (`CodeAgent`, `ToolCallingAgent`, `.run()`) is completely decoupled from the model. Switching from HuggingFace to OpenAI to Anthropic to a local Ollama instance requires changing one or two lines — the model instantiation — and nothing else. This makes smolagents-based systems portable across providers, cost tiers, and deployment environments without rewriting agent logic.

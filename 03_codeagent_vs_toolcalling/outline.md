# Module 03: CodeAgent vs ToolCallingAgent

**Read this first**, then run `notebook.ipynb`.

**Time:** 60–75 minutes · **Depends on:** Modules 01–02

---

## 1. What is actually different?

The **loop** is the same: think → act → observe → stop.

The **action language** is different:

| | Code as action | JSON as action |
|---|---|---|
| The model writes | A Python snippet | `{"name": "...", "arguments": {...}}` |
| The harness does | Execute in an interpreter | Look up the tool and call `forward()` |
| Between tool calls the model can | Loop, branch, do math, stitch results | Only reason in text, or call another tool |
| Blast radius | Whatever the interpreter allows | Whatever **your tools** allow |
| Model requirement | “Can write plausible Python” | **Native tool / function calling** |

This split exists everywhere, not only in smolagents:

- OpenAI Assistants / Chat Completions `tools=` → JSON as action
- Anthropic `tools` → JSON as action
- A ReAct prompt that asks for `Action: python` → code as action
- LangGraph nodes that `eval` generated code → code as action (please sandbox)

smolagents just names the two dialects `CodeAgent` and `ToolCallingAgent`.

---

## 2. When to pick which

**Choose code-as-action (`CodeAgent`) when:**

- The path needs computation the tools do not already encapsulate (medians, joins, unit conversions on the fly)
- You are prototyping and want the model to improvise
- Your model is a **coder** but does **not** support native tool calling

**Choose JSON-as-action (`ToolCallingAgent`) when:**

- The job is *dispatch*: pick a tool, fill arguments, stop
- You need an auditable call log (compliance, regulated workflows)
- You cannot give the model a general-purpose interpreter
- Your model **does** support tool calling (most current frontier / routed models; **not** every Hub id)

**Rule of thumb:** if the agent must *think computationally*, use CodeAgent. If it must *dispatch reliably*, use ToolCallingAgent.

Same task, two types, read the traces — that experiment is this module. Do not skip it.

### When the model cannot tool-call

This is why smolagents left `Qwen/Qwen2.5-Coder-32B-Instruct` as the default: many Inference Providers for that checkpoint **do not implement tool calling**. `ToolCallingAgent` then emits garbage or empty calls.

If you see parse errors, `0` tool calls, or “this model does not support tool calling”:

1. Switch `COURSE_MODEL_ID` / provider
2. Or skip `ToolCallingAgent` on that backend and record the failure — that *is* the lesson
3. Do not “fix” it by wrapping CodeAgent and pretending it is JSON

Small local models (3B) often fail ToolCallingAgent. A 7B+ coder, or the Hub default, is more honest.

---

## 3. How it looks in the trace

**CodeAgent (sketch):**

```
Thought: I need a count, then double it.
<code>
n = word_count("The quick brown fox")
print(n * 2)
</code>
Observation: 8
<code>
final_answer(8)
</code>
```

**ToolCallingAgent (sketch):**

```
call word_count(text="The quick brown fox")
Observation: 5
final_answer(5)
```

Notice: the JSON agent **cannot multiply in the interpreter**. It must either (a) put the doubling in the tool, (b) do it in the final natural-language answer (unreliable), or (c) call a second math tool. That is the architectural point of Exercise 2.

---

## 4. How smolagents wires this

```python
from smolagents import CodeAgent, ToolCallingAgent, tool

@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words.

    Args:
        text: The sentence to count.
    """
    return len(text.split())

code_agent = CodeAgent(tools=[word_count], model=model, max_steps=8)
json_agent = ToolCallingAgent(tools=[word_count], model=model, max_steps=8)

task = "How many words in 'The quick brown fox jumps over the lazy dog'? Double it."
code_agent.run(task)
json_agent.run(task)
```

Then compare `memory.steps`: types, whether `.tool_calls` look like Python or JSON, step counts.

`add_base_tools=True` is still off unless you want search in the mix.

### Model plug

`LiteLLMModel` talks to OpenAI, Anthropic, Gemini, Ollama, … with a model id string. `OpenAIModel` (also exported as `OpenAIServerModel`) talks to any OpenAI-compatible HTTP server.

Example ids **change**. Treat these as shapes, not eternal defaults:

| Backend | Shape |
|---|---|
| Hugging Face | `InferenceClientModel(model_id="Qwen/Qwen3-Next-80B-A3B-Thinking")` |
| Ollama | `LiteLLMModel(model_id="ollama_chat/qwen2.5-coder:7b", api_base="http://localhost:11434", num_ctx=8192)` |
| OpenAI | `LiteLLMModel(model_id="gpt-4.1-mini")` or `OpenAIModel(...)` |
| Anthropic | `LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")` |

The agent constructor does not change. That is the portability win.

Optional OpenAI cell in the notebook is **optional**. The module is complete without a paid key.

---

## 5. Safety (code-as-action)

`CodeAgent`’s interpreter is restricted (import allow-list, time limit). Restricted is not a VM.

For production: `executor_type` → Docker / E2B / Blaxel / Modal, documented in [secure code execution](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution). We stay local in this course.

`ToolCallingAgent` has no general interpreter. Prefer it when the allow-list of tools *is* your security policy.

---

## 6. Exercises

1. `count_vowels` on both agent types; compare traces.
2. A loop-y task (“word with the most letters”) on both; write 2–3 sentences on which type won and why.

---

## 7. What you should be able to say out loud

- Same loop, two action languages.
- I pick code-as-action for computation, JSON-as-action for dispatch and a smaller blast radius.
- ToolCallingAgent is not “the production version of CodeAgent”; it is a different bet, and it **requires** tool-calling models.
- Swapping OpenAI for Ollama is a model-class change, not an agent-class change.

**Next — Module 04.** Tools that leave the machine: search, then visit, then extract. Closed weights are not enough for “what shipped this week.”

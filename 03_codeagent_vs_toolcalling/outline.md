# Module 03: CodeAgent vs ToolCallingAgent — Outline

---

## 1. How CodeAgent Thinks

CodeAgent reasons by generating executable Python code. At each step, the model writes a code block, the framework executes it inside a sandboxed interpreter, and the agent observes the result (stdout or return value) before deciding what to do next.

**Internal "thought" structure (example):**

```
Thought: I need to count the words in the sentence, then double the result.
Code:
```python
count = word_count("The quick brown fox jumps over the lazy dog")
result = count * 2
print(result)
```<end_code>
Observation: 18
```

The agent can perform arbitrary computation between tool calls — loops, conditionals, string manipulation, math — because it is writing and running real Python. This is powerful but introduces a meaningful security surface: **arbitrary code execution** in the host environment. In production, this requires a hardened sandbox (e.g., E2B, Docker, or the built-in restricted interpreter).

---

## 2. How ToolCallingAgent Thinks

ToolCallingAgent reasons by generating structured JSON that names a tool and provides arguments. The framework parses the JSON, looks up the matching registered tool, calls it with the supplied arguments, and returns the observation.

**Internal "thought" structure (example):**

```
Thought: I need to call word_count with the sentence.
Tool call:
{
  "tool_name": "word_count",
  "arguments": {
    "text": "The quick brown fox jumps over the lazy dog"
  }
}
Observation: 9
```

There is no code execution. The agent can only call tools by name. All inter-step logic must either be handled by tool implementations or encoded in the model's final answer. The call structure is predictable, auditable, and does not expose a code execution surface.

---

## 3. Side-by-Side Comparison

| Dimension | CodeAgent | ToolCallingAgent |
|---|---|---|
| **Execution model** | Generates Python code, executes in sandbox, observes stdout/return | Generates JSON `{tool_name, arguments}`, framework dispatches to tool, observes return |
| **Inter-step logic** | Full Python available — loops, conditionals, math, string ops, list comprehensions | None — logic must live in tool implementations or in the final LLM answer |
| **Security** | Arbitrary code execution surface; requires sandbox hardening for production | No code execution; attack surface limited to tool implementations themselves |
| **Output predictability** | Non-deterministic execution path; code shape varies per run | Structured, auditable call log; identical inputs tend to produce identical call sequences |
| **Model requirements** | Any model capable of writing Python; does not require native function-calling support | Model must support native function/tool calling (e.g., OpenAI function calling, Qwen tool calling) |
| **Best for** | Compute-heavy, open-ended, or multi-step reasoning tasks where the solution path is unclear upfront | Dispatch-heavy tasks where tools do the work, auditability matters, or security constraints apply |

---

## 4. Decision Framework

Use the following rules to choose the right agent type for a task:

**Choose `CodeAgent` when:**
- The task requires computation, loops, or data manipulation between tool calls
- You need the agent to do math, string processing, or list operations on tool results
- The solution path is open-ended and not predictable in advance
- You trust the execution environment (internal infrastructure, trusted tooling)
- The model you are using may not support native function calling

**Choose `ToolCallingAgent` when:**
- Tool calls are the primary action — the agent just needs to dispatch to tools
- You need structured, auditable logs of exactly what was called and with what arguments
- Security matters — you cannot afford an arbitrary code execution surface
- Your LLM supports native function/tool calling (most modern frontier models do)
- You are building production systems where predictability and reproducibility outweigh flexibility

**Rule of thumb:** If your agent needs to *think computationally*, use `CodeAgent`. If your agent needs to *dispatch reliably*, use `ToolCallingAgent`.

---

## 5. Model Agnosticism

smolagents separates the agent logic from the model backend via a model abstraction layer. The agent API (`agent.run(task)`) is identical regardless of which LLM is behind it.

**Built-in model wrappers:**

| Wrapper | Backend |
|---|---|
| `InferenceClientModel` | HuggingFace Inference API (default for this course) |
| `LiteLLMModel` | Any provider supported by LiteLLM (100+ providers) |
| `TransformersModel` | Local HuggingFace model via `transformers` |
| `OpenAIServerModel` | Any OpenAI-compatible REST endpoint |

**Swapping model providers requires 2 lines:**

```python
# From this:
model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", token=HF_TOKEN)

# To this (OpenAI):
from smolagents import LiteLLMModel
model = LiteLLMModel(model_id="gpt-4o-mini", api_key=OPENAI_API_KEY)

# To this (Anthropic):
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-latest", api_key=ANTHROPIC_API_KEY)

# To this (Ollama — local, free):
model = LiteLLMModel(model_id="ollama_chat/llama3.2", api_base="http://localhost:11434")
```

The agent instantiation and `.run()` call are untouched. This is smolagents' biggest architectural win for portability.

---

## 6. Exercises

### Exercise 1: Vowel Counting Comparison

1. Write a `@tool` called `count_vowels` that counts vowels (a, e, i, o, u — case insensitive) in a string.
2. Run the task `"Count the vowels in: 'HuggingFace builds amazing open source tools'"` with both `CodeAgent` and `ToolCallingAgent`.
3. Compare the intermediate steps:
   - Which agent wrote code? Which emitted JSON?
   - Which produced cleaner, more readable steps?
   - Did both agents produce the same final answer?

**Learning goal:** Observe the structural difference in how each agent type records its reasoning.

### Exercise 2: Loop Task Comparison

Design a task that requires iteration:
> "For each word in `['python', 'data', 'engineer', 'agent']`, count its letters and return the word with the most letters."

1. Try `ToolCallingAgent` first. Observe whether and how it handles the iteration.
2. Then try `CodeAgent`. Note what is different in the steps.
3. Write 2–3 sentences explaining which agent type is better suited for this task and why.

**Learning goal:** Understand why `CodeAgent` has a structural advantage for tasks that require in-agent computation across multiple values.

---

## 7. Summary + Module 04 Preview

### Summary

- `CodeAgent` generates Python, executes it in a sandbox, and can reason computationally between tool calls. Powerful but requires a trusted execution environment.
- `ToolCallingAgent` generates structured JSON tool calls, dispatches them through the framework, and produces auditable, reproducible call logs. No code execution surface.
- Both agents share the same smolagents API. Swapping one for the other is a one-line change.
- smolagents is model-agnostic: `LiteLLMModel` connects to OpenAI, Anthropic, Ollama, and 100+ other providers with no changes to agent code.

### Module 04 Preview: Web Search & Browsing

In Module 04, agents move from static tools to live internet access. You will connect agents to `DuckDuckGoSearchTool` and `VisitWebpageTool`, giving them the ability to retrieve real-time information and reason over web content. This opens up a new class of research and retrieval tasks that were not possible with purely static tooling.

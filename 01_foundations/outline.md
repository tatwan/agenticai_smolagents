# Module 01: Foundations — The Agent Loop

**Read this first**, then run `notebook.ipynb`. This page is the lesson. The notebook is the lab.

**Time:** 60–90 minutes · **You need:** Python 3.10+, a working model backend (see the README)

---

## 1. What is an AI agent?

A **chatbot** is a function:

```
prompt  →  language model  →  text
```

One call. The model cannot check its work, look anything up, or recover from a mistake except by what it already “knows” in its weights.

An **agent** is a loop:

```
task  →  think  →  act  →  observe  →  think  →  …  →  stop
```

The model still only produces text. What changed is the **harness around it**: something parses that text into an action, executes the action in the real world (code, an API, a search, another agent), and feeds the result back. The next model call sees the history, including failures.

That loop is older than smolagents. You will meet it as ReAct, as “tool-calling,” as LangGraph nodes, as a `while` loop you write yourself. The product names change. The loop does not.

### Three parts you can name in any stack

| Part | What it is | What it is not |
|---|---|---|
| **Model** | A next-token generator you can call with a list of messages | A planner, a database, or a source of truth |
| **Tools / actions** | Functions the harness is willing to run on the model’s behalf | Magic the model “has.” If it is not in the tool list, the model cannot do it |
| **Loop / policy** | Rules for “call the model → parse → execute → stop or continue” | The model’s personality. Stopping is a harness decision (`final_answer`, `max_steps`, a human) |

**Mental model:** the LLM is a noisy CPU. The agent is the operating system: it schedules the CPU, offers syscalls (tools), and kills the process when it runs too long.

---

## 2. When to use an agent (and when not to)

Use an agent when **you cannot write the steps in advance**:

- The number of lookups depends on what the first lookup returns
- The model must try something, see an error, and try a different approach
- The task mixes reasoning with the outside world (files, APIs, the web)

Do **not** use an agent when a single LLM call, a regex, or a Python script would do:

| Job | Better tool |
|---|---|
| Rewrite this paragraph in a calmer tone | One chat completion |
| Extract JSON from a known schema | Structured output / a parser |
| Compute the 15th Fibonacci number *if you already know the algorithm* | Five lines of Python, no LLM |
| “Figure out what this CSV is, clean it, and chart the anomaly” | Agent (unknown path) |

Agents are slower, more expensive, and less reproducible than functions. You pay that cost to buy **flexibility**. If you do not need flexibility, do not pay.

This course uses small tasks (Fibonacci, word counts) so you can **see the loop**, not because those tasks need an agent in production.

---

## 3. How the loop actually runs

```
        ┌──────────────────────────────────────────────────────┐
        │                    AGENT LOOP                        │
        │                                                      │
        │   ┌──────────┐     ┌──────────┐     ┌──────────┐   │
        │   │  THINK   │────▶│   ACT    │────▶│ OBSERVE  │   │
        │   │          │     │          │     │          │   │
        │   │ LLM reads│     │ Run code │     │ Capture  │   │
        │   │ history, │     │ or call  │     │ stdout,  │   │
        │   │ reasons, │     │ a tool;  │     │ return   │   │
        │   │ picks     │     │ produce  │     │ value,   │   │
        │   │ next step │     │ output   │     │ or error │   │
        │   └──────────┘     └──────────┘     └──────────┘   │
        │         ▲                                  │        │
        │         └──────────── repeat ──────────────┘        │
        │                                                      │
        │   Stop when: the model emits a final answer          │
        │            or the harness hits max_steps             │
        └──────────────────────────────────────────────────────┘
```

**THINK** — The model receives: the system prompt (who it is, which tools exist), the task, and every previous action + observation. It does not receive your Python source for those tools. It receives their **schema**. (Module 02 is entirely about that fact.)

**ACT** — The harness parses the model output. Two common dialects:

- **Code as action:** the model writes a Python snippet; the harness executes it.
- **JSON as action:** the model emits `{"tool": "...", "arguments": {...}}`; the harness dispatches.

Same loop. Different action language. Module 03 is the comparison.

**OBSERVE** — stdout, a return value, a traceback, a search snippet. This string is the only new information the model will have on the next THINK. If your tools return novels, you will blow the context window. If they return nothing useful, the model will guess.

**STOP** — Either the model calls a designated `final_answer` (or equivalent), or `max_steps` fires. `max_steps` is a fuse, not a goal. Set it low while you are learning (6–10), higher when a task genuinely needs more hops.

Errors are not the end of the run. A good loop **feeds the traceback back** and lets the model try again. That is the whole point.

---

## 4. How smolagents implements this

smolagents keeps the surface small on purpose.

| Piece | Role |
|---|---|
| `MultiStepAgent` | The loop. You do not instantiate this directly. |
| `CodeAgent` | Loop whose actions are Python snippets in a local interpreter |
| `ToolCallingAgent` | Loop whose actions are structured tool calls |
| `Model` protocol | Anything callable as `model(messages) → response` |
| `Tool` | A function + a schema (`name`, `description`, `inputs`, `output_type`) |
| `agent.memory.steps` | The trace of one `run()` |

**CodeAgent already knows Python.** You do not need `add_base_tools=True` to compute Fibonacci. `add_base_tools=True` injects extra tools from a built-in map (today: DuckDuckGo search and `VisitWebpageTool` — and, for `ToolCallingAgent` only, a `python_interpreter` tool). For this module, leave it off so the agent cannot wander onto the web.

**`final_answer(...)`** is a real tool the agent is given automatically. When the model calls it, the loop exits and `agent.run()` returns that value.

### Models (the plug, not the product)

| Class | Backend | Use in this course |
|---|---|---|
| `InferenceClientModel` | Hugging Face [Inference Providers](https://huggingface.co/docs/inference-providers) (`router.huggingface.co`) | Default cloud path |
| `LiteLLMModel` | OpenAI, Anthropic, Ollama, 100+ others | Zero-cost Ollama path; optional paid APIs in Module 03 |
| `TransformersModel` / `MLXModel` | Weights on this machine | Optional; not required |

The retired “Inference API (serverless)” at `api-inference.huggingface.co` is gone (HTTP 410). Do not copy old blog posts that mention it.

Default Hub model in smolagents **1.26**: `Qwen/Qwen3-Next-80B-A3B-Thinking`. The February 2026 course default (`Qwen/Qwen2.5-Coder-32B-Instruct`) often **cannot tool-call** on current providers. We do not use it.

Token: a **fine-grained** Hugging Face token with **Make calls to Inference Providers**. Read scope is not enough. Free accounts get a small monthly credit, not an unlimited LLM. Ollama is the path that stays free.

`course_setup.make_model()` in the repo root reads `.env` and returns the right class. Notebooks import it so we do not paste a model id six times.

---

## 5. Your first run, unpacked

```python
from smolagents import CodeAgent
from course_setup import make_model

model = make_model()
agent = CodeAgent(tools=[], model=model, max_steps=8)
result = agent.run("What is the 15th Fibonacci number? Show your work.")
```

What happens:

1. `make_model()` builds a client. **No network call yet.**
2. `CodeAgent(...)` stores the model, an empty tool list, a `final_answer` tool, and a Python interpreter. Still no network call.
3. `agent.run(...)` starts the loop. Each THINK is an LLM call. Each ACT is local Python. You will see those steps stream to the notebook.
4. The return value of `run()` is whatever was passed to `final_answer`.

Watch the stream. The fastest way to learn agents is to read THINK / ACT / OBSERVE live, not to wait for the number 610.

---

## 6. Reading `agent.memory.steps`

After a run, the trace lives on the agent until the next `run()` (which **resets** memory by default).

| Type | When | What to look at |
|---|---|---|
| `TaskStep` | First | `.task` — the original request |
| `PlanningStep` | Optional | `.plan` — only if you enabled planning |
| `ActionStep` | Each hop | `.tool_calls`, `.observations`, `.error` |
| `FinalAnswerStep` | Last | the value that `run()` returned |

On an `ActionStep`:

- `.model_input_messages` — the prompt the model actually saw (debugging gold)
- `.tool_calls` — the code or tool call it chose
- `.observations` — what the harness fed back
- `.error` — a caught exception, if any

Keep memory across two user turns with `reset=False`:

```python
agent.run("Remember that number.", reset=False)
```

Use this sparingly. Long memories are expensive and confusing. Most production systems treat each `run()` as a fresh task and store durable state **outside** the agent (a database, a file, a session object).

---

## 7. Safety (read this once, take it seriously)

`CodeAgent` executes model-written Python **on your machine**, in a restricted interpreter (import allow-list, time limit). Restricted is not the same as safe.

- Do not point a CodeAgent at untrusted tools that fetch and `eval` the internet.
- Do not run a CodeAgent with broad `additional_authorized_imports` on a laptop that has secrets in the environment.
- For anything beyond a tutorial: sandbox (Docker, E2B, Blaxel, Modal). smolagents documents these as `executor_type`. We stay on the local interpreter in this course so you can see the loop without extra accounts.

`ToolCallingAgent` has no general-purpose code execution. Its blast radius is whatever your tools do. That is why many production systems prefer it even when CodeAgent is “smarter.”

---

## 8. Exercises

Do these in the notebook. Success criteria are next to each `# TODO`.

1. **Temperature** — convert 98.6°F to Celsius and Kelvin, showing the formulae, and print how many steps it took.
2. **Median without `statistics`** — median of `[4, 7, 2, 9, 1, 5]`; then list the step types you actually got.

Stretch (optional): run a follow-up with `reset=False` that uses the previous answer. Then run the same follow-up with the default `reset=True` and notice the failure.

---

## 9. What you should be able to say out loud

- An agent is a loop around a model, not a smarter model.
- I use an agent when the path is unknown; I use a function when it is known.
- In smolagents, `CodeAgent` acts by writing Python; `memory.steps` is the trace.
- `add_base_tools=True` is not why Fibonacci works.
- Hugging Face Inference Providers are metered. Ollama is the free fallback.

**Next — Module 02.** The model never sees your tool’s source code. It sees a schema. You will write that schema on purpose.

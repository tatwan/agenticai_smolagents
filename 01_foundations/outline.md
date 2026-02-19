# Module 01: Foundations — Building Your First Agent
## Course Outline

---

## 1. What Is an AI Agent?

An AI agent is more than a chatbot. A chatbot responds to a single prompt and stops. An agent operates in a loop: it reasons about a task, takes an action (running code, calling a tool, searching the web), observes the result of that action, and then reasons again — repeating until it produces a final answer or exhausts its step budget.

### The Agent Loop

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
        │   Loop exits when: final_answer() is called          │
        │                 or max_steps is reached              │
        └──────────────────────────────────────────────────────┘
```

Key properties:
- The agent sees its full history on every THINK step — this is how it maintains context across multiple actions.
- Actions in smolagents are either code blocks (CodeAgent) or structured tool calls (ToolCallingAgent).
- The loop is managed entirely by the framework; you define the task and tools.

---

## 2. smolagents Architecture Overview

smolagents is built around a small number of composable abstractions.

### 2.1 MultiStepAgent (base class)

`MultiStepAgent` is the abstract base that implements the agent loop. It handles:
- Maintaining `memory` (a `AgentMemory` object holding all steps)
- Calling the LLM on each iteration
- Parsing the LLM output into a concrete action
- Executing the action and storing the result
- Checking termination conditions

You do not use `MultiStepAgent` directly. You subclass it or use one of the two provided concrete agents.

### 2.2 CodeAgent

`CodeAgent` extends `MultiStepAgent`. On each THINK step the LLM writes a Python code block. The agent executes that code in a sandboxed local interpreter and feeds stdout/return value back as the observation.

Strengths:
- Naturally expressive — the LLM can write loops, list comprehensions, intermediate print statements
- Handles numerical/data tasks very well
- `add_base_tools=True` gives it a Python interpreter, web search, and a few utilities out of the box

### 2.3 ToolCallingAgent

`ToolCallingAgent` extends `MultiStepAgent`. Instead of writing code, the LLM emits a structured JSON tool call. The framework looks up the tool, calls it with the provided arguments, and returns the result.

Strengths:
- More constrained — the LLM can only call tools you have explicitly registered
- Easier to audit and restrict
- Better for production pipelines where you want predictable action space

### 2.4 How Models Plug In

smolagents uses a thin `Model` protocol. Any object that implements `__call__(messages, ...) -> str` can be used as the model. Built-in adapters include:

| Class | Backend |
|---|---|
| `InferenceClientModel` | HuggingFace Inference API (free tier or dedicated) |
| `LiteLLMModel` | 100+ providers via LiteLLM (OpenAI, Anthropic, Gemini, …) |
| `TransformersModel` | Local weights via `transformers` |
| `MLXModel` | Local weights via Apple MLX (Apple Silicon) |

The agent does not care which model class you use — it just calls `model(messages)`.

---

## 3. InferenceClientModel — HuggingFace Free Tier Setup

### 3.1 Getting Your Token

1. Create a free account at https://huggingface.co
2. Navigate to Settings → Access Tokens
3. Create a new token with **Read** scope (sufficient for Inference API calls)
4. Copy the token — it starts with `hf_`

### 3.2 Storing the Token

Store the token in a `.env` file at the project root (never commit this file):

```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

Load it in your notebook or script with:

```python
from dotenv import load_dotenv
load_dotenv()
import os
token = os.environ["HF_TOKEN"]
```

### 3.3 Model Selection

The HuggingFace free Inference API supports several models. For this course we use:

| Model | Notes |
|---|---|
| `Qwen/Qwen2.5-Coder-32B-Instruct` | Strong coder, available via Together/Sambanova providers; recommended default |
| `meta-llama/Llama-3.3-70B-Instruct` | General reasoning; may hit rate limits on free tier |
| `Qwen/Qwen2.5-72B-Instruct` | Larger general model |

### 3.4 Initialization

```python
from smolagents import InferenceClientModel

model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

Optional parameters:
- `provider` — force a specific inference provider (e.g., `"together"`, `"sambanova"`)
- `max_tokens` — cap on generated tokens per step (default 2048)
- `temperature` — sampling temperature (default 0.5)

---

## 4. Your First CodeAgent — Minimal Working Example Walkthrough

```python
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)

agent = CodeAgent(tools=[], model=model, add_base_tools=True)

result = agent.run("What is the 15th Fibonacci number? Show your work.")
print("Final answer:", result)
```

Step-by-step walkthrough:

1. `InferenceClientModel(...)` — creates a model object pointing at the HF Inference API. No network call is made yet.
2. `CodeAgent(tools=[], model=model, add_base_tools=True)` — constructs the agent.
   - `tools=[]` — no custom tools for now.
   - `add_base_tools=True` — adds the built-in Python interpreter tool and a few utilities.
3. `agent.run("...")` — triggers the agent loop.
   - The agent sees the task, reasons about it, writes Python code, executes it, observes the output, and when satisfied calls `final_answer()`.
   - The return value of `agent.run()` is the argument passed to `final_answer()`.
4. `print(result)` — prints what the agent decided was the answer.

During `agent.run()` you will see real-time output showing each THINK → ACT → OBSERVE iteration.

---

## 5. Inspecting Agent Steps — memory.steps

After `agent.run()` completes, every step is persisted in `agent.memory.steps`.

```python
print(f"Total steps: {len(agent.memory.steps)}")
for i, step in enumerate(agent.memory.steps):
    print(f"Step {i}: {type(step).__name__}")
    print(str(step)[:300])
    print("---")
```

### Step Types

| Type | When it appears | Key attributes |
|---|---|---|
| `TaskStep` | First step — records the original task | `.task` |
| `PlanningStep` | When agent produces a high-level plan (optional) | `.plan` |
| `ActionStep` | Each THINK → ACT → OBSERVE iteration | `.model_input_messages`, `.tool_calls`, `.observations`, `.error` |
| `FinalAnswerStep` | Last step — records the final answer | (implicit in last ActionStep) |

### What to look for

- `step.model_input_messages` — the full prompt sent to the LLM on that iteration (useful for prompt debugging)
- `step.tool_calls` — the code the LLM chose to run
- `step.observations` — what the code printed or returned
- `step.error` — any Python exception that was caught and fed back to the LLM

The memory is reset on each `agent.run()` call by default. To preserve it across runs, pass `reset=False`:

```python
agent.run("Follow-up task", reset=False)
```

---

## 6. Exercises

### Exercise 1 — Temperature Conversion Agent

Students create a fresh `CodeAgent` and ask it to convert 98.6°F to both Celsius and Kelvin, requiring it to show the formula. After the run, students print both the final result and the total number of steps taken. This reinforces agent initialization and accessing `agent.memory.steps`.

### Exercise 2 — Median Without the statistics Library

Students ask the agent to find the median of `[4, 7, 2, 9, 1, 5]` without importing `statistics`, and to show each step of reasoning. After the run, students inspect `agent.memory.steps` and identify which step types appeared. This reinforces step inspection and shows how the agent handles a constraint in the prompt.

---

## 7. Summary and What's Next

### What You Learned

- The agent loop (Think → Act → Observe) is the core primitive of all agent frameworks, not just smolagents.
- `CodeAgent` uses LLM-generated Python code as its action space, giving it flexible problem-solving ability.
- `InferenceClientModel` connects any HuggingFace-hosted model to the agent with just a token and a model ID.
- `agent.memory.steps` gives you full visibility into every reasoning step — essential for debugging.

### What's Next — Module 02: Tools and Custom Tools

The built-in base tools cover common tasks but real-world agents need domain-specific capabilities. In Module 02 you will learn:
- The `@tool` decorator — turning any Python function into an agent tool in three lines
- Tool docstrings — how the LLM discovers what a tool does and what arguments it takes
- Building tools that call external APIs, read files, or perform domain calculations
- Registering custom tools with `CodeAgent` and `ToolCallingAgent`
- Tool safety — what the agent can and cannot do with your tools

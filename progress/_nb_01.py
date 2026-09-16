from pathlib import Path

from _write_nb import ROOT, write

cells = [
    (
        "md",
        """# Module 01: Foundations — Building Your First Agent

This notebook is the **lab**. The lesson (what / when / how, including ideas that apply outside smolagents) is [`outline.md`](outline.md). Keep it open.

You will:

1. Smoke-test a model (Hugging Face or Ollama)
2. Run a `CodeAgent` on a tiny task so you can **see the loop**
3. Read `agent.memory.steps` — the trace you will use for the rest of the course
4. Do two short exercises

If something fails, [`instructions.md`](instructions.md) has the error table.

---

## What is an agent?

A chatbot is one call: prompt in, text out. An **agent** is a loop around a model:

```
task → THINK (model) → ACT (code or tool) → OBSERVE (result or error) → THINK → … → stop
```

The model is still only generating tokens. The harness parses those tokens into an action, executes it, and feeds the result back. That loop is the same idea in smolagents, LangGraph, a `while` loop you write yourself, or a production orchestrator.

**When to use it:** the path is unknown — you cannot hard-code the steps. **When not to:** a single completion, a parser, or ten lines of Python would do. Fibonacci does not *need* an agent; we use it so the loop is visible.
""",
    ),
    (
        "md",
        """## Setup

**Local (canonical):** this cell imports `course_setup.py` from the repo root. Your `.env` must live next to `pyproject.toml`.

**Colab:** run the two *Colab only* cells first (install + secrets), then this one. The fallback path uses `HF_TOKEN` from the environment.
""",
    ),
    (
        "code",
        r"""# Colab only — skip this cell locally.
# !pip install -q "smolagents[toolkit,litellm]" python-dotenv pandas requests markdownify huggingface-hub
""",
    ),
    (
        "code",
        r"""# Colab only — skip this cell locally.
# In Colab: Secrets (key icon) → add HF_TOKEN with "Make calls to Inference Providers".
# import os
# from google.colab import userdata
# os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")
""",
    ),
    (
        "code",
        r"""import os
import sys
from pathlib import Path

def _repo_root() -> Path | None:
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "course_setup.py").exists():
            return candidate
    return None

ROOT = _repo_root()
if ROOT is not None:
    sys.path.insert(0, str(ROOT))
    from course_setup import make_model, print_setup, smoke_test

    model = make_model()
    print_setup(model)
    smoke_test(model)
else:
    from dotenv import load_dotenv
    from smolagents import InferenceClientModel

    load_dotenv()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "course_setup.py was not found and HF_TOKEN is unset. "
            "Local: start Jupyter from the cloned repo (`uv run jupyter lab`). "
            "Colab: run the secrets cell, then re-run this cell."
        )
    model = InferenceClientModel(
        model_id=os.environ.get("COURSE_MODEL_ID", "Qwen/Qwen3-Next-80B-A3B-Thinking"),
        token=token,
    )
    print("Model initialized:", model.model_id)
""",
    ),
    (
        "md",
        """## How smolagents pieces fit

| Piece | Job |
|---|---|
| `InferenceClientModel` / `LiteLLMModel` | Talk to an LLM. The agent does not care which. |
| `CodeAgent` | Loop whose **actions are Python**. Built-in interpreter; no web unless you add it. |
| `ToolCallingAgent` | Loop whose **actions are JSON tool calls**. Module 03. |
| `agent.run(task)` | Start the loop. Returns the `final_answer(...)` value. |
| `agent.memory.steps` | Trace of that run. |

`CodeAgent` can already run Python. **`add_base_tools=True` is not why Fibonacci works.** That flag injects extra tools (search, visit-webpage). Leave it off here so the agent cannot wander onto the web.

`max_steps` is a fuse. Default is 20. We use 8 so a confused model dies cheaply.
""",
    ),
    (
        "md",
        """## Your first agent

Watch the stream. You should see the model write Python, the interpreter print a number, then a `final_answer`. The 15th Fibonacci number is **610** (counting F(1)=1, F(2)=1, …). If you get a different indexing convention, read the trace — the loop still worked.
""",
    ),
    (
        "code",
        r"""from smolagents import CodeAgent

agent = CodeAgent(tools=[], model=model, max_steps=8)

result = agent.run("What is the 15th Fibonacci number? Show your work. Use F(1)=1, F(2)=1.")
print("\nFinal answer:", result)
""",
    ),
    (
        "md",
        """## Inspect the trace

Every hop is stored until the next `run()` (which **resets** memory by default).

| Type | When | Useful fields |
|---|---|---|
| `TaskStep` | First | `.task` |
| `PlanningStep` | Only if planning is on | `.plan` |
| `ActionStep` | Each Think → Act → Observe | `.tool_calls`, `.observations`, `.error` |
| `FinalAnswerStep` | Last | the value `run()` returned |

This table is the same idea as a trace UI in LangSmith, Phoenix, or MLflow (Module 06): **you cannot improve a loop you cannot see.**
""",
    ),
    (
        "code",
        r"""print(f"Total steps: {len(agent.memory.steps)}\n")
for i, step in enumerate(agent.memory.steps):
    print(f"Step {i}: {type(step).__name__}")
    print(str(step)[:400])
    print("---")
""",
    ),
    (
        "code",
        r"""from smolagents.memory import ActionStep

action_steps = [s for s in agent.memory.steps if isinstance(s, ActionStep)]
if not action_steps:
    print("No ActionStep — the run may have failed before the first act.")
else:
    step = action_steps[0]
    print("tool_calls:", step.tool_calls)
    print("observations:", str(step.observations)[:500])
    print("error:", step.error)
""",
    ),
    (
        "md",
        """## Memory across turns (`reset=False`)

By default each `run()` starts a blank slate. Pass `reset=False` to keep the previous trace in context (a short chat). Production systems usually keep durable state **outside** the agent; this flag is a demo, not a memory architecture.
""",
    ),
    (
        "code",
        r"""follow = agent.run(
    "What number did you just compute? Add 5 to it.",
    reset=False,
)
print("Follow-up with memory:", follow)

fresh = CodeAgent(tools=[], model=model, max_steps=8)
amnesiac = fresh.run("What number did you just compute? Add 5 to it.")
print("Same question, new agent:", amnesiac)
""",
    ),
    (
        "md",
        """## Safety (one cell, then we move on)

`CodeAgent` runs model-written Python **on this machine**, inside a restricted interpreter (import allow-list + time limit). Restricted ≠ sandboxed.

- Do not add `additional_authorized_imports` that let the model talk to your filesystem or network unless you intend that.
- For anything beyond a tutorial, use a real sandbox (`executor_type` in the [secure code execution guide](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution)).
- `ToolCallingAgent` (Module 03) has no general-purpose interpreter. Its blast radius is your tools.
""",
    ),
    (
        "md",
        """## Guided example: more than one hop

A slightly richer task. You should see multiple `ActionStep`s: build a list, then reduce it. If your local model is tiny, it may burn `max_steps` — that is useful data, not a failed lesson. Read the last step’s `.error`.
""",
    ),
    (
        "code",
        r"""agent = CodeAgent(tools=[], model=model, max_steps=10)
result = agent.run(
    "Create a list of the first 10 prime numbers, then calculate their sum and average. "
    "Return both numbers."
)
print("\nFinal answer:", result)
print("Steps used:", len(agent.memory.steps))
print("Step types:", [type(s).__name__ for s in agent.memory.steps])
""",
    ),
    (
        "md",
        """## Exercises

Write these from scratch. Do not copy the guided cells blindly.

Each cell has **You succeeded if…** under the TODO.
""",
    ),
    (
        "code",
        r"""# TODO Exercise 1: Temperature conversion
# Create a fresh CodeAgent (same `model`, tools=[], max_steps=8).
# Ask it to convert 98.6°F to Celsius AND Kelvin, and to show the formulae.
# Print the result and the number of steps.
#
# You succeeded if:
#   - agent.run() returns without raising
#   - the result mentions both Celsius (~37) and Kelvin (~310)
#   - you printed len(agent.memory.steps) and it is >= 2 (Task + at least one action)

# Your code here:
""",
    ),
    (
        "code",
        r"""# TODO Exercise 2: Median without the statistics library
# Ask a CodeAgent for the median of [4, 7, 2, 9, 1, 5] without importing statistics.
# Then print every step type you actually got.
#
# You succeeded if:
#   - the numeric median is 4.5 (sorted: 1,2,4,5,7,9 — average of the two middle values)
#   - your printed types include TaskStep and FinalAnswerStep (names may differ slightly by version)
#   - you did not import statistics in *your* notebook cell (the agent must not either)

# Your code here:
""",
    ),
    (
        "md",
        """## Hints (stay out until you have tried)

<details>
<summary>Exercise 1</summary>

```python
agent = CodeAgent(tools=[], model=model, max_steps=8)
result = agent.run(
    "Convert 98.6°F to Celsius and Kelvin. Show the formulae you used."
)
print(result)
print("steps:", len(agent.memory.steps))
```

</details>

<details>
<summary>Exercise 2</summary>

Median of an even-length list is the average of the two central values after sorting. Prompt the agent with that constraint if it tries to import `statistics`.

```python
print([type(s).__name__ for s in agent.memory.steps])
```

</details>
""",
    ),
    (
        "md",
        """## What you built

- A working picture of the agent loop that does not depend on smolagents
- A model client (`InferenceClientModel` or `LiteLLMModel`) behind one helper
- A `CodeAgent` that acts by writing Python
- A habit: after every run, read `memory.steps`

**Key insight:** the model only thinks. The harness acts. The trace is how you tell those apart.

---

## Next — Module 02: Tools & custom tools

Right now the agent’s only action is Python. Real agents need **domain tools** (APIs, files, calculators). The LLM never sees the tool’s source — only a schema. That sentence is the whole next module.
""",
    ),
]

write(ROOT / "01_foundations" / "notebook.ipynb", cells)

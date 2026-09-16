from _write_nb import ROOT, SETUP_CODE, SETUP_COLAB_INSTALL, SETUP_COLAB_SECRETS, SETUP_MD, write

cells = [
    (
        "md",
        """# Module 03: CodeAgent vs ToolCallingAgent

This notebook is the **lab**. The lesson is [`outline.md`](outline.md).

The loop is the same. The **action language** is not:

| | `CodeAgent` | `ToolCallingAgent` |
|---|---|---|
| Model writes | Python | JSON tool call |
| Between tools | Full computation | Text only (or another tool) |
| Needs native tool calling | No | **Yes** |
| Blast radius | Interpreter | Your tools |

We give **both** the same `word_count` tool and the same task, then read the traces. That comparison is the module.

Errors: [`instructions.md`](instructions.md).
""",
    ),
    ("md", SETUP_MD),
    ("code", SETUP_COLAB_INSTALL),
    ("code", SETUP_COLAB_SECRETS),
    ("code", SETUP_CODE),
    (
        "md",
        """## One tool, used twice
""",
    ),
    (
        "code",
        r'''from smolagents import CodeAgent, ToolCallingAgent, tool

@tool
def word_count(text: str) -> int:
    """Count whitespace-separated words in text.

    Args:
        text: The sentence or paragraph to count.
    """
    return len(text.split())

print(word_count.name, word_count.inputs)
print("direct:", word_count("The quick brown fox jumps over the lazy dog"))
''',
    ),
    (
        "md",
        """## Same task, CodeAgent

Watch for a Python snippet that may call `word_count` *and* do extra math.
""",
    ),
    (
        "code",
        r'''TASK = (
    "How many words are in 'The quick brown fox jumps over the lazy dog'? "
    "Then double that number and return the doubled value."
)

code_agent = CodeAgent(tools=[word_count], model=model, max_steps=8)
code_result = code_agent.run(TASK)
print("CodeAgent result:", code_result)
print("steps:", [type(s).__name__ for s in code_agent.memory.steps])
''',
    ),
    (
        "md",
        """## Same task, ToolCallingAgent

If this cell errors or never calls the tool, your model likely **cannot tool-call**. That is a real 2026 failure mode (it is why the library dropped Qwen2.5-Coder-32B as default). Write what you observed in the comparison cell; do not fake a JSON trace.
""",
    ),
    (
        "code",
        r'''json_error = None
json_result = None
json_agent = ToolCallingAgent(tools=[word_count], model=model, max_steps=8)
try:
    json_result = json_agent.run(TASK)
    print("ToolCallingAgent result:", json_result)
    print("steps:", [type(s).__name__ for s in json_agent.memory.steps])
except Exception as exc:
    json_error = exc
    print("ToolCallingAgent failed:", type(exc).__name__, exc)
    print("Use a tool-calling Hub model, or treat this as the 'model cannot tool-call' case.")
''',
    ),
    (
        "md",
        """## Compare traces

Look at *shape*, not poetry: did one write Python? Did one emit a structured call? Who doubled the number, the interpreter or the final sentence?
""",
    ),
    (
        "code",
        r'''def show_trace(label, agent):
    print(f"\n===== {label} =====")
    if agent is None:
        print("(no agent)")
        return
    for i, step in enumerate(agent.memory.steps):
        print(f"{i} {type(step).__name__}")
        calls = getattr(step, "tool_calls", None)
        if calls:
            print("  tool_calls:", calls)
        obs = getattr(step, "observations", None)
        if obs:
            print("  observations:", str(obs)[:240])

show_trace("CodeAgent", code_agent)
show_trace("ToolCallingAgent", json_agent if json_error is None else None)

print("\nExpected word count of that sentence: 9; doubled: 18")
''',
    ),
    (
        "md",
        """## Decision framework (keep this)

- **Computation between tools / unknown path / no tool-calling model** → `CodeAgent`
- **Dispatch, audit log, no general interpreter, model supports tools** → `ToolCallingAgent`

They are not “beginner vs production.” They are different bets.
""",
    ),
    (
        "md",
        """## Optional: swap the model, not the agent

Uncomment **one** block if you have that backend. Agent code stays the same.

Example ids change — check current docs before copying them into production.
""",
    ),
    (
        "code",
        r'''# ── OPTIONAL. Skip unless you have the matching key / server. ──
# from smolagents import LiteLLMModel, OpenAIModel
# import os
#
# OpenAI-compatible:
# alt = LiteLLMModel(model_id="gpt-4.1-mini", api_key=os.environ["OPENAI_API_KEY"])
#
# Anthropic via LiteLLM:
# alt = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5", api_key=os.environ["ANTHROPIC_API_KEY"])
#
# Already on Ollama? You are using LiteLLMModel through course_setup.
# OpenAIModel is the native OpenAI-compatible client (alias: OpenAIServerModel).
#
# CodeAgent(tools=[word_count], model=alt).run(TASK)
print("Optional model-swap cell skipped (as designed).")
''',
    ),
    (
        "md",
        """## Safety reminder

This `CodeAgent` runs on the **local** interpreter. For untrusted tasks, use a sandbox (`executor_type` in the [secure code execution guide](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution)). `ToolCallingAgent` has no general-purpose exec; its policy *is* your tool list.
""",
    ),
    (
        "md",
        """## Exercises
""",
    ),
    (
        "code",
        r'''# TODO Exercise 1: count_vowels on BOTH agent types
# @tool count_vowels(text: str) -> int  (a,e,i,o,u case-insensitive)
# Task: "Count the vowels in: 'HuggingFace builds amazing open source tools'"
# Run CodeAgent and ToolCallingAgent. Print both results and both step-type lists.
#
# You succeeded if:
#   - a direct call returns 16 (count them: u,i,a,e,u,i,a,a,i,o,e,o,u,e,o,o)
#   - you printed two traces (or a documented ToolCallingAgent failure)
#   - both successful runs agree on the integer, even if step counts differ

# Your code here:
''',
    ),
    (
        "code",
        r'''# TODO Exercise 2: a loop-shaped task
# Task: "For each word in ['python', 'data', 'engineer', 'agent'], count its
# letters and return the word with the most letters."
# Run ToolCallingAgent FIRST, then CodeAgent. Write 2–3 sentences:
# which type is a better fit, and what in the traces made you say that?
#
# You succeeded if:
#   - CodeAgent returns "engineer" (8 letters)
#   - you have a written comparison, not just two printed results
#   - if ToolCallingAgent struggles, you explain it using the decision framework

# Your code here:
''',
    ),
    (
        "md",
        '''## Hints

<details>
<summary>Vowel count</summary>

```python
@tool
def count_vowels(text: str) -> int:
    """Count vowels a,e,i,o,u in text, case-insensitive.

    Args:
        text: Any string.
    """
    return sum(ch.lower() in "aeiou" for ch in text)
```

</details>

<details>
<summary>Why CodeAgent wins the loop task</summary>

The JSON agent must call a letter-count tool once per word *or* cram the loop into one tool. The code agent writes a `for` loop in one hop. That is the architecture, not a scoring bug.

</details>
''',
    ),
    (
        "md",
        """## What you built

- A side-by-side of two action languages on one contract (the tool schema)
- A decision rule you can reuse in LangGraph, raw APIs, or smolagents
- A plan for “this model cannot tool-call”

**Key insight:** swapping `CodeAgent` for `ToolCallingAgent` is a one-line change in the constructor and a large change in what the model is allowed to *do*.

---

## Next — Module 04: Web search & browsing

Closed weights cannot answer “what shipped this week.” You will search, pick a URL, visit the page, and extract with citations.
""",
    ),
]

write(ROOT / "03_codeagent_vs_toolcalling" / "notebook.ipynb", cells)

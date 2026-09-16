# Module 01: Foundations — how to run this lab

**Module:** 01 of 06  
**Read first:** [`outline.md`](outline.md) (the lesson)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

By the end of this module you can:

- Explain the agent loop (Think → Act → Observe) in words that do not mention smolagents
- Say when an agent is the wrong tool
- Initialize a model via `course_setup.make_model()` (Hugging Face **or** Ollama)
- Run a `CodeAgent` and read `agent.memory.steps`
- Recognize `TaskStep`, `ActionStep`, and `FinalAnswerStep`

---

## Prerequisites

- Course environment from the root [README](../README.md): `uv sync` already succeeded
- A model backend:
  - **Cloud:** `.env` at the **repo root** (same folder as `pyproject.toml`) with `HF_TOKEN=...` — fine-grained token, permission **Make calls to Inference Providers**
  - **Local:** Ollama running, `COURSE_MODEL_BACKEND=ollama` in `.env`
- You can read Python functions and `print`

There is no “Module 00.” Setup lives in the README.

---

## Estimated time

60–90 minutes, including the first-time token / Ollama setup. Exploring traces can push this toward two hours; that time is well spent.

---

## How to run

From the **repository root** (the folder that contains `pyproject.toml`):

```bash
uv run jupyter lab 01_foundations/notebook.ipynb
```

If Jupyter cannot import `smolagents`, the notebook is not using this project’s kernel. Either start Jupyter with `uv run jupyter lab` as above, or pick the `Python (smolagents-course)` kernel after:

```bash
uv run python -m ipykernel install --user --name smolagents-course --display-name "Python (smolagents-course)"
```

Run cells top to bottom with **Shift + Enter**. Do not skip the smoke-test cell.

---

## Common errors

### 1. `KeyError: 'HF_TOKEN'` or `HF_TOKEN is not set`

The process never saw your token.

1. `.env` must sit next to `pyproject.toml`, not inside `01_foundations/`.
2. Line shape: `HF_TOKEN=hf_...` with no spaces around `=`.
3. Restart the kernel after creating or editing `.env`.
4. Or switch to Ollama: `COURSE_MODEL_BACKEND=ollama` (see `.env.example`).

### 2. `401` / `403` / “this authentication method does not have sufficient permissions”

You used a **Read** token, or a fine-grained token without **Make calls to Inference Providers**.

Create a new fine-grained token at https://huggingface.co/settings/tokens, enable that permission, replace `HF_TOKEN`, restart the kernel.

### 3. `429` / payment / “exceeded monthly credits”

Hugging Face free Inference Providers credit is small (on the order of $0.10 / month). This is expected.

- Wait if it is a per-minute limit.
- Set `COURSE_MODEL_BACKEND=ollama` and pull `qwen2.5-coder:7b`.
- Optionally force a provider: `COURSE_HF_PROVIDER=together` (or `novita`, `sambanova`, …).

### 4. Empty smoke test / connection refused to `11434`

Ollama is not running, or the model is not pulled.

```bash
ollama serve          # if it is not already a background service
ollama pull qwen2.5-coder:7b
```

### 5. `ModuleNotFoundError: smolagents` / `course_setup`

You started Jupyter from a different environment, or opened the notebook in Colab without running the install cell. Local: always `uv run jupyter lab` from the repo root. Colab: run the commented install + secrets cells at the top.

### 6. Agent tries to search the web for Fibonacci

You passed `add_base_tools=True`. For this module, use `CodeAgent(tools=[], model=model)` so the only action is Python. Search is Module 04.

### 7. `AttributeError: 'CodeAgent' object has no attribute 'memory'`

Your smolagents is older than 1.0. This course pins `>=1.26,<2`. From the repo root: `uv sync`, then restart the kernel.

### 8. The answer is wrong but there is no exception

Open `agent.memory.steps` and read the last `ActionStep`. Look at `.error` and `.observations`. Wrong answers with a clean trace are a **model** problem (weak local model, or a thinking model that burned `max_steps`). Raise `max_steps` slightly or switch models. Do not add tools yet.

---

## Tips

- Read the outline’s “when not to use an agent” before you start worshipping the loop.
- The live stream during `agent.run()` is the lesson. Do not skip it.
- Print `type(step).__name__` before you print `str(step)`. Orientation first, detail second.
- Exercises: write them from the patterns above, then use the hint cell at the bottom if you stall.
- After a failed run, `agent.memory.steps[-1]` is the first debugger you need. Later modules will still use it.

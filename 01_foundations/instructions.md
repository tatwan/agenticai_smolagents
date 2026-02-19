# Module 01: Foundations — Building Your First Agent

## Module Overview

**Module number:** 01 of 06
**Topic:** Foundations — the agent loop, smolagents architecture, and your first CodeAgent

---

## Learning Objectives

By the end of this module you will be able to:

- Explain the agent loop (Think → Act → Observe) and how it differs from a simple LLM chat call
- Initialize an `InferenceClientModel` using a free HuggingFace token and select a suitable model
- Create and run a `CodeAgent` against a real reasoning task
- Inspect `agent.memory.steps` to read each step type and understand what the agent did at each iteration

---

## Prerequisites

Before starting this module, ensure the following are in place:

- **Python 3.10 or higher** installed on your machine
- **Course environment set up:** you have run `uv sync` from the project root and all dependencies are installed
- **`.env` file configured:** the file exists at the project root and contains your HuggingFace token:
  ```
  HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
  ```
  If you do not have a token yet, create one at https://huggingface.co/settings/tokens (Read scope is sufficient).
- **Familiarity with Python** at a basic level — you can read and write functions, loops, and use the `print()` statement

---

## Estimated Time

45 to 60 minutes

This includes reading the concept cells, running all code cells, and completing both exercises. If you spend time exploring the step output in detail or experimenting beyond the exercises, plan for up to 90 minutes.

---

## How to Run

Open a terminal, navigate to the project root (the directory containing `pyproject.toml`), and launch JupyterLab pointing at this module's notebook:

```bash
cd /path/to/smolagents
uv run jupyter lab 01_foundations/notebook.ipynb
```

Replace `/path/to/smolagents` with the actual path on your machine — for example:

```bash
cd /Users/yourname/Repos/agentic_ai/smolagents
uv run jupyter lab 01_foundations/notebook.ipynb
```

JupyterLab will open in your browser. Run cells top to bottom using **Shift + Enter**. Do not skip cells — each one builds on the previous state.

---

## Common Errors and Fixes

### 1. `KeyError: 'HF_TOKEN'` or `HF_TOKEN not set`

**What it means:** The environment variable `HF_TOKEN` was not found. Either the `.env` file does not exist, it is in the wrong directory, or the key name is misspelled.

**How to fix:**
1. Confirm the `.env` file exists at the **project root** (the same directory as `pyproject.toml`), not inside `01_foundations/`.
2. Open the file and verify the line reads exactly `HF_TOKEN=hf_...` with no spaces around the `=`.
3. Confirm `load_dotenv()` is called before `os.environ["HF_TOKEN"]` in the setup cell.
4. If you just created or edited the `.env` file, restart the Jupyter kernel (Kernel → Restart Kernel) and rerun all cells.

### 2. Rate limit errors or `429 Too Many Requests`

**What it means:** The HuggingFace free Inference API has per-minute and per-day request limits. You have exceeded them.

**How to fix:**
- Wait 60 seconds and retry — the per-minute limit resets quickly.
- Switch to a model that routes through providers with more generous free limits. The most reliable free-tier options are:

  | Model ID | Notes |
  |---|---|
  | `Qwen/Qwen2.5-Coder-32B-Instruct` | Routes through Together/Sambanova; recommended default |
  | `Qwen/Qwen2.5-72B-Instruct` | Alternative general model on similar providers |

  To switch models, change the `model_id` in the setup cell and rerun from that cell downward.
- If you hit persistent limits, add `provider="together"` or `provider="sambanova"` explicitly to the `InferenceClientModel` constructor to force a specific provider endpoint.

### 3. `AttributeError: 'CodeAgent' object has no attribute 'memory'`

**What it means:** You are running an older version of smolagents. The `memory` attribute was introduced in smolagents 1.0.0.

**How to fix:**
1. Check your installed version:
   ```bash
   uv run python -c "import smolagents; print(smolagents.__version__)"
   ```
2. If the version is below `1.0.0`, update the lock file and reinstall:
   ```bash
   uv sync --upgrade
   ```
3. Restart the Jupyter kernel and rerun all cells from the top.

---

## Tips for Getting the Most Out of This Module

**Read the concept cells carefully.** The code cells are short on purpose — the reasoning is in the markdown. Understanding the agent loop conceptually before running code will make the output much easier to interpret.

**Watch the live output during `agent.run()`.** smolagents streams each step to stdout as it happens. Read through the THINK, ACT, and OBSERVE blocks in real time — this is the fastest way to build intuition for what the agent is doing.

**Don't skip the step inspection cell.** The most common beginner mistake is treating `agent.run()` as a black box. Printing `agent.memory.steps` and reading through the step types is the foundation of all agent debugging you will do in later modules.

**For the exercises, resist the urge to look at the guided examples above them.** Write the code from scratch using only the patterns you learned. If you get stuck, look at the setup cell and the first agent run cell — you have everything you need.

**Experiment beyond the exercises.** Once you have completed the two exercises, try changing the task in `agent.run()` to something you are curious about. Longer or more open-ended tasks will show you more interesting multi-step behavior in the memory.

**If the agent fails or loops:** Check `agent.memory.steps[-1]` to see the last step. The `.error` attribute on `ActionStep` objects will show you the Python exception the agent encountered. Often the model self-corrects — but if it loops, reduce `max_steps` (default is 20) to cut it off earlier during experimentation.

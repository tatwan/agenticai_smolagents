# Building AI Agents with smolagents

![Gemini_Generated_Image_wiu8prwiu8prwiu8](images/Gemini_Generated_Image_wiu8prwiu8prwiu8.png)

A practical, code-heavy mini-course for data engineers and ML practitioners.

---

## Overview

This is a 6-module, hands-on mini-course for building AI agents using Hugging Face's [smolagents](https://github.com/huggingface/smolagents) library. It targets intermediate-to-advanced practitioners who are comfortable with Python and have basic familiarity with language models. Every module uses open-source tools and free-tier APIs — no paid subscriptions required to complete the core curriculum. The modules follow a linear progression, where each one builds directly on concepts and code introduced in the previous module.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | |
| uv (package manager) | Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| HuggingFace account | Free at huggingface.co — needed for `HF_TOKEN` |
| Basic Python proficiency | Comfortable with functions, classes, imports |
| Basic ML familiarity | Know what a language model is |

---

## Quick Start

1. Clone or download this repository
2. `cd smolagents`
3. `uv sync` — installs all dependencies
4. `cp .env.example .env` — then edit `.env` and add your `HF_TOKEN`
5. `uv run jupyter lab` — opens Jupyter in your browser
6. Start with `01_foundations/notebook.ipynb`

> **Get your HF_TOKEN at https://huggingface.co/settings/tokens** — free account, read access is sufficient.

---

## Quick Start (Colab) <a name="quick-start-colab"></a>

1. Click any **Open in Colab** badge in the Module Map below
2. In Colab, go to **Secrets** (🔑 icon in the left sidebar) → **Add a new secret**
   - Name: `HF_TOKEN` · Value: your HuggingFace token
3. In the notebook, uncomment the **installation cell** (first code cell) and run it:
   ```python
   !uv pip install smolagents python-dotenv duckduckgo-search mlflow
   ```
4. Uncomment the **Colab Secrets block** in the `## Setup` cell and run it:
   ```python
   from google.colab import userdata
   os.environ['HF_TOKEN'] = userdata.get('HF_TOKEN')
   ```
5. Run all remaining cells in order

---



## Module Map

| Module | Topic | Key Tools | Open in Colab |
|---|---|---|---|
| 01 | Foundations: The Agent Loop | `CodeAgent`, `InferenceClientModel` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/01_foundations/notebook.ipynb) |
| 02 | Tools & Custom Tools | `@tool`, `Tool` subclass | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/02_tools_and_custom_tools/notebook.ipynb) |
| 03 | CodeAgent vs ToolCallingAgent | Both agent types, `LiteLLMModel` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/03_codeagent_vs_toolcalling/notebook.ipynb) |
| 04 | Web Search & Browsing | `DuckDuckGoSearchTool`, `VisitWebpageTool` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/04_web_search_and_browsing/notebook.ipynb) |
| 05 | Multi-Agent Orchestration | `managed_agents`, manager pattern | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/05_multi_agent_orchestration/notebook.ipynb) |
| 06 | MLflow Observability | `mlflow`, step tracing, run comparison | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/tatwan/agenticai_smolagents/blob/main/06_mlflow_observability/notebook.ipynb) |


> **Running in Colab?** Each notebook has a commented-out cell at the top to install dependencies (`!uv pip install ...`) and a section for loading your `HF_TOKEN` via Colab Secrets. See the [Quick Start for Colab](#quick-start-colab) section below.

---

## Course Structure

Each module folder contains three files:

- `outline.md` — what the module covers; intended as an instructor reference and planning document
- `notebook.ipynb` — the main learning artifact; this is what you run and work through
- `instructions.md` — module-specific prerequisites, step-by-step run instructions, and common errors with solutions

Work through the `notebook.ipynb` in each module in order. Refer to `instructions.md` if you hit a setup issue, and `outline.md` if you want to understand the full scope of a module before diving in.

---

## Tooling Summary

| Tool | Purpose | Free? |
|---|---|---|
| smolagents | Agent framework | Yes (Apache 2.0) |
| HuggingFace Inference API | LLM backend | Yes (free tier) |
| DuckDuckGo Search | Web search for agents | Yes |
| MLflow | Experiment tracking & observability | Yes (Apache 2.0) |
| uv | Fast Python package manager | Yes |
| OpenAI API | Optional: Module 03 model-swap demo | Paid (optional) |

---

## FAQ

**Q: Do I need a GPU?**

No. All models run on the HuggingFace Inference API (free tier). No local GPU is required.

---

**Q: Can I use a local model with Ollama instead of HuggingFace?**

Yes. Module 03 shows how to swap model providers. Use:

```python
LiteLLMModel(model_id="ollama_chat/llama3.2", api_base="http://localhost:11434")
```

---

**Q: Can I use OpenAI or Anthropic?**

Yes. Module 03 demonstrates the model swap. For example:

```python
LiteLLMModel(model_id="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])
```

The rest of the agent code is unchanged — smolagents abstracts the model backend cleanly.

---

**Q: The notebooks use `Qwen/Qwen2.5-Coder-32B-Instruct` — can I change the model?**

Yes. Replace `model_id` in the setup cell of any notebook with any HuggingFace model that supports chat. Recommended alternatives:

- `meta-llama/Llama-3.3-70B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`

---

**Q: I'm getting rate limit errors from DuckDuckGo.**

Add `time.sleep(3)` between agent runs, or reduce `max_steps`. DuckDuckGo's free API has a soft rate limit that can trigger under rapid repeated requests.

---

## Resources

- smolagents docs: https://huggingface.co/docs/smolagents
- HF Agents Course: https://huggingface.co/learn/agents-course
- MLflow docs: https://mlflow.org/docs/latest/
- smolagents GitHub: https://github.com/huggingface/smolagents

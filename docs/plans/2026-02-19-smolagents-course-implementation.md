# smolagents Mini-Course Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 6-module, code-heavy mini-course teaching AI agent development with smolagents, targeting intermediate–advanced data engineers and ML practitioners.

**Architecture:** Linear progression — each module folder contains `outline.md`, `notebook.ipynb`, and `instructions.md`. A single `pyproject.toml` at the root manages all dependencies via `uv`. Notebooks follow a consistent 6-section structure: Concept Brief → Setup → Guided Examples → Exercises → What You Built → Next Module Preview.

**Tech Stack:** `smolagents`, `uv`, HuggingFace Inference API (free tier), `DuckDuckGoSearchTool`, `VisitWebpageTool`, `LiteLLMModel` (OpenAI demo), `mlflow`

---

## Task 1: Project Scaffold

**Files:**
- Create: `smolagents/README.md`
- Create: `smolagents/pyproject.toml`
- Create: `smolagents/.env.example`

**Step 1: Create the smolagents root directory**

```bash
mkdir -p smolagents
```

**Step 2: Create `smolagents/pyproject.toml`**

```toml
[project]
name = "smolagents-course"
version = "0.1.0"
description = "Building AI Agents with smolagents — Mini-Course"
requires-python = ">=3.10"
dependencies = [
    "smolagents[litellm]>=1.0.0",
    "huggingface-hub>=0.23.0",
    "mlflow>=2.13.0",
    "duckduckgo-search>=6.0.0",
    "jupyter>=1.0.0",
    "ipykernel>=6.0.0",
    "python-dotenv>=1.0.0",
    "pandas>=2.0.0",
    "requests>=2.31.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Create `smolagents/.env.example`**

```bash
# Required: Hugging Face token (free tier works)
# Get yours at https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here

# Optional: Only needed for Module 03 model-agnosticism demo
OPENAI_API_KEY=sk-your_key_here
```

**Step 4: Create `smolagents/README.md`**

Content: Course overview, prerequisites (Python 3.10+, basic ML familiarity), setup instructions (`uv sync`, `cp .env.example .env`, `uv run jupyter lab`), module map table, and learning outcomes.

**Step 5: Create module subdirectories**

```bash
mkdir -p smolagents/01_foundations
mkdir -p smolagents/02_tools_and_custom_tools
mkdir -p smolagents/03_codeagent_vs_toolcalling
mkdir -p smolagents/04_web_search_and_browsing
mkdir -p smolagents/05_multi_agent_orchestration
mkdir -p smolagents/06_mlflow_observability
```

---

## Task 2: Module 01 — Foundations

**Files:**
- Create: `smolagents/01_foundations/outline.md`
- Create: `smolagents/01_foundations/instructions.md`
- Create: `smolagents/01_foundations/notebook.ipynb`

**Learning objectives:** Understand the agent loop (think → act → observe), initialize a `CodeAgent` with `InferenceClientModel`, run a first agent task, inspect agent steps and logs.

**Step 1: Write `outline.md`**

Sections:
1. What is an AI agent? (agent loop diagram in text)
2. smolagents architecture overview
3. InferenceClientModel — HF free tier setup
4. Your first CodeAgent
5. Inspecting agent steps
6. Exercises
7. Summary + next module teaser

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: Module 00 (setup), HF_TOKEN in `.env`
- Estimated time: 45–60 min
- How to run: `cd smolagents && uv run jupyter lab 01_foundations/notebook.ipynb`
- Common errors: token scopes, model rate limits, how to pick a free-tier model

**Step 3: Write `notebook.ipynb`**

Cells in order:

*Cell 1 — Concept Brief (markdown):*
Explain the agent loop: Think (LLM reasons) → Act (call a tool or write code) → Observe (get result) → repeat until done. Include ASCII diagram.

*Cell 2 — Setup:*
```python
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel

load_dotenv()

model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

*Cell 3 — First agent run:*
```python
agent = CodeAgent(tools=[], model=model, add_base_tools=True)
result = agent.run("What is the 15th Fibonacci number? Show your work.")
print(result)
```

*Cell 4 — Inspecting steps (markdown + code):*
Explain `agent.logs` / step memory. Show how to iterate and print each step type.
```python
for step in agent.memory.steps:
    print(type(step).__name__, ":", str(step)[:200])
```

*Cell 5 — Guided example: multi-step reasoning:*
```python
result = agent.run(
    "Create a list of the first 10 prime numbers, then calculate their sum and average."
)
print(result)
```

*Cell 6 — Exercise stubs:*
```python
# TODO Exercise 1: Create an agent that converts temperatures.
# Ask it: "Convert 98.6°F to Celsius and Kelvin."
# Print the result and inspect how many steps it took.

# TODO Exercise 2: Ask the agent to solve a simple data task:
# "Given the list [4, 7, 2, 9, 1, 5], find the median without using statistics library."
```

*Cell 7 — What You Built (markdown):*
Summary of concepts: agent loop, InferenceClientModel, CodeAgent, step inspection.

*Cell 8 — Next Module Preview (markdown):*
"In Module 02 you'll learn how to give your agent real capabilities by building custom tools."

---

## Task 3: Module 02 — Tools & Custom Tools

**Files:**
- Create: `smolagents/02_tools_and_custom_tools/outline.md`
- Create: `smolagents/02_tools_and_custom_tools/instructions.md`
- Create: `smolagents/02_tools_and_custom_tools/notebook.ipynb`

**Learning objectives:** Use built-in tools, write a custom tool with `@tool` decorator, write a custom tool by subclassing `Tool`, understand tool schemas, integrate custom tools into an agent.

**Step 1: Write `outline.md`**

Sections:
1. What makes a good tool? (schema, docstring, type hints)
2. Built-in smolagents tools overview
3. `@tool` decorator approach
4. Subclassing `Tool` for complex tools
5. Tool schema deep-dive
6. Exercises
7. Summary + next module teaser

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: Module 01 complete
- Estimated time: 60–75 min
- Common errors: missing type hints break tool schema, docstring format matters

**Step 3: Write `notebook.ipynb`**

Cells:

*Cell 1 — Concept Brief (markdown):*
Tools are the agent's hands. A tool is a Python function + a schema (name, description, input types, output type). The LLM uses the schema to decide when and how to call the tool. Quality of the docstring directly affects agent performance.

*Cell 2 — Setup (recap):*
```python
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel, tool, Tool

load_dotenv()
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

*Cell 3 — Built-in tools:*
```python
from smolagents import PythonInterpreterTool

python_tool = PythonInterpreterTool()
print(python_tool.name)
print(python_tool.description)
print(python_tool.inputs)
```

*Cell 4 — @tool decorator:*
```python
from huggingface_hub import list_models

@tool
def top_hf_model(task: str) -> str:
    """
    Returns the most downloaded model for a given task on Hugging Face Hub.

    Args:
        task: The ML task name (e.g., 'text-classification', 'text-to-image').
    """
    model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
    return model.id

agent = CodeAgent(tools=[top_hf_model], model=model)
result = agent.run("What is the most downloaded text-generation model on HuggingFace?")
print(result)
```

*Cell 5 — Inspect tool schema:*
```python
print("Name:", top_hf_model.name)
print("Description:", top_hf_model.description)
print("Inputs:", top_hf_model.inputs)
print("Output type:", top_hf_model.output_type)
```

*Cell 6 — Subclassing Tool:*
```python
import pandas as pd

class CSVSummaryTool(Tool):
    name = "csv_summary"
    description = (
        "Loads a CSV file from a local path and returns summary statistics "
        "including shape, column names, dtypes, and describe() output."
    )
    inputs = {
        "filepath": {
            "type": "string",
            "description": "Absolute or relative path to the CSV file.",
        }
    }
    output_type = "string"

    def forward(self, filepath: str) -> str:
        df = pd.read_csv(filepath)
        summary = (
            f"Shape: {df.shape}\n"
            f"Columns: {list(df.columns)}\n"
            f"Dtypes:\n{df.dtypes.to_string()}\n"
            f"Stats:\n{df.describe().to_string()}"
        )
        return summary
```

*Cell 7 — Exercise stubs:*
```python
# TODO Exercise 1: Write a @tool that takes a list of numbers as a string
# (comma-separated) and returns mean, median, and std dev.

# TODO Exercise 2: Create a Tool subclass that fetches the current price
# of a cryptocurrency using a free public API (e.g., CoinGecko).
# Hint: import requests; use https://api.coingecko.com/api/v3/simple/price

# TODO Exercise 3: Integrate both tools into a single CodeAgent and ask it:
# "What is the median of [3, 7, 1, 9, 4, 6] and what is the current price of bitcoin?"
```

*Cell 8 — What You Built (markdown)*

*Cell 9 — Next Module Preview (markdown):*
"In Module 03 you'll compare CodeAgent vs ToolCallingAgent — two fundamentally different ways agents reason and act."

---

## Task 4: Module 03 — CodeAgent vs ToolCallingAgent

**Files:**
- Create: `smolagents/03_codeagent_vs_toolcalling/outline.md`
- Create: `smolagents/03_codeagent_vs_toolcalling/instructions.md`
- Create: `smolagents/03_codeagent_vs_toolcalling/notebook.ipynb`

**Learning objectives:** Understand the architectural difference between the two agent types, run the same task with both and compare outputs/steps, know when to choose each, see how smolagents is model-agnostic via LiteLLMModel + OpenAI.

**Step 1: Write `outline.md`**

Sections:
1. How CodeAgent thinks (writes Python, executes it)
2. How ToolCallingAgent thinks (emits JSON tool calls)
3. Side-by-side comparison table
4. When to use each (decision framework)
5. Model agnosticism: swapping to OpenAI
6. Exercises
7. Summary + next module teaser

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: Modules 01–02
- Estimated time: 60–75 min
- Note: OpenAI section is optional; `OPENAI_API_KEY` needed only for that section
- Common errors: ToolCallingAgent requires models that support function/tool calling

**Step 3: Write `notebook.ipynb`**

Cells:

*Cell 1 — Concept Brief (markdown):*
- **CodeAgent**: writes Python code snippets → executes them in a sandbox → observes stdout/result. Powerful, flexible, can do arbitrary computation. Risk: code execution security surface.
- **ToolCallingAgent**: emits structured JSON `{"tool_name": ..., "arguments": {...}}` → framework dispatches → observes result. Predictable, auditable, no code execution. Better when output format matters and tools are well-defined.

*Cell 2 — Setup:*
```python
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, ToolCallingAgent, InferenceClientModel, tool

load_dotenv()
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

*Cell 3 — Shared tool for fair comparison:*
```python
@tool
def word_count(text: str) -> int:
    """
    Counts the number of words in the given text string.

    Args:
        text: The input text to count words in.
    """
    return len(text.split())
```

*Cell 4 — Same task, CodeAgent:*
```python
task = "Count the words in this sentence: 'The quick brown fox jumps over the lazy dog'. Then double that number."

code_agent = CodeAgent(tools=[word_count], model=model)
code_result = code_agent.run(task)
print("CodeAgent result:", code_result)
print("Steps taken:", len(code_agent.memory.steps))
```

*Cell 5 — Same task, ToolCallingAgent:*
```python
tool_agent = ToolCallingAgent(tools=[word_count], model=model)
tool_result = tool_agent.run(task)
print("ToolCallingAgent result:", tool_result)
print("Steps taken:", len(tool_agent.memory.steps))
```

*Cell 6 — Step-by-step diff (markdown + code):*
Print each step from both agents side-by-side. Highlight how CodeAgent writes code while ToolCallingAgent emits JSON calls.

*Cell 7 — Decision framework (markdown):*
```
Use CodeAgent when:
  - Task requires computation, loops, data manipulation
  - You need arbitrary logic between tool calls
  - You trust the execution environment

Use ToolCallingAgent when:
  - Tool calls are the primary action (no inter-step computation needed)
  - You need structured, auditable call logs
  - The LLM backend supports function/tool calling natively
  - Security: you don't want code execution
```

*Cell 8 — Model agnosticism demo (OpenAI, optional):*
```python
# ── Optional: requires OPENAI_API_KEY in .env ──────────────────────────────
# This section shows that smolagents is model-agnostic.
# Swap InferenceClientModel for LiteLLMModel — the agent code is identical.

from smolagents import LiteLLMModel

openai_model = LiteLLMModel(
    model_id="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

openai_agent = ToolCallingAgent(tools=[word_count], model=openai_model)
result = openai_agent.run(task)
print("OpenAI-backed agent result:", result)
# ───────────────────────────────────────────────────────────────────────────
```

*Cell 9 — Exercise stubs:*
```python
# TODO Exercise 1: Build a @tool that returns the number of vowels in a string.
# Run the same vowel-counting task with BOTH agent types.
# Compare: which produced cleaner intermediate steps?

# TODO Exercise 2: Pick a task that involves a loop (e.g., process a list of 5 items).
# Try it with ToolCallingAgent first — does it handle it well?
# Then try CodeAgent. Which one is better suited? Why?
```

*Cell 10 — What You Built (markdown)*

*Cell 11 — Next Module Preview (markdown):*
"In Module 04 you'll connect your agent to the real world — web search, browsing, and live data retrieval."

---

## Task 5: Module 04 — Web Search & Browsing

**Files:**
- Create: `smolagents/04_web_search_and_browsing/outline.md`
- Create: `smolagents/04_web_search_and_browsing/instructions.md`
- Create: `smolagents/04_web_search_and_browsing/notebook.ipynb`

**Learning objectives:** Use `DuckDuckGoSearchTool` and `VisitWebpageTool`, build a research workflow agent, understand result quality/reliability, combine search + page reading in multi-step tasks.

**Step 1: Write `outline.md`**

Sections:
1. Why web-enabled agents? (open vs closed information)
2. DuckDuckGoSearchTool — usage and results format
3. VisitWebpageTool — scraping pages
4. Building a research workflow
5. Reliability and hallucination guards
6. Exercises
7. Summary + next module teaser

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: Modules 01–03
- Estimated time: 60–75 min
- Note: DuckDuckGo rate-limits; add small sleeps between runs
- Common errors: blocked requests (add User-Agent), HTML parsing failures

**Step 3: Write `notebook.ipynb`**

Cells:

*Cell 1 — Concept Brief (markdown):*
Web-enabled agents can access live information beyond their training data. The pattern: search → pick best result → visit page → extract relevant content → reason. Quality depends on search query design and page content reliability.

*Cell 2 — Setup:*
```python
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool, VisitWebpageTool

load_dotenv()
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

*Cell 3 — DuckDuckGoSearchTool basics:*
```python
search_tool = DuckDuckGoSearchTool()
results = search_tool("smolagents huggingface tutorial 2024")
print(results)
```

*Cell 4 — VisitWebpageTool basics:*
```python
visit_tool = VisitWebpageTool()
content = visit_tool("https://huggingface.co/blog/smolagents")
print(content[:1000])
```

*Cell 5 — Research agent (search only):*
```python
research_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=5,
)
result = research_agent.run(
    "What are the main differences between smolagents and LangChain? "
    "Search for recent comparisons and summarize the key points."
)
print(result)
```

*Cell 6 — Research agent (search + visit):*
```python
deep_research_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=8,
)
result = deep_research_agent.run(
    "Find the latest HuggingFace blog post about agents, visit the page, "
    "and give me a 3-bullet summary of what it covers."
)
print(result)
```

*Cell 7 — Reliability note (markdown):*
Discuss: agents can hallucinate citations, pages can be unavailable, search results can be outdated. Best practices: ask agent to cite sources, limit max_steps, validate outputs.

*Cell 8 — Exercise stubs:*
```python
# TODO Exercise 1: Build an agent that searches for the current Python version,
# visits the official python.org page, and extracts the latest stable release number.

# TODO Exercise 2: Build a data-engineer-focused research agent.
# Task: "Find 3 recent articles about dbt best practices, visit each, and
# produce a comparison table of their main recommendations."
# Hint: Use max_steps=10 and VisitWebpageTool.
```

*Cell 9 — What You Built (markdown)*

*Cell 10 — Next Module Preview (markdown):*
"In Module 05 you'll build systems of agents — a manager that delegates to specialist sub-agents."

---

## Task 6: Module 05 — Multi-Agent Orchestration

**Files:**
- Create: `smolagents/05_multi_agent_orchestration/outline.md`
- Create: `smolagents/05_multi_agent_orchestration/instructions.md`
- Create: `smolagents/05_multi_agent_orchestration/notebook.ipynb`

**Learning objectives:** Understand the manager–specialist pattern, implement `managed_agents`, pass context between agents, design specialist agents with focused roles, understand when orchestration adds value vs overhead.

**Step 1: Write `outline.md`**

Sections:
1. Why multi-agent? (specialization, parallelism, modularity)
2. Manager + managed agent pattern
3. Agent-as-tool concept
4. Designing specialist agents
5. Information flow between agents
6. Exercises
7. Summary + next module teaser

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: Modules 01–04 (especially Module 04 for web tools)
- Estimated time: 75–90 min
- Common errors: circular delegation, context window overflow, vague agent descriptions

**Step 3: Write `notebook.ipynb`**

Cells:

*Cell 1 — Concept Brief (markdown):*
Multi-agent systems divide complex tasks: a manager agent breaks the problem into sub-tasks and delegates to specialist agents. Each specialist has a focused set of tools and a clear description. The manager never calls tools directly — it reasons about which specialist to use.

*Cell 2 — Setup:*
```python
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, ToolCallingAgent, InferenceClientModel, DuckDuckGoSearchTool, VisitWebpageTool, tool

load_dotenv()
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)
```

*Cell 3 — Build a web researcher specialist:*
```python
web_researcher = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=6,
    name="web_researcher",
    description=(
        "Searches the web and visits pages to retrieve factual, up-to-date information. "
        "Give it a specific research question as the task."
    ),
)
```

*Cell 4 — Build a data analyst specialist:*
```python
@tool
def compute_stats(numbers: str) -> str:
    """
    Computes mean, median, min, max, and std for a comma-separated list of numbers.

    Args:
        numbers: Comma-separated numeric values, e.g. '1,2,3,4,5'.
    """
    import statistics
    vals = [float(x.strip()) for x in numbers.split(",")]
    return (
        f"mean={statistics.mean(vals):.2f}, median={statistics.median(vals):.2f}, "
        f"min={min(vals):.2f}, max={max(vals):.2f}, stdev={statistics.stdev(vals):.2f}"
    )

data_analyst = CodeAgent(
    tools=[compute_stats],
    model=model,
    max_steps=5,
    name="data_analyst",
    description=(
        "Performs numerical analysis and statistics on data provided to it. "
        "Pass it raw numbers or data descriptions."
    ),
)
```

*Cell 5 — Manager agent:*
```python
manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_researcher, data_analyst],
    max_steps=8,
)

result = manager.run(
    "Research the average annual salary for a senior data engineer in the US in 2024. "
    "Then, given these reported figures: 130000, 145000, 152000, 128000, 160000, "
    "compute the statistics and compare them to what you found online."
)
print(result)
```

*Cell 6 — Inspect delegation (markdown + code):*
Show how to inspect which specialist was called and when from `manager.memory.steps`.

*Cell 7 — Design principles (markdown):*
- Each specialist should have ONE clear responsibility
- Descriptions are critical — the manager uses them to decide who to call
- Avoid giving the manager tools directly (keep it a pure orchestrator)
- Specialists should be stateless across calls

*Cell 8 — Exercise stubs:*
```python
# TODO Exercise 1: Add a third specialist: a "report_writer" agent that takes
# research findings and formats them into a structured markdown report.
# Wire it into the manager and ask for a full research + analysis + report workflow.

# TODO Exercise 2: Design a 2-agent system for a data pipeline task:
# - Agent 1: searches for a public CSV dataset URL on a topic of your choice
# - Agent 2: (using CSVSummaryTool from Module 02) analyzes the dataset
# Manager: coordinates and returns a combined summary.
```

*Cell 9 — What You Built (markdown)*

*Cell 10 — Next Module Preview (markdown):*
"In Module 06 you'll add full observability to your agents using MLflow — log runs, trace steps, and compare experiments."

---

## Task 7: Module 06 — MLflow Observability

**Files:**
- Create: `smolagents/06_mlflow_observability/outline.md`
- Create: `smolagents/06_mlflow_observability/instructions.md`
- Create: `smolagents/06_mlflow_observability/notebook.ipynb`

**Learning objectives:** Start an MLflow tracking server, log agent runs as MLflow experiments, trace agent steps with MLflow tracing, compare runs across different models/configurations, add custom metrics and tags.

**Step 1: Write `outline.md`**

Sections:
1. Why observability for agents? (non-determinism, debugging, iteration)
2. MLflow concepts refresher (experiments, runs, traces)
3. Logging agent runs manually
4. Automatic tracing with smolagents callbacks
5. Comparing runs in MLflow UI
6. Exercises
7. Course wrap-up

**Step 2: Write `instructions.md`**

Include:
- Prerequisites: All previous modules
- Estimated time: 75–90 min
- How to start MLflow server: `uv run mlflow ui --port 5000` (visit http://localhost:5000)
- Common errors: port conflicts, experiment name collisions, trace size limits

**Step 3: Write `notebook.ipynb`**

Cells:

*Cell 1 — Concept Brief (markdown):*
AI agents are non-deterministic: the same prompt can yield different paths, step counts, and quality. MLflow gives you a structured way to record what happened: which model, which tools, how many steps, what was the final answer, and how long it took. This is how you iterate on agent design scientifically.

*Cell 2 — Setup:*
```python
import os
import time
import mlflow
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool

load_dotenv()
model = InferenceClientModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=os.environ["HF_TOKEN"],
)

# Point to local MLflow server (run `uv run mlflow ui` in a terminal first)
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("smolagents-course")
```

*Cell 3 — Manual run logging:*
```python
task = "What is the current HuggingFace leaderboard top model for coding tasks?"

with mlflow.start_run(run_name="baseline-codeagent"):
    mlflow.log_param("model_id", "Qwen/Qwen2.5-Coder-32B-Instruct")
    mlflow.log_param("agent_type", "CodeAgent")
    mlflow.log_param("max_steps", 6)
    mlflow.log_param("task", task)

    agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model, max_steps=6)

    start = time.time()
    result = agent.run(task)
    elapsed = time.time() - start

    mlflow.log_metric("duration_seconds", elapsed)
    mlflow.log_metric("steps_taken", len(agent.memory.steps))
    mlflow.log_text(str(result), "result.txt")

    print(f"Done in {elapsed:.1f}s | Steps: {len(agent.memory.steps)}")
    print("Result:", result)
```

*Cell 4 — Callback-based automatic step tracing:*
```python
from smolagents.monitoring import LogLevel

# smolagents has built-in verbosity; combine with MLflow by capturing steps
def log_agent_steps_to_mlflow(agent, run_name: str, task: str, **params):
    """Run agent and log all steps to MLflow as a single run."""
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({"task": task, **params})
        start = time.time()
        result = agent.run(task)
        elapsed = time.time() - start

        steps_log = []
        for i, step in enumerate(agent.memory.steps):
            step_info = {"step": i, "type": type(step).__name__, "content": str(step)[:500]}
            steps_log.append(step_info)

        mlflow.log_metric("duration_seconds", elapsed)
        mlflow.log_metric("steps_taken", len(agent.memory.steps))
        mlflow.log_dict({"steps": steps_log}, "steps_trace.json")
        mlflow.log_text(str(result), "result.txt")

        return result

result = log_agent_steps_to_mlflow(
    agent=CodeAgent(tools=[DuckDuckGoSearchTool()], model=model, max_steps=6),
    run_name="traced-codeagent",
    task=task,
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    agent_type="CodeAgent",
)
```

*Cell 5 — Comparing two configurations:*
```python
from smolagents import ToolCallingAgent

# Run 1: CodeAgent
log_agent_steps_to_mlflow(
    agent=CodeAgent(tools=[DuckDuckGoSearchTool()], model=model, max_steps=6),
    run_name="compare-codeagent",
    task=task,
    agent_type="CodeAgent",
)

# Run 2: ToolCallingAgent — same task, same model
log_agent_steps_to_mlflow(
    agent=ToolCallingAgent(tools=[DuckDuckGoSearchTool()], model=model, max_steps=6),
    run_name="compare-toolcallingagent",
    task=task,
    agent_type="ToolCallingAgent",
)

print("Open http://localhost:5000 → smolagents-course experiment to compare runs.")
```

*Cell 6 — MLflow UI walkthrough (markdown):*
Step-by-step guide: open experiment → compare runs → look at params vs metrics → download result artifacts → use 'Compare' view to see duration and steps side-by-side.

*Cell 7 — Exercise stubs:*
```python
# TODO Exercise 1: Run the multi-agent system from Module 05 and log it to MLflow.
# Log: manager steps, total duration, each specialist's step count as separate metrics.

# TODO Exercise 2: Run the same task 3 times with the same agent configuration.
# Log each as a separate run. Compare results — how much does the output vary?
# This demonstrates agent non-determinism empirically.
```

*Cell 8 — What You Built (markdown):*
Full summary of the entire course: agent loop → tools → agent types → web access → orchestration → observability.

*Cell 9 — Where to go next (markdown):*
- smolagents docs: https://huggingface.co/docs/smolagents
- HF Agent course: https://huggingface.co/learn/agents-course
- MLflow LLM tracing: https://mlflow.org/docs/latest/llms/tracing/index.html
- Try: deploying an agent as a Gradio app, adding memory/persistence, using local models

---

## Task 8: Course README

**Files:**
- Modify: `smolagents/README.md`

**Step 1: Write complete README**

Sections:
- Course overview (one paragraph)
- Prerequisites table (Python 3.10+, basic ML, HF account)
- Quick start (5 commands: install uv → clone → uv sync → cp .env → jupyter lab)
- Module map table with links and estimated times
- Tooling summary (smolagents, DuckDuckGo, MLflow, uv)
- FAQ: "Do I need a GPU?" (No), "Can I use Ollama instead?" (Yes, see Module 03)

---

## Execution Order

Tasks must be executed in order (1 → 8). Each task is independent once the scaffold (Task 1) is done. Tasks 2–7 can be parallelized after Task 1 completes.

## Verification

After all tasks:
- `uv sync` completes without errors
- Each notebook runs top-to-bottom without errors (setup cells only — exercise stubs are expected to be incomplete)
- MLflow server starts with `uv run mlflow ui`
- All `outline.md` and `instructions.md` files are present and complete

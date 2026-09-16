# Module 04: Web Search & Browsing — how to run this lab

**Module:** 04 of 06  
**Read first:** [`outline.md`](outline.md)  
**Then run:** [`notebook.ipynb`](notebook.ipynb)

---

## Learning objectives

- Call `WebSearchTool` and `VisitWebpageTool` **standalone** before wrapping them in an agent
- Run the search → select → visit → extract → cite pattern
- Prompt for a source URL and check it appeared in the trace
- Recover from rate limits and bot-blocked pages without assuming your code is wrong

---

## Prerequisites

- Modules 01–03
- Network access. This module talks to the public web.

---

## Estimated time

75–90 minutes (web flake included)

---

## How to run

```bash
uv run jupyter lab 04_web_search_and_browsing/notebook.ipynb
```

Wait a few seconds between search cells. Do not hammer re-run.

---

## Common errors

### 1. Empty search / exception from DuckDuckGo

Free HTML search is rate-limited and occasionally layout-breaks.

Wait 30–60 seconds. Tighten the query. Try `WebSearchTool(engine="bing")`. If you are on a VPN that DDG dislikes, switch network.

`DuckDuckGoSearchTool` (the `ddgs` client) is an alternative with the same tool `name`. You do not need both.

### 2. Visit returns CAPTCHA / 403 / almost no text

The site blocked a non-browser GET. Pick another URL for the same fact (docs mirror, Wikipedia, official download page).

### 3. Agent “cites” a URL that never appeared in observations

Hallucinated citation. The task must say “only cite URLs you actually visited or received from search.” Then check `memory.steps`.

### 4. Agent never visits, only searches

The prompt did not require a visit. Add “visit the official page and extract the number from the page text.”

### 5. `max_steps` exhausted on Exercise 2

The stretch task is *stretch*. Drop to one article, or lower `max_steps` and accept a partial table.

---

## Tips

- Isolation-test both tools with `print(tool("..."))` first.
- Prefer `ToolCallingAgent` for “search then visit” if your model tool-calls; `CodeAgent` is fine if it does not.
- Official domains in the prompt save steps.

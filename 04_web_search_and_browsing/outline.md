# Module 04: Web Search & Browsing — Outline

---

## 1. Why Web-Enabled Agents?

### The Problem with Static Knowledge
- LLMs are trained on a fixed dataset with a knowledge cutoff date
- Questions like "What happened this week?" or "What is the current price of X?" cannot be answered reliably from training data alone
- Hallucinated citations and outdated facts are a direct consequence of closed information

### Open vs Closed Information
- **Closed information**: facts baked into model weights at training time — useful for reasoning, general knowledge, coding
- **Open information**: live data that changes continuously — prices, news, documentation releases, research papers, API changelogs
- Web tools bridge the gap: they allow an agent to reach out and retrieve current information on demand

### Live Data Scenarios
- **Financial**: current stock prices, exchange rates, commodity prices
- **News**: recent events, press releases, announcements
- **Software docs**: latest API reference, changelog entries, newly released libraries
- **Research**: preprints, conference proceedings, benchmark leaderboards
- **General factual queries**: "Who won X award this year?", "What is the population of Y city today?"

---

## 2. DuckDuckGoSearchTool

### How It Works
- Wraps the `duckduckgo_search` Python library (DDGS)
- Sends a text query to DuckDuckGo and retrieves organic search results
- No API key required — DuckDuckGo's search is free and does not require authentication
- Returns results as a formatted string containing multiple entries

### Output Format
Each result typically contains:
- **title**: the page title as it appears in search results
- **url**: the full URL of the result
- **body**: a short snippet/abstract of the page content (not the full page)

The tool concatenates these into a single string returned to the agent. The agent reads this string and decides which URLs are worth visiting.

### Rate Limiting Considerations
- DuckDuckGo actively rate-limits automated queries
- Repeated queries in quick succession will trigger a `RatelimitException`
- In notebooks: wait 3–5 seconds between consecutive searches
- In production: implement exponential backoff and cache results where possible
- Queries that are too broad ("AI") hit rate limits faster than specific queries

### Query Design Tips
- Be specific: "smolagents vs LangChain 2024 comparison" beats "agent frameworks"
- Include the year when recency matters: "Python 3.13 release notes 2024"
- Use quotes sparingly — DuckDuckGo handles natural language well
- For technical documentation, include the library name + "documentation" or "docs"
- Avoid very short queries (1–2 words) — they are both rate-limit-prone and return noisy results

---

## 3. VisitWebpageTool

### How It Works
- Accepts a URL string as input
- Fetches the page using an HTTP GET request (via `requests` or similar)
- Strips HTML markup and converts the page to cleaned markdown text
- Returns the markdown text to the agent

### Handling Large Pages
- Some pages are very long (documentation hubs, Wikipedia articles)
- The tool may truncate content beyond a certain token budget
- Agent strategy: use the search snippet to identify which page section is relevant, then visit and extract only what is needed
- If a page is too long, the agent should focus its extraction prompt on a specific subsection

### When Pages Block Bots
- Many sites detect and block automated HTTP requests (Cloudflare, CAPTCHAs, JS-rendered content)
- Symptoms: empty response, `403 Forbidden`, garbled content, or a CAPTCHA page returned as text
- This is expected and normal behavior — not a bug in the tool
- Agent mitigation: try a different URL for the same information (e.g., a mirror, a cached version, or a different source)
- Student mitigation: if the target URL is blocked, substitute a different URL in the task prompt

---

## 4. The Research Workflow Pattern

### The Four-Step Pattern
1. **Search** — use `DuckDuckGoSearchTool` to retrieve a list of relevant URLs and snippets
2. **Select** — read the snippets and choose the most promising URL(s) based on relevance, recency, and source credibility
3. **Visit** — use `VisitWebpageTool` to fetch the full content of the selected page
4. **Extract and Reason** — read the page content, extract the specific information needed, and synthesize a final answer

### Why This Is More Reliable Than Just Searching
- Search snippets are short — they may not contain the exact detail needed
- Visiting the page gives the agent access to the full context, tables, code examples, and precise figures
- An agent that only searches may hallucinate details not present in snippets
- The visit step anchors the agent's answer to actual page content, reducing confabulation
- The pattern mirrors how a human researcher would work: skim search results, open the best link, read carefully

### Practical Considerations
- Not every task requires visiting a page — for well-known facts, search snippets may be sufficient
- Visiting multiple pages increases accuracy but also increases step count and latency
- The agent should be prompted to prefer official sources (python.org, docs.huggingface.co) over aggregator blogs

---

## 5. Reliability and Hallucination Guards

### How Agents Hallucinate in Web Research
- **Citation fabrication**: the agent invents a plausible-looking URL without actually searching for it
- **Snippet extrapolation**: the agent reads a snippet and assumes details not present in it
- **Stale snippet data**: the search snippet is cached and may not reflect the current page content
- **Misattribution**: the agent attributes a fact to the wrong source

### Best Practices

#### Ask for Citations
- Always include "provide the source URL" in the task prompt
- This forces the agent to surface the URL it used, making verification possible
- Example: "Find X and return the answer along with the URL where you found it."

#### Set an Appropriate max_steps
- Web research can spiral: search → visit → search again → visit again → …
- Setting `max_steps=5` to `max_steps=8` is usually sufficient for most research tasks
- Very high `max_steps` (>10) rarely improves quality and increases cost and latency
- If the agent is looping, the problem is usually a vague task — rewrite the prompt first

#### Be Specific in Your Task
- Vague task: "Tell me about Python." → unfocused searches → low-quality result
- Specific task: "What is the latest stable Python release? Visit python.org/downloads and extract the exact version number." → targeted search → reliable result

#### Verify Critical Information
- For high-stakes outputs (medical, legal, financial), always manually check the agent's cited sources
- The agent's answer is a starting point, not ground truth
- Build human-in-the-loop review steps into workflows that depend on factual accuracy

---

## 6. Exercises

### Exercise 1: Python Release Finder
Build an agent with `DuckDuckGoSearchTool` and `VisitWebpageTool`.
- Task: "What is the latest stable release of Python? Visit python.org/downloads and extract the exact version number."
- After running: print the result and note how many steps were used.
- Reflection: did the agent visit the page, or did it answer from search snippets alone?

### Exercise 2: Data Engineering Research Agent
Build an agent with both web tools and `max_steps=10`.
- Task: "Search for 3 recent articles (2023 or later) about dbt (data build tool) best practices. For each article, visit the page and extract the top recommendation. Return a comparison table with columns: Article Title | Top Recommendation | Source URL."
- Challenge: does the agent reliably visit 3 separate URLs? If not, what would you change in the prompt to help it?

---

## 7. Summary and Module 05 Preview

### What Students Learn in This Module
- How to use `DuckDuckGoSearchTool` and `VisitWebpageTool` standalone and inside an agent
- The search → visit → extract → reason research workflow pattern
- Rate limiting behavior and how to work around it
- Hallucination risks specific to web-enabled agents and how to mitigate them

### Module 05 Preview: Multi-Agent Orchestration
A single agent with many tools can become unwieldy — tool selection gets confused, context grows too large, and the agent loses focus. Module 05 introduces the manager/worker architecture: a manager agent that receives a high-level task and delegates to specialist sub-agents, each focused on one capability (search, code execution, data processing). This is the architecture behind production-grade agent systems.

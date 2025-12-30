# Agentic Frameworks

This is my personal repository documenting my progress and work as I explore and develop various **agentic AI frameworks and design patterns**.

Each notebook represents a hands-on implementation where I experiment with multi-agent systems, LLM orchestration, and workflow patterns.

---

## Completed Exercises

### 1. Orchestrator-Worker Workflow Pattern
**Folder:** `OrchestratorWorker/`

My first implementation! This notebook explores the **Orchestrator-Worker** multi-agent design pattern — a powerful approach where a central orchestrator dynamically breaks down complex problems and delegates sub-tasks to specialized worker models.

#### What I Built:
- An orchestrator that takes a complex question and decomposes it into sub-problems
- Logic to route each sub-problem to the most suitable LLM based on its strengths
- A synthesis step that aggregates all worker responses into a unified final answer
- A comparison against a single-model baseline to evaluate the multi-agent approach

#### Tools & Models Used:
| Role | Model | Provider |
|------|-------|----------|
| Orchestrator | `openai/gpt-oss-120b` | Groq |
| Worker | `gpt-5-nano` | OpenAI |
| Worker | `claude-sonnet-4-5` | Anthropic |
| Worker | `gemini-2.5-flash` | Google |
| Worker | `openai/gpt-oss-120b` | Groq |
| Worker | `llama3.2` | Ollama (local) |
| Synthesizer | `openai/gpt-oss-120b` | Groq |

#### Key Takeaways:
1. **Richer detail** — The multi-model workflow produced far more raw facts, statistics, and diverse perspectives than a solo model.
2. **Coherence trade-off** — The solo model maintained better narrative coherence since all reasoning came from a single source, whereas the workflow's output was diluted by different strategies from different models.

---

### 2. AI-VC: Multi-Agent Startup Analyzer
**Folder:** `AIStartupAnalyzer/`

A multi-agent debate system that simulates a VC investment committee analyzing startups, using **OpenAISDK**.

#### Architecture
```
User Input → [ Optimist + Skeptic] (parallel) → Investment Committee → Decision
```

#### Project Structure:
```
AIStartupAnalyzer/
├── models.py        # Pydantic models with guardrail validator
├── tools.py         # Serper search tool
├── agents.py        # Optimist, Skeptic, Committee agents
├── orchestrator.py  # run_vc_debate() function
├── app.py           # Gradio UI
├── main.py          # CLI entry point
└── __init__.py      # Package exports
```

#### What I Built:
- **3 specialized agents** with structured Pydantic outputs
- **Parallel execution** of Bull/Bear cases for speed
- **Serper API tool** for real-time startup research
- **Pydantic guardrail** that blocks INVEST decisions with unresolved risks
- **Gradio UI** for interactive analysis

#### Agentic Patterns Used:
| Pattern | Implementation |
|---------|----------------|
| Multi-Agent Debate | Opposing Bull vs Bear viewpoints |
| Parallel Execution | `asyncio.gather()` for simultaneous research |
| Structured Outputs | Pydantic models with validators |
| Custom Guardrails | `@model_validator` blocking invalid decisions |
| Tool Use | `@function_tool` with Serper API |
| Hierarchical Orchestration | Committee synthesizes worker outputs |

#### Key Guardrail:
```python
@model_validator(mode='after')
def invest_requires_addressed_risks(self):
    if self.decision == "INVEST" and self.unresolved_risks:
        raise ValueError("Cannot INVEST with unresolved risks!")
```

#### Key Takeaways:
1. **Guardrails enable trust** — The Pydantic validator prevents logically invalid outputs (e.g., recommending INVEST while risks remain unaddressed). This is crucial for production AI.
2. **Debate improves reasoning** — Having opposing agents (Bull vs Bear) forces more thorough analysis than a single model. The Committee must explicitly reconcile conflicting views.
3. **Structured outputs > free text** — Pydantic models ensure every decision includes required fields like `unresolved_risks` and `risk_mitigations`, making downstream processing reliable.
4. **Parallel execution is key** — Running Bull/Bear cases simultaneously halves latency without sacrificing quality.
5. **Tools ground agents in reality** — The Serper search tool prevents hallucination by providing real-time data on funding, competitors, and news.

---

### 3. GhostPress: The Syndicate Crew
**Folder:** `GhostPress/`

A 4-agent content creation pipeline built with **CrewAI** that researches a topic, structures an outline, writes a blog post, and emails the final result.

#### Architecture
```
Topic Input → [ Researcher → Architect → Storyteller → Delivery ] (sequential) → Email Sent
```

#### Project Structure:
```
ghostpress/
├── src/ghostpress/
│   ├── crew.py           # Crew definition with 4 agents
│   ├── main.py           # Entry point
│   ├── config/
│   │   ├── agents.yaml   # Agent roles, goals, backstories
│   │   └── tasks.yaml    # Task descriptions and context chains
│   └── tools/
│       └── custom_tool.py  # SendEmailTool implementation
├── output/
│   ├── blog_post.md      # Generated blog post
│   └── email_campaign.md # Email confirmation
└── pyproject.toml        # Dependencies
```

#### What I Built:
- **4 specialized agents** in a sequential workflow
- **SerperDevTool** for real-time research and trend discovery
- **Custom SendEmailTool** using SendGrid API
- **Context chaining** where each agent builds on previous outputs
- **Auto-delivery** of the completed blog post via email

#### The Syndicate Agents:
| Agent | Role | Tools | LLM |
|-------|------|-------|-----|
| Insight Researcher | Market & Trend Analyst ("The Brain") | SerperDevTool | Groq `llama-3.1-70b-versatile` |
| Content Architect | Structural Engineer ("The Skeleton") | — | Groq `llama-3.1-70b-versatile` |
| Creative Storyteller | Lead Copywriter ("The Soul") | — | Groq `llama-3.1-70b-versatile` |
| Delivery Specialist | Email Campaign Manager ("The Logistics") | SendEmailTool | Groq `llama-3.1-70b-versatile` |

#### Agentic Patterns Used:
| Pattern | Implementation |
|---------|----------------|
| Sequential Process | Each task output feeds into the next |
| Context Chaining | `context: [previous_task]` in YAML config |
| Tool Use | Serper for research, SendGrid for delivery |
| YAML Configuration | Agents and tasks defined declaratively |
| Custom Tools | `BaseTool` subclass with Pydantic schema |

#### Key Takeaways:
1. **Sequential chaining is powerful** — Each agent's output becomes the context for the next, creating a coherent pipeline from research to delivery.
2. **YAML config is maintainable** — Defining agents and tasks in YAML keeps the Python code clean and makes iteration easy.
3. **Custom tools extend capabilities** — The SendEmailTool integrates SendGrid seamlessly, turning CrewAI into an end-to-end automation system.
4. **Backstories matter** — Detailed agent backstories (e.g., "veteran journalist with a nose for news") significantly improve output quality.
5. **CrewAI CLI streamlines workflow** — `crewai create`, `crewai install`, and `crewai run` make project scaffolding and execution simple.

---

## What's Next

I'll continue adding more agentic patterns and frameworks as I progress through my learning journey. Stay tuned!


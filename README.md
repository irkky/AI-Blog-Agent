
---

# 📘 AI Blog Production Agent

### *Multi-Agent Content Creation System built with Google ADK + Gemini*

This project is submitted as part of the **Kaggle 5-Day AI Agents Intensive – Capstone Project (2025)** under the **Concierge Agents** track.

It demonstrates a fully functional **multi-agent production pipeline** for generating high-quality, research-backed, SEO-optimized blog posts using Google ADK, Gemini 2.5, and custom tools.

---

## 🚀 Overview

Modern content creators waste hours researching, outlining, writing, editing, and optimizing articles for SEO. This project solves that by creating an **end-to-end autonomous blog production system** powered by multiple AI agents, tools, memory services, and evaluation logic.

Users simply enter a topic, tone, audience, and target word count — the agent team produces a full blog within seconds, along with SEO metadata and automated quality evaluation.

---

# 🎯 Features at a Glance

* 🧠 **6-Agent Autonomous Workflow**

  * Research → Outline → Draft → Critic → SEO → Evaluation
* 🔍 **Grounded Google Search Tool**
* 🧰 **Custom Tools**

  * Python Code Execution Tool
  * User Profile Tool
* 🗂 **Long-Term Memory + Session Memory**
* 🧹 **Context Compaction** (token-efficient)
* 📊 **Observability**

  * Structured JSONL logs
  * Execution time metrics
* 📝 **Agent Evaluation**

  * LLM judges clarity, SEO strength, structure, usefulness
* 🌐 **Streamlit Web UI**
* 🖥 **CLI Mode**

Fully satisfies **6+ Kaggle Capstone Requirements**.

---

# 🧩 Architecture

```
                 ┌───────────────────────────┐
                 │     User Input (UI/CLI)   │
                 └───────────────┬───────────┘
                                 │
                                 ▼
                      [1] ResearchAgent
                                 │
                     (Google Search Tool)
                                 │
                                 ▼
                      [2] OutlineAgent
                                 │
                    (Context Compaction)
                                 │
                                 ▼
                        [3] DraftAgent
                                 │
                                 ▼
                        [4] CriticAgent
                                 │
                                 ▼
                         [5] SEOAgent
                                 │
                                 ▼
                      [6] EvaluationAgent
                                 │
                                 ▼
                ┌────────────────────────────────┐
                │ Final SEO-Optimized Blog + JSON │
                │     scores (clarity, SEO, etc.) │
                └────────────────────────────────┘
```

---

# 🏗 Multi-Agent Workflow

### **1. ResearchAgent**

* Uses the **Google Search Tool** for grounded research
* Produces factual notes, bullet points, definitions, statistics

### **2. OutlineAgent**

* Converts research notes into a structured markdown outline

### **3. DraftAgent**

* Generates full blog content (headings, examples, explanations)

### **4. CriticAgent**

* Improves clarity, grammar, flow, and structure

### **5. SEOAgent**

* Produces:

  * SEO title
  * Meta description
  * URL slug
  * Keyword list
  * Social caption
* Returns final improved blog

### **6. EvaluationAgent**

Produces structured JSON:

```json
{
  "clarity": 9,
  "structure": 9,
  "seo": 8,
  "usefulness": 9,
  "overall": 9,
  "comments": "Well-structured and highly actionable."
}
```

---

# 🛠 Tools Integrated

### 🔍 **GoogleSearchTool**

Grounded search via Gemini 2.5’s `google_search` capability.

### 🧪 **CodeExecutionTool**

Runs safe Python code snippets for:

* readability analysis
* keyword density
* word count calculations

### 👤 **UserProfileTool**

Stores:

* preferred tones
* user writing style
* SEO keyword history
* blog history

---

# 🧠 Memory & Context Engineering

### **Short-Term Memory**

* ADK `InMemorySessionService`

### **Long-Term Memory**

* Custom `memory_bank.py` storing:

  * tone
  * preferred word count
  * blog history
  * SEO preferences

### **Context Compaction (`utils/context_manager.py`)**

* Truncates long outlines/drafts
* Keeps new content + summary
* Prevents token overflow
* Ensures consistent agent performance

---

# 🔎 Observability

All agent runs are logged to:

```
logs/
  events.jsonl
```

Logs include:

* agent_name
* step
* duration
* number of output characters
* error messages
* evaluation JSON

This satisfies Kaggle’s **Observability: Logging, Tracing, Metrics** requirement.

---

# 🧪 Agent Evaluation

The project includes a dedicated **EvaluationAgent** that judges each generated blog across:

* Clarity
* Structure
* SEO strength
* Usefulness
* Overall quality

This fulfills Kaggle’s **Agent Evaluation** requirement.

---

# 🖥 How to Run

---

## ✔ Option 1: Streamlit Web App (recommended)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open:

```
http://localhost:8501
```

---

## ✔ Option 2: CLI Mode

```bash
python main.py
```

You’ll be prompted for:

* topic
* tone
* audience
* word count

---

# 📦 Directory Structure

```
project/
│
├── blog_agents/
│   ├── research_agent.py
│   ├── outline_agent.py
│   ├── draft_agent.py
│   ├── critic_agent.py
│   ├── seo_agent.py
│   └── evaluation_agent.py
│
├── tools/
│   ├── google_search_tool.py
│   ├── code_execution_tool.py
│   └── user_profile_tool.py
│
├── memory/
│   ├── memory_bank.py
│   └── session_service.py
│
├── utils/
│   └── context_manager.py
│
├── logging/
│   └── logger.py
│
├── main.py
├── streamlit_app.py
├── config.py
├── requirements.txt
└── README.md
```

---

# 🏁 Conclusion

This project demonstrates a production-level **multi-agent AI system** using Google ADK and Gemini, capable of generating complete high-quality blog articles autonomously.

It shows:

* real agent orchestration
* grounded research
* custom tools
* memory
* evaluation
* observability
* a full UI

---
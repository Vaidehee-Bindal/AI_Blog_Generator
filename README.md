# AI Blog Writing Agent

An AI-powered long-form blog generation system built using **LangGraph**, **Groq LLMs**, **Tavily Search**, and **Streamlit**.

This project generates editorial blogs with:

- Research-backed content
- Humanized writing
- Structured long-form sections
- Modern publication-style UI
- Persistent blog storage
- Table of contents navigation
- Execution plan & evidence display

---

# Features

- Multi-agent AI workflow using LangGraph
- Research + writing orchestration
- Markdown blog generation
- Streamlit publication-quality frontend
- Persistent blog saving
- Session history
- Table of contents navigation
- Research evidence tracking
- Long-form structured writing
- SEO-friendly formatting
- Optimized for Groq API
- Tavily web search integration

---

# Tech Stack

- Python 3.10+
- LangGraph
- LangChain
- Groq LLM API
- Tavily Search API
- Streamlit
- Markdown Rendering

---

# Project Structure

```text
AI-BLOG-WRITER/
│
├── agents/
│   ├── editor_agent.py
│   ├── orchestrator_agent.py
│   ├── research_agent.py
│   ├── router_agent.py
│   └── writer_agent.py
│
├── generated_blogs/
│   └── Generated markdown blogs are stored here
│
├── models/
│   ├── schemas.py
│   └── state.py
│
├── prompts/
│   ├── editor_prompt.py
│   ├── orchestrator_prompt.py
│   ├── research_prompt.py
│   ├── router_prompt.py
│   └── writer_prompt.py
│
├── tools/
│   └── web_search.py
│
├── utils/
│   └── config.py
│
├── workflow/
│   └── blog_workflow.py
│
├── .env
├── frontend.py
├── main.py
├── requirements.txt
└── README.md
```

---

# Folder Explanation

## `agents/`

Contains all AI agents responsible for the workflow.

### `router_agent.py`

Decides whether web research is required.

### `research_agent.py`

Performs Tavily-based web research and evidence collection.

### `orchestrator_agent.py`

Creates the blog structure, sections, and execution plan.

### `writer_agent.py`

Generates detailed long-form blog sections.

### `editor_agent.py`

Humanizes and refines the final blog for SEO optimization.

---

## `generated_blogs/`

Stores all generated blogs automatically as `.md` markdown files.

Example:

```text
generated_blogs/
├── AI_Hallucinations.md
├── Future_of_AI.md
└── Parenting_Guide.md
```

---

## `models/`

Contains application schemas and workflow state definitions.

### `schemas.py`

Defines Pydantic schemas for plans, tasks, evidence, etc.

### `state.py`

Defines LangGraph workflow state management.

---

## `prompts/`

Contains all system prompts for the AI agents.

Each agent has its own prompt engineering file.

---

## `tools/`

Contains external integrations.

### `web_search.py`

Handles Tavily web search integration.

---

## `utils/`

Contains shared configuration utilities.

### `config.py`

Initializes:

- Groq LLM
- Tavily API
- Model configuration
- Environment variables

---

## `workflow/`

Contains LangGraph orchestration logic.

### `blog_workflow.py`

Defines:

- Nodes
- Edges
- Graph execution flow
- Sequential blog generation pipeline

---

## `frontend.py`

Main Streamlit frontend.

Features:

- Blog generation UI
- Sidebar controls
- TOC navigation
- Blog rendering
- Session history
- Evidence display
- Logs & execution plan

---

## `main.py`

Optional project entry point.

---

# Environment Setup

This project is optimized for:

- **Groq API**
- **Tavily Search API**

Create a `.env` file in the root directory.

Example:

```env
# GROQ
GROQ_API_KEY=your_groq_api_key_here

# TAVILY
TAVILY_API_KEY=your_tavily_api_key_here
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your_repo_url>
cd AI-BLOG-WRITER
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Project

```bash
streamlit run frontend.py
```

---

# Workflow Overview

```text
User Input
   ↓
Router Agent
   ↓
Research Agent (Optional)
   ↓
Orchestrator Agent
   ↓
Writer Agent
   ↓
Editor Agent
   ↓
Final Blog
   ↓
Save to generated_blogs/
```

## Workflow Diagram

<img width="1622" height="969" alt="workflow" src="https://github.com/user-attachments/assets/766fcbb5-daa0-46e2-b80e-aa95b7053479" />

---

# Output Features

Generated blogs include:

- Long-form sections
- Structured headings
- TOC navigation
- Research-backed content
- Editorial formatting
- Markdown export
<img width="1917" height="991" alt="image" src="https://github.com/user-attachments/assets/2320d4ca-d648-4e33-822a-a8bf12aed595" />
<img width="1919" height="990" alt="image" src="https://github.com/user-attachments/assets/3a996d9b-eaa3-40ca-b053-6278fe5cd61c" />
<img width="1919" height="995" alt="image" src="https://github.com/user-attachments/assets/56aaca19-8ff7-4693-a75d-18fd2d3aaa25" />
<img width="1919" height="982" alt="image" src="https://github.com/user-attachments/assets/1ed7a908-8d4d-4d89-9617-fe7156ba4123" />
<img width="1919" height="990" alt="image" src="https://github.com/user-attachments/assets/c9a2f3a5-d1dc-44ea-b7d5-657fdc328a7d" />
<img width="1919" height="990" alt="image" src="https://github.com/user-attachments/assets/fe2a0c58-afd2-4b80-aa95-679b0f6b4359" />

---

# Notes

- Optimized primarily for **Groq LLM inference speed**
- Tavily improves factual accuracy and freshness
- Streamlit frontend designed for publication-style reading
- Blogs are saved automatically

---

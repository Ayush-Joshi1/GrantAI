<div align="center">

# 🚀 GrantAI
### *Agentic AI Grant & Funding Finder for Startups*

<p align="center">
  <strong>Empowering Indian Startups with AI-Powered Government Grant Discovery, Eligibility Analysis, Proposal Generation, and Funding Guidance.</strong>
</p>

<p align="center">
  Built with ❤️ using <strong>IBM Granite</strong>, <strong>IBM watsonx.ai</strong>, <strong>FastAPI</strong>, <strong>React</strong>, <strong>Retrieval-Augmented Generation (RAG)</strong>, and <strong>Multi-Agent AI</strong>.
</p>

---

![IBM](https://img.shields.io/badge/IBM-watsonx.ai-blue?style=for-the-badge)
![Granite](https://img.shields.io/badge/IBM-Granite-black?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Powered-success?style=for-the-badge)

</div>

---

# 🌟 About GrantAI

GrantAI is an AI-powered platform designed to simplify the journey of discovering and applying for government grants. Instead of manually searching through lengthy documents, founders can interact with an intelligent assistant that recommends relevant schemes, evaluates eligibility, generates proposal drafts, analyzes deadlines, and provides actionable next steps.

The platform combines **IBM Granite Foundation Models**, **Retrieval-Augmented Generation (RAG)**, and a **Multi-Agent AI architecture** to deliver reliable, transparent, and context-aware responses grounded in official government documents.

---

# 🎯 Problem Statement

**Problem Statement No. 18 – AI Grant and Funding Finder for Startups**

Startups often struggle to identify suitable government funding opportunities because grant information is spread across multiple portals, documents, and organizations. Understanding eligibility criteria, deadlines, and proposal requirements is time-consuming and error-prone.

GrantAI solves this challenge by bringing AI-powered grant discovery, eligibility assessment, proposal assistance, deadline analysis, and intelligent notifications into one unified platform.

---

# ✨ Key Features

- 🔍 AI-Powered Grant Recommendation
- ✅ Startup Eligibility Analysis
- 📝 Intelligent Proposal Generation
- 📅 Deadline Analysis
- 🔔 Smart Notification & Action Guidance
- 🤖 Conversational AI Experience
- 📚 Retrieval-Augmented Generation (RAG)
- ⚡ Multi-Agent Workflow Coordination
- 📖 Evidence-Based Responses
- 🏛 Government Grant Knowledge Base

---

# 🧠 AI Capabilities

GrantAI consists of five specialized AI services:

### 🎯 Grant Recommendation Agent
Analyzes startup details and recommends the most relevant government funding opportunities.

### 📋 Eligibility Agent
Compares startup information against grant requirements and identifies confirmed matches, missing information, and potential eligibility gaps.

### 📝 Proposal Generation Agent
Creates structured proposal drafts using startup information and retrieved government grant evidence.

### 📅 Deadline Agent
Analyzes official grant documentation to identify application timelines while avoiding unsupported or fabricated deadlines.

### 🔔 Notification Agent
Provides practical reminders, next actions, and funding guidance based on the startup's current progress.

---

# 🏗 System Architecture

```text
                     Startup Founder
                            │
                            ▼
                   React Frontend
                            │
                    Shared API Layer
                            │
                            ▼
                         FastAPI
                            │
                  Dependency Injection
                            │
                            ▼
                   Workflow Coordinator
                            │
      ┌─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
 Grant Recommendation   Eligibility       Proposal Generator
      │                     │                     │
      └──────────────┬──────┴──────────────┬──────┘
                     ▼                     ▼
            Deadline Agent        Notification Agent
                     │
                     ▼
             Prompt Builders
                     │
                     ▼
          Shared RAGAnswerService
                     │
        Semantic Retriever + FAISS
                     │
                     ▼
      IBM Granite (watsonx.ai)
                     │
                     ▼
           Grounded AI Response
```

---

# 📂 Knowledge Base

GrantAI uses only official Government of India funding documents.

### Supported Organizations

- Startup India
- DPIIT
- BIRAC
- MeitY
- DST
- NIDHI Programs
- TIDE
- SAMRIDH
- GENESIS
- BioNEST
- BIG
- LEAP

### Dataset

- 📄 21 Official Government PDFs
- 🧩 1099 Indexed Knowledge Chunks
- ⚡ Semantic Vector Search using FAISS

---

# ⚙ Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

## Backend

- FastAPI
- Python

## Artificial Intelligence

- IBM Granite Foundation Models
- IBM watsonx.ai
- Prompt Engineering
- Multi-Agent AI

## Retrieval

- Retrieval-Augmented Generation (RAG)
- FAISS Vector Database
- Semantic Search
- Metadata Enrichment

## Dev Tools

- Git
- GitHub
- VS Code

---

# 📌 Project Workflow

```text
Startup Information
        │
        ▼
Grant Recommendation
        │
        ▼
Eligibility Assessment
        │
        ▼
Proposal Generation
        │
        ▼
Deadline Analysis
        │
        ▼
Notification Guidance
        │
        ▼
Unified AI Response
```

---

# 🌍 Why GrantAI?

✔ Eliminates manual grant research

✔ Personalized funding recommendations

✔ Grounded AI responses

✔ Transparent source-backed outputs

✔ Faster proposal preparation

✔ Startup-focused workflow

✔ Scalable Agentic AI architecture

---

# 🚀 Future Scope

- Real-time government portal synchronization
- Automated grant application tracking
- Multi-language support
- PDF proposal export
- Email and calendar reminders
- Startup incubator dashboards
- AI-powered application scoring
- Human-in-the-loop proposal review

---

# 📊 Project Status

| Module | Status |
|----------|--------|
| Planning | ✅ Complete |
| Frontend | ✅ Complete |
| Backend | ✅ Complete |
| AI Agents | ✅ Complete |
| RAG Pipeline | ✅ Complete |
| IBM Granite Integration | ✅ Complete |
| IBM watsonx.ai | ✅ Complete |
| Multi-Agent Workflow | ✅ Complete |
| Testing | ✅ Complete |

---

# 🛠 Installation

```bash
git clone <repository-url>

cd GrantAI

# Backend
cd apps/api
pip install -r requirements.txt

# Frontend
cd ../web
npm install

# Run Backend
uvicorn app.main:app --reload

# Run Frontend
npm run dev
```

---

# 📷 Screenshots

> *(Add your application screenshots here)*

- 🏠 Landing Page
- 📊 Dashboard
- 🔍 Grant Recommendation
- ✅ Eligibility Analysis
- 📝 Proposal Generation
- 📅 Deadline Analysis
- 🔔 Notification System
- 💬 Chat Interface

---

# 👨‍💻 Developed By

**Ayush Joshi**

Computer Science Engineering Student

Passionate about Artificial Intelligence, Machine Learning, Cloud Computing, and Building Intelligent Systems.

---

<div align="center">

## ⭐ If you found this project interesting, don't forget to Star the repository!

**GrantAI — Empowering Startups Through Agentic AI 🚀**

</div>

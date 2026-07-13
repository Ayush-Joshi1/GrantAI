# 🚀 GrantAI – Agentic AI Grant & Funding Finder for Startups

<div align="center">

![IBM](https://img.shields.io/badge/IBM-watsonx.ai-blue?style=for-the-badge)
![Granite](https://img.shields.io/badge/IBM-Granite-black?style=for-the-badge)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![RAG](https://img.shields.io/badge/RAG-Enabled-success?style=for-the-badge)
![AI Agents](https://img.shields.io/badge/AI-Multi--Agent-orange?style=for-the-badge)

### 🏆 IBM Project | Problem Statement No. 18
### **AI Grant & Funding Finder for Startups**

Helping startups discover government grants, evaluate eligibility, generate proposals, analyze deadlines, and receive AI-powered funding guidance using **IBM Granite**, **watsonx.ai**, **RAG**, and **Agentic AI**.

</div>

---

# 📖 Overview

Finding the right government grant is difficult.

Grant information is scattered across multiple government portals, lengthy PDF guidelines, notifications, eligibility documents, and funding schemes. Founders spend countless hours searching, comparing, and interpreting these documents before they even begin an application.

**GrantAI** solves this problem using **IBM Agentic AI**.

It combines **Retrieval-Augmented Generation (RAG)**, **IBM Granite Foundation Models**, **Semantic Search**, and a **Multi-Agent Workflow** to provide accurate, evidence-based funding guidance.

Instead of manually reading hundreds of pages of government documentation, founders simply describe their startup and GrantAI assists them throughout the complete funding journey.

---

# 🎯 Problem Statement

**Problem Statement No. 18**

**AI Grant and Funding Finder for Startups**

The platform addresses challenges such as:

- Discovering relevant Government funding schemes
- Understanding complex eligibility requirements
- Generating grant proposal drafts
- Tracking deadlines
- Providing startup-specific funding guidance
- Reducing manual effort using grounded AI

---

# ✨ Features

### 🎯 Smart Grant Recommendation
Personalized government grant recommendations based on startup profile, domain, funding requirement, location, and development stage.

---

### ✅ Eligibility Assessment
Compares startup information with official grant requirements and identifies:

- Eligibility matches
- Missing information
- Possible gaps
- Recommended next steps

---

### 📝 AI Proposal Generator
Creates structured proposal drafts using:

- Startup information
- Retrieved government grant evidence
- IBM Granite

while preventing fabricated claims.

---

### 📅 Deadline Analysis
Analyzes official grant deadlines and distinguishes:

- Application deadline
- Notification date
- Guideline publication
- Unknown or unsupported dates

without inventing information.

---

### 🔔 Smart Notifications
Provides actionable reminders and funding guidance while avoiding false urgency.

---

### 🤖 Agentic AI Workflow
GrantAI coordinates multiple AI capabilities through a unified workflow.

```
Founder
   │
   ▼
Grant Recommendation
   │
   ▼
Eligibility Analysis
   │
   ▼
Proposal Generation
   │
   ▼
Deadline Analysis
   │
   ▼
Notification Guidance
```

---

# 🏗 System Architecture

```
                    React Frontend
                           │
                           ▼
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
 ┌──────────────────────────────────────────┐
 │                                          │
 │ Grant Recommendation Agent               │
 │ Eligibility Agent                        │
 │ Proposal Generator Agent                 │
 │ Deadline Agent                           │
 │ Notification Agent                       │
 └──────────────────────────────────────────┘
                           │
                           ▼
                    Prompt Builders
                           │
                           ▼
                 Shared RAGAnswerService
                           │
                           ▼
                 Semantic Retriever (FAISS)
                           │
                           ▼
            Government Grant Knowledge Base
                           │
                           ▼
                   IBM Granite (watsonx.ai)
                           │
                           ▼
                 Grounded AI Responses
```

---

# 🧠 AI Technologies

- IBM Granite Foundation Models
- IBM watsonx.ai
- IBM watsonx Assistant
- IBM watsonx Orchestrate (Repository Integration)
- Retrieval-Augmented Generation (RAG)
- FAISS Vector Database
- Semantic Search
- Prompt Engineering
- Multi-Agent Workflow
- Clean Architecture
- SOLID Principles

---

# 📚 Knowledge Base

GrantAI retrieves information exclusively from official Government sources.

Current corpus includes:

- Startup India
- DPIIT
- Startup India Seed Fund
- BIRAC
- BIG
- BioNEST
- LEAP Fund
- MeitY
- TIDE
- SAMRIDH
- GENESIS
- DST
- NIDHI PRAYAS
- NIDHI EIR
- NIDHI Seed Support
- NIDHI Accelerator
- NIDHI TBI
- NIDHI CoE
- NIDHI iTBI

**Total Documents:** 21 Official Government PDFs

---

# 🧩 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

## Backend

- FastAPI
- Python

## AI

- IBM Granite
- IBM watsonx.ai
- Prompt Engineering

## Retrieval

- FAISS
- Semantic Search
- RAG

## Architecture

- Clean Architecture
- SOLID
- Dependency Injection

---

# 📂 Repository Structure

```
apps/
 ├── api/
 ├── web/
 └── workers/

packages/
 ├── shared-types/
 ├── ui-kit/
 └── python-shared/

docs/
infra/
scripts/
tests/
```

---

# 🚀 AI Workflow

```
Founder Query
      │
      ▼
React Frontend
      │
      ▼
FastAPI
      │
      ▼
Workflow Coordinator
      │
      ▼
AI Agents
      │
      ▼
Prompt Builders
      │
      ▼
RAG Pipeline
      │
      ▼
IBM Granite
      │
      ▼
Grounded Response
```

---

# 📊 Project Highlights

✅ AI-Powered Government Grant Discovery

✅ Personalized Funding Recommendations

✅ Grounded Eligibility Assessment

✅ Proposal Generation

✅ Deadline Analysis

✅ Notification Guidance

✅ IBM Granite Integration

✅ Retrieval-Augmented Generation

✅ Multi-Agent Workflow

✅ Production-Ready Clean Architecture

---

# 🧪 Testing

Project validation includes:

- Unit Tests
- API Tests
- Workflow Tests
- Integration Tests
- Container Tests
- Regression Tests

**Current Status**

- ✅ 94+ Tests Passed
- ✅ 0 Regression Failures

---

# 📄 Documentation

Project documentation includes:

- Architecture Documentation
- API Documentation
- Submission Checklist
- Demo Outline
- Architecture Diagrams
- Deployment Notes

---

# 🔮 Future Scope

- Live Government Portal Synchronization
- Real-Time Grant Updates
- Multilingual AI Support
- Human-in-the-Loop Proposal Review
- AI-Based Grant Ranking
- Enterprise Deployment
- Startup Incubator Integration

---

# 👨‍💻 Developed By

**Ayush Joshi**

IBM AI Internship Project

Problem Statement No. 18

**GrantAI – Agentic AI Grant & Funding Finder for Startups**

---

<div align="center">

### ⭐ If you like this project, consider giving it a Star ⭐

Built with ❤️ using IBM Granite, watsonx.ai, FastAPI, React & Agentic AI

</div>

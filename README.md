# Multi-Agent Self-Correcting RAG for RFP Generation

A **LangGraph-based multi-agent RAG system** that analyzes enterprise RFPs, retrieves relevant organizational knowledge, generates grounded proposal responses, and iteratively improves low-quality sections through a reviewer–revision loop.

## Architecture

```text
                         ┌───────────────┐
                         │   Input RFP   │
                         └───────┬───────┘
                                 ▼
                      ┌────────────────────┐
                      │ 1. RFP Analyzer    │
                      │ Requirements       │
                      │ Sections           │
                      │ Priorities         │
                      └─────────┬──────────┘
                                ▼
                    ┌────────────────────────┐
                    │ 2. Knowledge Retriever │
                    │                        │
                    │ OpenAI Embeddings      │
                    │          ↓             │
                    │      Pinecone          │
                    │   ┌──────┴──────┐      │
                    │   ▼             ▼      │
                    │ Historical   Company   │
                    │ Proposals       KB     │
                    │                        │
                    │ Adaptive Query         │
                    │ Refinement             │
                    └──────────┬─────────────┘
                               ▼
                      ┌──────────────────┐
                      │ 3. Response      │
                      │    Drafter       │
                      │ Grounded Section │
                      │ Generation       │
                      └────────┬─────────┘
                               ▼
                      ┌──────────────────┐
                      │ 4. Quality       │
                      │    Reviewer      │
                      │ Relevance        │
                      │ Completeness     │
                      │ Accuracy         │
                      └────────┬─────────┘
                               │
                         Score ≥ 7?
                         /          \
                       NO            YES
                       │              │
                       ▼              ▼
                 Revision Loop      Final
                 Feedback →        Proposal
                 Drafter
                       │
                       └── Max 2 Cycles
```

## Agents

### 1. RFP Analyzer

Transforms the raw RFP into structured information used by downstream agents.

* Extracts individual requirements
* Assigns priorities and categories
* Determines required proposal sections
* Estimates RFP complexity

### 2. Knowledge Retriever

Retrieves supporting evidence for each proposal section.

* Generates embeddings using `text-embedding-3-small`
* Searches separate Pinecone namespaces for historical proposals and company knowledge
* Routes retrieval based on requirement type
* Evaluates retrieval quality using similarity scores
* Performs a refined retrieval when the initial evidence is insufficient

Documents are indexed using **500-word chunks with 50-word overlap**.

### 3. Response Drafter

Generates proposal sections using Claude and retrieved evidence.

* Generates responses section-by-section
* Grounds responses in retrieved organizational knowledge
* Incorporates retrieved historical examples
* Uses reviewer feedback during subsequent revision cycles

### 4. Quality Reviewer

Evaluates generated proposal sections and drives the self-correction loop.

Each section receives a **0–10** score for:

* **Relevance** — how well the response addresses the requirement
* **Completeness** — whether the required information is covered
* **Accuracy** — whether claims are supported by retrieved evidence

Any metric below **7** triggers targeted feedback and regeneration.

## Self-Correction Loop

```text
             ┌──────────┐
             │ Retrieve │
             └────┬─────┘
                  ▼
             ┌──────────┐
             │ Generate │◄────────────┐
             └────┬─────┘             │
                  ▼                   │
             ┌──────────┐             │
             │  Review  │             │
             └────┬─────┘             │
                  │                   │
             Score ≥ 7?               │
              /      \                │
            YES       NO              │
             │         │              │
             ▼         ▼              │
           Accept   Feedback ─────────┘
```

Only sections that fail evaluation are regenerated. The workflow allows a maximum of **2 revision cycles**.

## Tech Stack

| Component           | Technology                      |
| ------------------- | ------------------------------- |
| Agent orchestration | LangGraph                       |
| LLM                 | Anthropic Claude                |
| Embeddings          | OpenAI `text-embedding-3-small` |
| Vector database     | Pinecone                        |
| Observability       | Langfuse                        |
| Language            | Python                          |

## Workflow

```text
RFP
 ↓
Structured Requirements
 ↓
Section-Specific Retrieval
 ↓
Grounded Proposal Generation
 ↓
Quality Evaluation
 ↓
Targeted Self-Correction
 ↓
Final Proposal
```

## Key Features

* Multi-agent LangGraph orchestration
* RAG over multiple knowledge namespaces
* Requirement-aware retrieval
* Adaptive query refinement
* Evidence-grounded generation
* LLM-based quality evaluation
* Reviewer-driven self-correction
* Selective section regeneration
* Langfuse tracing and observability

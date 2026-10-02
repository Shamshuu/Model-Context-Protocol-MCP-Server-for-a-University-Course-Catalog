# Model Context Protocol (MCP) Server for University Course Catalog

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Standard%20v1.0-8A2BE2)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-39%20Passing-brightgreen)](https://docs.pytest.org/)

A production-ready **Model Context Protocol (MCP)** server enabling Large Language Models (LLMs) and autonomous AI academic advisors to interact with a university course catalog. The server exposes structured tools, contextual text resources, and prompt templates, powered by an SQLite database with SQLAlchemy ORM and NetworkX graph dependency resolution.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Design](#architecture--design)
- [Database Schema & Seed Data](#database-schema--seed-data)
- [MCP Capabilities](#mcp-capabilities)
  - [Tools](#tools)
  - [Resources](#resources)
  - [Prompt Templates](#prompt-templates)
- [Quick Start with Docker](#quick-start-with-docker)
- [Local Development Setup](#local-development-setup)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [LLM Interaction & Example Queries](#llm-interaction--example-queries)
- [Repository Structure](#repository-structure)
- [Environment Variables](#environment-variables)

---

## Overview

Modern Large Language Models lack real-time access to private institutional databases. This MCP server acts as the backend infrastructure for an AI-powered Academic Advisor, exposing course descriptions, faculty directories, prerequisite dependencies, and course comparison workflows via standard MCP protocols.

### Key Highlights
- **MCP Protocol Compliance:** Standard Server-Sent Events (SSE) transport (`/sse`, `/messages`) and Streamable HTTP (`/mcp`), fully compatible with Claude Desktop and MCP Inspector.
- **Dual-Interface API:** Implements native MCP protocols alongside RESTful JSON endpoints (`/tools/...`, `/resources/...`, `/prompts/...`) and a direct JSON-RPC 2.0 handler.
- **Strict Data Contracts:** Validated inputs and outputs using Pydantic v2 schemas.
- **Graph Prerequisite Engine:** Uses `networkx.DiGraph` to compute multi-level prerequisite dependency trees.
- **One-Command Setup:** Containerized via Docker and orchestrated with Docker Compose, featuring built-in health checks and volume persistence.

---

## Architecture & Design

```
                     ┌────────────────────────────────────────┐
                     │          LLM / AI Advisor Agent        │
                     └───────────────────┬────────────────────┘
                                         │
                   MCP SSE / JSON-RPC / REST HTTP (:8080)
                                         │
                     ┌───────────────────▼────────────────────┐
                     │         FastMCP & Starlette App        │
                     ├───────────────────┬────────────────────┤
                     │   Healthcheck     │   MCP Handlers     │
                     │  (/health : 200)  │  (SSE & Messages)  │
                     └─────────┬─────────┴─────────┬──────────┘
                               │                   │
                               ▼                   ▼
                     ┌───────────────────┐ ┌──────────────────┐
                     │  Pydantic Schemas │ │ NetworkX Graph   │
                     │  Data Validation  │ │ Prereq Resolvers │
                     └─────────┬─────────┘ └─────────┬────────┘
                               │                     │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │   SQLAlchemy ORM    │
                               │  (Foreign Keys ON)  │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │ SQLite (catalog.db) │
                               └─────────────────────┘
```

---

## Database Schema & Seed Data

The catalog database is stored in SQLite (`data/catalog.db`). Foreign keys are enforced via `PRAGMA foreign_keys = ON;`.

### Entity-Relationship Schema

1. **`departments`**
   - `id` (INTEGER, Primary Key, Autoincrement)
   - `name` (TEXT, Not Null)
   - `code` (TEXT, Not Null, Unique) — *e.g., 'CS', 'MATH', 'EE', 'PHYS'*

2. **`instructors`**
   - `id` (INTEGER, Primary Key, Autoincrement)
   - `name` (TEXT, Not Null)
   - `email` (TEXT, Not Null)
   - `office` (TEXT, Nullable)
   - `department_id` (INTEGER, Foreign Key to `departments.id`)

3. **`courses`**
   - `id` (INTEGER, Primary Key, Autoincrement)
   - `course_code` (TEXT, Not Null, Unique) — *e.g., 'CS101'*
   - `title` (TEXT, Not Null)
   - `description` (TEXT, Not Null)
   - `credits` (INTEGER, Not Null)
   - `instructor_id` (INTEGER, Foreign Key to `instructors.id`)
   - `department_id` (INTEGER, Foreign Key to `departments.id`)

4. **`prerequisites`**
   - `course_id` (INTEGER, Foreign Key to `courses.id`) — *Target course*
   - `prerequisite_id` (INTEGER, Foreign Key to `courses.id`) — *Required course*
   - Primary Key: `(course_id, prerequisite_id)`

### Seed Catalog Overview

- **4 Departments:** Computer Science (`CS`), Mathematics (`MATH`), Electrical Engineering (`EE`), Physics (`PHYS`).
- **6 Instructors:** Dr. Alan Turing, Dr. Ada Lovelace, Dr. Grace Hopper, Dr. Carl Gauss, Dr. Claude Shannon, Dr. Marie Curie.
- **14 Courses:**
  - `CS101` Introduction to Programming (4 credits)
  - `CS102` Data Structures and Algorithms (4 credits, prereq: `CS101`)
  - `CS201` Systems Programming (4 credits, prereq: `CS102`)
  - `CS301` Operating Systems (4 credits, prereq: `CS201`)
  - `CS350` Distributed Systems (3 credits, prereq: `CS301`)
  - `CS250` Theory of Computation (3 credits, prereqs: `CS102`, `MATH202`)
  - `CS320` Artificial Intelligence (3 credits, prereqs: `CS102`, `MATH201`)
  - `MATH101` Introduction to Calculus (4 credits)
  - `MATH201` Linear Algebra (3 credits, prereq: `MATH101`)
  - `MATH202` Discrete Mathematics (3 credits, prereq: `MATH101`)
  - `EE101` Introduction to Digital Logic (4 credits)
  - `EE201` Computer Architecture (4 credits, prereqs: `EE101`, `CS101`)
  - `PHYS101` General Physics I (4 credits)
  - `PHYS102` General Physics II (4 credits, prereqs: `PHYS101`, `MATH101`)
- **Multi-Level Prerequisite Chain:** `CS101 -> CS102 -> CS201 -> CS301 -> CS350` (5 tiers).

---

## MCP Capabilities

### Tools

#### 1. `search_courses`
Searches courses by keyword matching code, title, or description, with optional department filter.

- **Input Schema:**
  ```json
  {
    "query": "string",
    "department_code": "string (optional)"
  }
  ```
- **Output Schema (on success):**
  ```json
  [
    {
      "course_code": "string",
      "title": "string",
      "credits": "integer"
    }
  ]
  ```
- **Example Usage:**
  ```bash
  curl -s -X POST http://localhost:8080/tools/search_courses \
    -H "Content-Type: application/json" \
    -d '{"query": "Introduction", "department_code": "CS"}'
  ```

#### 2. `get_prerequisites`
Retrieves direct prerequisite courses for a given course code.

- **Input Schema:**
  ```json
  {
    "course_code": "string"
  }
  ```
- **Output Schema (on success):**
  ```json
  {
    "course_code": "string",
    "prerequisites": [
      {
        "course_code": "string",
        "title": "string"
      }
    ]
  }
  ```
- **Example Usage:**
  ```bash
  curl -s -X POST http://localhost:8080/tools/get_prerequisites \
    -H "Content-Type: application/json" \
    -d '{"course_code": "CS102"}'
  ```

#### 3. `lookup_instructor`
Finds an instructor's contact details and department affiliation.

- **Input Schema:**
  ```json
  {
    "instructor_name": "string"
  }
  ```
- **Output Schema (on success):**
  ```json
  {
    "name": "string",
    "email": "string",
    "department_name": "string"
  }
  ```
- **Output Schema (on error):**
  ```json
  {
    "error": "Instructor not found"
  }
  ```
- **Example Usage:**
  ```bash
  curl -s -X POST http://localhost:8080/tools/lookup_instructor \
    -H "Content-Type: application/json" \
    -d '{"instructor_name": "Dr. Alan Turing"}'
  ```

#### 4. `get_prerequisite_graph`
Builds the full multi-level dependency graph for a course using NetworkX. Directed edges denote that `source` is a prerequisite for `target`.

- **Input Schema:**
  ```json
  {
    "course_code": "string"
  }
  ```
- **Output Schema (on success):**
  ```json
  {
    "nodes": [
      {"id": "string"}
    ],
    "edges": [
      {"source": "string", "target": "string"}
    ]
  }
  ```
- **Example Usage:**
  ```bash
  curl -s -X POST http://localhost:8080/tools/get_prerequisite_graph \
    -H "Content-Type: application/json" \
    -d '{"course_code": "CS301"}'
  ```
- **Response:**
  ```json
  {
    "nodes": [{"id": "CS101"}, {"id": "CS102"}, {"id": "CS201"}, {"id": "CS301"}],
    "edges": [
      {"source": "CS101", "target": "CS102"},
      {"source": "CS102", "target": "CS201"},
      {"source": "CS201", "target": "CS301"}
    ]
  }
  ```

---

### Resources

#### 1. `course_descriptions`
- **URI:** `catalog://course_descriptions`
- **Description:** Formatted text directory of all courses and descriptions.
- **Format:** `[CODE] Title: Description`
- **Fetch via REST:**
  ```bash
  curl -s http://localhost:8080/resources/course_descriptions
  ```

#### 2. `department_directory`
- **URI:** `catalog://department_directory`
- **Description:** Formatted text listing of academic departments and codes.
- **Format:** `Department Name (CODE)`
- **Fetch via REST:**
  ```bash
  curl -s http://localhost:8080/resources/department_directory
  ```

---

### Prompt Templates

#### 1. `course_comparison_template`
- **Name:** `course_comparison_template`
- **Placeholders:** `{{course_code_1}}` and `{{course_code_2}}`
- **Template Content:**
  ```
  Create a table comparing the following two courses: {{course_code_1}} and {{course_code_2}}. Include columns for Title, Credits, Description, and Prerequisites.
  ```
- **Fetch via REST:**
  ```bash
  curl -s http://localhost:8080/prompts/course_comparison_template
  ```

---

## Quick Start with Docker

The entire application runs via Docker Compose with a single command.

### 1. Launch Services
```bash
docker compose up --build -d
```
*(or `docker-compose up --build -d`)*

### 2. Verify Health
The container includes a health check running against `http://localhost:8080/health`.
```bash
docker compose ps
```
Output:
```
NAME                            STATUS
university-catalog-mcp-server   Up About a minute (healthy)
```

### 3. Check Logs
```bash
docker compose logs -f
```

### 4. Stop Services
```bash
docker compose down
```

---

## Local Development Setup

To run locally without Docker:

### 1. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database
```bash
python data/seed.py
```

### 4. Start Server
```bash
python -m app.main
```
The server will be accessible at `http://localhost:8080`.

---

## Testing & Quality Assurance

A comprehensive automated test suite covers database constraints, business services, FastMCP tools, resources, prompt templates, REST endpoints, and JSON-RPC dispatching.

Run the test suite:
```bash
pytest -v
```

### Test Coverage Highlights
- `tests/test_database.py`: Verifies existence of `data/catalog.db`, schema validation of all 4 tables, foreign keys, row counts (>= 3 departments, >= 5 instructors, >= 10 courses, >= 3 with prereqs), and seed idempotency.
- `tests/test_services.py`: Tests keyword searches, department filters, empty queries, direct prerequisites, faculty lookups, multi-level graph traversal, and resource generation.
- `tests/test_mcp_tools.py`: Tests FastMCP tool listing and execution via the MCP protocol.
- `tests/test_mcp_resources_prompts.py`: Tests FastMCP resource reads and prompt template placeholders.
- `tests/test_api_endpoints.py`: Tests the healthcheck (`/health`), REST routes, and direct JSON-RPC 2.0 requests.

---

## LLM Interaction & Example Queries

When connected to an LLM assistant (e.g., via Claude Desktop or an AI agent harness), the assistant can handle queries like:

1. **"What introductory computer science courses are offered?"**
   - The LLM calls `search_courses(query="Introduction", department_code="CS")`.
   - Returns `CS101: Introduction to Programming (4 credits)`.

2. **"What prerequisites do I need to complete before enrolling in Operating Systems (CS301)?"**
   - The LLM calls `get_prerequisite_graph(course_code="CS301")`.
   - Returns dependency chain: `CS101 -> CS102 -> CS201 -> CS301`.
   - The LLM advises: *"To take CS301 (Operating Systems), you must first complete CS201 (Systems Programming), which requires CS102 (Data Structures & Algorithms), which requires CS101 (Introduction to Programming)."*

3. **"Who teaches Artificial Intelligence and how can I contact them?"**
   - The LLM calls `search_courses(query="Artificial Intelligence")` to identify instructor `Dr. Alan Turing`.
   - Then calls `lookup_instructor(instructor_name="Dr. Alan Turing")`.
   - Returns: `a.turing@university.edu`, Department: `Computer Science`.

4. **"Compare CS101 and CS102 for me."**
   - The LLM retrieves `course_comparison_template` and fills in `CS101` and `CS102`.
   - The LLM outputs a side-by-side comparison table with titles, credits, descriptions, and prerequisites.

---

## Repository Structure

```
.
├── Dockerfile                  # Container build instructions (python:3.12-slim)
├── docker-compose.yml          # Container orchestration with health check & volume mount
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration (asyncio_mode = auto)
├── .env.example                # Environment variable documentation
├── .gitignore                  # Git ignore rules (catalog.db tracked)
├── .dockerignore               # Docker build exclusions
├── README.md                   # Project documentation
├── app/
│   ├── __init__.py             # Package marker
│   ├── config.py               # Environment configuration and paths
│   ├── database.py             # SQLAlchemy engine, session, and SQLite pragmas
│   ├── models.py               # SQLAlchemy ORM models (departments, instructors, courses, prerequisites)
│   ├── schemas.py              # Pydantic v2 validation contracts
│   ├── services.py             # Business logic and NetworkX graph solver
│   ├── mcp_server.py           # FastMCP server registration (tools, resources, prompts)
│   └── main.py                 # ASGI application combining SSE, REST, and JSON-RPC
├── data/
│   ├── catalog.db              # Pre-seeded SQLite database file
│   └── seed.py                 # Database seeding script
└── tests/
    ├── __init__.py
    ├── conftest.py             # Test fixtures & database setup
    ├── test_database.py        # Database schema & constraint tests
    ├── test_services.py        # Service layer unit tests
    ├── test_mcp_tools.py       # MCP tool listing and invocation tests
    ├── test_mcp_resources_prompts.py # MCP resource and prompt tests
    └── test_api_endpoints.py   # REST & JSON-RPC endpoint tests
```

---

## Environment Variables

Documented in `.env.example`:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLite database URI inside container | `sqlite:////app/data/catalog.db` |
| `HOST` | Bind address for server | `0.0.0.0` |
| `PORT` | Listening port for server | `8080` |
| `LOG_LEVEL` | Logging level (`debug`, `info`, `warning`, `error`) | `info` |

---

## License

This project is licensed under the MIT License.
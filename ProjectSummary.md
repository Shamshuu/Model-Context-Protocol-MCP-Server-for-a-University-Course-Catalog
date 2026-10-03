# Project Summary: Model Context Protocol (MCP) Server for University Course Catalog

## 1. What Will This Project Do? (Overview)

This project builds an **AI Academic Advisor backend infrastructure** using the **Model Context Protocol (MCP)**.

Instead of an AI model guessing or hallucinating about what courses a university offers, this server connects directly to the university's course catalog database. It exposes:
- **Interactive Tools:** Functions an LLM can invoke dynamically (e.g., searching courses by keyword, looking up instructors, checking prerequisites, and generating full dependency trees).
- **Contextual Resources:** Read-only background knowledge documents an LLM can read (e.g., a catalog-wide course summary or department directory).
- **Prompt Templates:** Pre-configured prompts that guide the LLM on how to perform structured tasks (e.g., generating side-by-side course comparisons).
- **Universal Transports:** Supports native MCP (Server-Sent Events at `/sse` and Streamable HTTP at `/mcp`), direct JSON-RPC 2.0 requests, and RESTful HTTP endpoints for testing with `curl`.

---

## 2. What Is the Purpose? (The "Why")

Modern Large Language Models (LLMs) like Claude, Gemini, or GPT have two major limitations when acting as domain-specific assistants:
1. **Lack of Private / Real-Time Data:** They do not know a university's specific course catalog, real faculty contact details, or current degree requirements.
2. **Hallucination on Dependencies:** LLMs frequently make mistakes when reasoning through multi-step requirements (e.g., *"Can I take CS301 if I only took CS101?"*).

**The Purpose of this Project:**
- By implementing the **Model Context Protocol (MCP)**, we create a secure, standardized bridge between any AI agent and the university's database.
- The AI model doesn't need to be retrained or fine-tuned. It simply queries our MCP server on demand, receiving validated, real-time facts to answer student questions accurately.

---

## 3. System Architecture

```
              ┌────────────────────────────────────────────────────────┐
              │             AI Model / Claude / User Curl              │
              └───────────────────────────┬────────────────────────────┘
                                          │
                            Port 8080 (SSE / JSON-RPC / REST)
                                          │
              ┌───────────────────────────▼────────────────────────────┐
              │                Starlette & FastMCP Server              │
              ├───────────────────────────┬────────────────────────────┤
              │      REST & Healthcheck   │     MCP Protocol Engine    │
              │     (/health, /tools/...) │   (/sse, /messages, /mcp)  │
              └─────────────┬─────────────┴──────────────┬─────────────┘
                            │                            │
                            ▼                            ▼
              ┌───────────────────────────┐┌───────────────────────────┐
              │   Pydantic Data Schemas   ││ NetworkX Prereq Graph DAG │
              │   (Strict Data Contracts) ││ (Multi-Level Ancestors)   │
              └─────────────┬─────────────┘└─────────────┬─────────────┘
                            │                            │
                            └─────────────┬──────────────┘
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │    SQLAlchemy 2.0 ORM     │
                            │  (PRAGMA foreign_keys=ON) │
                            └─────────────┬─────────────┘
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │ SQLite (data/catalog.db)  │
                            └───────────────────────────┘
```

---

## 4. How Each and Every Functionality Is Implemented

### A. The Four MCP Tools (Dynamic Functions)
1. **`search_courses(query, department_code)`**
   - **How it works:** Implemented in `app/services.py`. It runs an SQLAlchemy query joining `courses` and `departments`. It applies case-insensitive search (`ilike`) across course codes, titles, and descriptions. If a `department_code` is provided (e.g., `'CS'`), it filters specifically by that department.
   - **Output:** Returns a validated list of `CourseSummary` objects (`course_code`, `title`, `credits`). Returns `[]` if no matches are found.

2. **`get_prerequisites(course_code)`**
   - **How it works:** Implemented in `app/services.py`. It queries the target course and looks up its direct relationships in the `prerequisites` mapping table.
   - **Output:** Returns `{course_code, prerequisites: [{"course_code": "...", "title": "..."}]}`. If the course has no prerequisites (like `CS101`), it cleanly returns an empty list `[]`. If the course doesn't exist, it returns `{"error": "Course '...' not found"}`.

3. **`lookup_instructor(instructor_name)`**
   - **How it works:** Implemented in `app/services.py`. It performs an exact match first, followed by a case-insensitive substring match on the `instructors` table, joining `departments` to get the department's full name.
   - **Output:** Returns `{name, email, department_name}`. If not found, it returns a structured error: `{"error": "Instructor not found"}`.

4. **`get_prerequisite_graph(course_code)`**
   - **How it works:** Implemented in `app/services.py`. This is an advanced graph-theory tool using **NetworkX**:
     - It constructs a Directed Acyclic Graph (DAG) where nodes are courses and directed edges point from prerequisite to target (`source -> target`).
     - It computes `nx.ancestors(G, target_code)` to traverse all transitive prerequisites up the entire tree (e.g., for `CS301`, it discovers `CS201`, `CS102`, and `CS101`).
     - It extracts the subgraph and sorts nodes and edges.
   - **Output:** Returns `{nodes: [{"id": "..."}], edges: [{"source": "...", "target": "..."}]}`.

---

### B. The Two Contextual Resources (Background Knowledge)
1. **`catalog://course_descriptions`**
   - **How it works:** Dynamically reads all courses from the database and formats them into a standardized text document: `[CODE] Title: Description`. An LLM can read this entire resource into its system prompt to understand all offerings at once.
2. **`catalog://department_directory`**
   - **How it works:** Formats all academic departments into a directory string: `Department Name (CODE)` (e.g., `Computer Science (CS)`).

---

### C. The Prompt Template (Reusable AI Workflow)
1. **`course_comparison_template`**
   - **How it works:** Implemented in `app/mcp_server.py`. It defines a structured template containing placeholders `{{course_code_1}}` and `{{course_code_2}}`.
   - **Behavior:** When called without arguments, it returns the raw template string. When called with arguments (e.g., `CS101` and `CS102`), it replaces the placeholders so the AI immediately formats a side-by-side comparison matrix.

---

### D. Database Seeding & Startup Verification
- Implemented in `data/seed.py`.
- When the server starts up, it automatically checks if the database is populated. If empty, it populates **4 departments**, **6 instructors**, **14 courses**, and **14 prerequisite links** with multi-tier dependency chains (`CS101 -> CS102 -> CS201 -> CS301 -> CS350`).
- It is idempotent: subsequent runs will not duplicate rows.

---

## 5. How Each Technology Used in This Project Helps

| Technology | Role in the Project | Why It Helps / Advantage |
|---|---|---|
| **Model Context Protocol (`mcp` / FastMCP)** | Protocol Layer | Provides the official standard for tool declaration, resource serving, and prompt templating. Compatible with Claude Desktop, MCP Inspector, and custom AI agents. |
| **Pydantic v2** | Data Validation & Schemas | Defines strict data contracts for every tool input and output. Guarantees that data sent to and received from AI models is 100% type-safe and schema-validated. |
| **SQLAlchemy 2.0** | Object-Relational Mapper (ORM) | Abstracts SQL into clean Python classes (`Course`, `Instructor`, `Department`). Prevents SQL injection, handles database sessions, and enforces foreign key relationships (`PRAGMA foreign_keys = ON;`). |
| **NetworkX** | Graph Theory Engine | Used to build directed graphs of course dependencies. It solves complex multi-level prerequisite chains and cycle detection with built-in graph algorithms like `nx.ancestors` in milliseconds. |
| **SQLite** | Database Engine | A serverless, zero-configuration database stored as a single file (`data/catalog.db`). Requires no external DB container (like Postgres), making the project completely portable and persistent via volume mounts. |
| **Starlette & Uvicorn** | Web Framework & ASGI Server | Powers the high-performance asynchronous HTTP and Server-Sent Events (SSE) server. Enables serving standard MCP endpoints, REST endpoints, and Docker health checks on port 8080 simultaneously. |
| **Docker & Docker Compose** | Containerization & Orchestration | Packages Python 3.12, all dependencies, `curl`, and code into an isolated image. Enables a 1-command startup (`docker compose up --build -d`) with volume persistence (`./data:/app/data`) and automated health checks (`/health`). |
| **Pytest & Pytest-Asyncio** | Automated Testing | Comprehensive test suite of **39 tests** verifying database schemas, business logic, NetworkX graph outputs, FastMCP tools, resources, prompts, and REST/JSON-RPC endpoints. |

---

## 6. Real-World LLM Interaction Scenario

1. A student asks: *"I want to take Operating Systems (CS301). What courses do I need to finish first, and who teaches it?"*
2. The AI assistant queries the MCP server:
   - Calls `get_prerequisite_graph(course_code="CS301")` $\rightarrow$ receives the dependency chain: `CS101 -> CS102 -> CS201 -> CS301`.
   - Calls `search_courses(query="Operating Systems")` $\rightarrow$ finds instructor `Dr. Grace Hopper`.
   - Calls `lookup_instructor(instructor_name="Dr. Grace Hopper")` $\rightarrow$ gets email `g.hopper@university.edu` and office `Hopper Hall 303`.
3. The AI answers the student with **100% verified factual data** from the university catalog, completely eliminating hallucinations.

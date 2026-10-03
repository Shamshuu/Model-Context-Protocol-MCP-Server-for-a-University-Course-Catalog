# Project Summary: Model Context Protocol (MCP) Server for University Course Catalog

## Executive Summary
This project implements a production-grade **Model Context Protocol (MCP)** server providing structured access to a university course catalog for autonomous AI academic advisors and Large Language Models. Built with Python 3.12, FastMCP, SQLAlchemy ORM, and NetworkX, the server exposes 4 tools, 2 contextual resources, and 1 prompt template, fully containerized with Docker and Docker Compose.

---

## Technical Architecture

1. **Protocol Layer (FastMCP + Starlette)**
   - **MCP Standard SSE Transport:** Exposes `/sse` for event streaming and `/messages` for client-to-server messaging.
   - **Streamable HTTP Transport:** Exposes `/mcp` for unified streaming sessions.
   - **Direct JSON-RPC 2.0:** Standard JSON-RPC handler at `POST /` and `POST /jsonrpc`.
   - **RESTful Endpoints:** Direct HTTP endpoints for tool invocation, resource retrieval, and health checks.

2. **Data & Persistence Layer**
   - **SQLite Database (`data/catalog.db`):** Pre-seeded with 4 departments, 6 instructors, 14 courses, and 14 prerequisite dependencies.
   - **Foreign Key Integrity:** Enforced at connection time via `PRAGMA foreign_keys = ON;`.
   - **Idempotent Seeder (`data/seed.py`):** Automatically initializes the database on startup if empty; supports `--force` re-seeding.

3. **Graph Dependency Engine (NetworkX)**
   - Course prerequisite relationships are modeled as a Directed Acyclic Graph (DAG) `(prereq -> course)`.
   - Multi-level transitive dependencies are computed via `nx.ancestors(G, target)` to extract complete prerequisite chains.

4. **Containerization & Health Monitoring**
   - **Dockerfile:** Based on `python:3.12-slim`, includes `curl` for container health monitoring.
   - **Docker Compose:** Maps port 8080, mounts `./data:/app/data` for persistence, and configures automated container healthchecks.

---

## Capabilities & Verified Core Requirements

| Requirement | Implementation | Status |
|---|---|---|
| **1. Docker & Docker Compose** | `docker-compose.yml` with `mcp-server` service, healthcheck, port 8080 | Verified |
| **2. .env.example** | Documents `DATABASE_URL=sqlite:////app/data/catalog.db`, `PORT=8080` | Verified |
| **3. Seeded Database** | SQLite database `catalog.db` with departments, instructors, courses, prerequisites | Verified |
| **4. Tool: search_courses** | Keyword search across code, title, and description with optional department filter | Verified |
| **5. Tool: get_prerequisites** | Retrieves direct prerequisites for a course code (empty array if none) | Verified |
| **6. Tool: lookup_instructor** | Look up instructor email and department; returns structured error if not found | Verified |
| **7. Tool: get_prerequisite_graph** | Returns multi-level DAG with nodes and edges (`source` is prerequisite for `target`) | Verified |
| **8. Resource: course_descriptions** | Formatted directory string of all courses and descriptions | Verified |
| **9. Resource: department_directory** | Formatted directory string of all academic departments and codes | Verified |
| **10. Prompt: course_comparison_template** | Prompt template with `{{course_code_1}}` and `{{course_code_2}}` placeholders | Verified |

---

## Test Suite Results
- Total Tests: **39 passing** (0 failures)
- Test modules:
  - `tests/test_database.py` (4 tests)
  - `tests/test_services.py` (12 tests)
  - `tests/test_mcp_tools.py` (7 tests)
  - `tests/test_mcp_resources_prompts.py` (6 tests)
  - `tests/test_api_endpoints.py` (10 tests)

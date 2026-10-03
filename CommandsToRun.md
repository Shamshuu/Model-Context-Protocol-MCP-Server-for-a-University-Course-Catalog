# Commands To Run: University Course Catalog MCP Server

This guide contains complete commands to run, test, and interact with the MCP Server from **Git Bash**, **macOS Terminal**, or **Linux Shell**.

---

## 1. Quick Start with Docker (Recommended)

### Start Server
```bash
docker compose up --build -d
```
*(or `docker-compose up --build -d`)*

### Verify Container Health
```bash
docker compose ps
```
*Expected status:* `Up ... (healthy)`

### Run Automated Demo Script
A pre-configured verification script executes all `curl` commands below in sequence:
```bash
./scripts/demo_curl.sh
```

### Stop Server
```bash
docker compose down
```

---

## 2. Healthcheck & Service Discovery

### Health Check Endpoint
```bash
curl -s http://localhost:8080/health
```
*Expected Output:*
```json
{"status":"healthy","service":"mcp-server","version":"1.0.0"}
```

### Service Root & Discovery
```bash
curl -s http://localhost:8080/
```
*Expected Output:*
```json
{
  "name": "University Course Catalog MCP Server",
  "status": "running",
  "mcp_endpoints": {
    "sse": "/sse",
    "messages": "/messages",
    "streamable_http": "/mcp"
  },
  "rest_endpoints": {
    "health": "/health",
    "tools": "/tools",
    "resources": "/resources",
    "prompts": "/prompts"
  }
}
```

### List All Registered Tools
```bash
curl -s http://localhost:8080/tools
```

---

## 3. Testing MCP Tools via curl

### Tool 1: `search_courses`
Searches courses matching a query string, with optional department filter.

#### Case A: Matching query
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "Introduction"}'
```
*Expected Output:*
```json
[
  {"course_code":"CS101","title":"Introduction to Programming","credits":4},
  {"course_code":"EE101","title":"Introduction to Digital Logic","credits":4},
  {"course_code":"MATH101","title":"Introduction to Calculus","credits":4}
]
```

#### Case B: Filtered by department code
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "Programming", "department_code": "CS"}'
```
*Expected Output:*
```json
[
  {"course_code":"CS101","title":"Introduction to Programming","credits":4},
  {"course_code":"CS201","title":"Systems Programming","credits":4}
]
```

#### Case C: Non-existent query (returns empty list `[]`)
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "QuantumWarpDrive"}'
```
*Expected Output:*
```json
[]
```

---

### Tool 2: `get_prerequisites`
Retrieves direct prerequisite courses for a course code.

#### Case A: Course with prerequisites (`CS102` requires `CS101`)
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisites \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS102"}'
```
*Expected Output:*
```json
{
  "course_code": "CS102",
  "prerequisites": [
    {"course_code": "CS101", "title": "Introduction to Programming"}
  ]
}
```

#### Case B: Course with NO prerequisites (`CS101`)
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisites \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS101"}'
```
*Expected Output:*
```json
{
  "course_code": "CS101",
  "prerequisites": []
}
```

---

### Tool 3: `lookup_instructor`
Finds faculty contact details and department affiliation.

#### Case A: Valid instructor (`Dr. Alan Turing`)
```bash
curl -s -X POST http://localhost:8080/tools/lookup_instructor \
  -H "Content-Type: application/json" \
  -d '{"instructor_name": "Dr. Alan Turing"}'
```
*Expected Output:*
```json
{
  "name": "Dr. Alan Turing",
  "email": "a.turing@university.edu",
  "department_name": "Computer Science"
}
```

#### Case B: Non-existent instructor (structured error)
```bash
curl -s -X POST http://localhost:8080/tools/lookup_instructor \
  -H "Content-Type: application/json" \
  -d '{"instructor_name": "Unknown Professor"}'
```
*Expected Output:*
```json
{
  "error": "Instructor not found"
}
```

---

### Tool 4: `get_prerequisite_graph`
Builds the full multi-level dependency graph using NetworkX.

#### Multi-level dependency chain for `CS301` (`CS101 -> CS102 -> CS201 -> CS301`)
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisite_graph \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS301"}'
```
*Expected Output:*
```json
{
  "nodes": [
    {"id": "CS101"},
    {"id": "CS102"},
    {"id": "CS201"},
    {"id": "CS301"}
  ],
  "edges": [
    {"source": "CS101", "target": "CS102"},
    {"source": "CS102", "target": "CS201"},
    {"source": "CS201", "target": "CS301"}
  ]
}
```

---

## 4. Testing MCP Resources via curl

### Resource 1: `course_descriptions`
```bash
curl -s http://localhost:8080/resources/course_descriptions
```
*Output preview:*
```
[CS101] Introduction to Programming: A foundational course on programming principles...
[CS102] Data Structures and Algorithms: Study of fundamental data structures...
...
```

### Resource 2: `department_directory`
```bash
curl -s http://localhost:8080/resources/department_directory
```
*Output:*
```
Computer Science (CS)
Electrical Engineering (EE)
Mathematics (MATH)
Physics (PHYS)
```

---

## 5. Testing MCP Prompt Template via curl

### Prompt: `course_comparison_template`
```bash
curl -s http://localhost:8080/prompts/course_comparison_template
```
*Output:*
```
Create a table comparing the following two courses: {{course_code_1}} and {{course_code_2}}. Include columns for Title, Credits, Description, and Prerequisites.
```

---

## 6. Testing Native MCP JSON-RPC 2.0 via curl

### Initialize MCP Session
```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

### Call Tool via JSON-RPC
```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_courses","arguments":{"query":"Calculus"}}}'
```

---

## 7. Local Testing without Docker

```bash
# Activate virtual environment
source .venv/bin/activate

# Run full pytest test suite (39 tests)
pytest -v
```

# Commands To Run: University Course Catalog MCP Server

This guide provides step-by-step instructions with **Git Bash `curl` commands** to run and verify every single functionality of the University Course Catalog MCP Server from scratch to end.

---

## Step 1: Start the Application with Docker Compose

Open **Git Bash** in the project root directory and run:

```bash
docker compose up --build -d
```
*(or `docker-compose up --build -d`)*

### Verify Container Health Status
```bash
docker compose ps
```
**Expected Output:**
```text
NAME                            IMAGE                                              STATUS
university-catalog-mcp-server   model-context-protocol-mcp-server...               Up About a minute (healthy)
```

> **Automated One-Click Demo:** You can also run the bundled demo script anytime in Git Bash:
> ```bash
> ./scripts/demo_curl.sh
> ```

---

## Step 2: Healthcheck & Service Discovery

### 1. Verify Healthcheck Endpoint
```bash
curl -s http://localhost:8080/health
```
**Expected Output:**
```json
{"status":"healthy","service":"mcp-server","version":"1.0.0"}
```

### 2. Root Service Discovery
```bash
curl -s http://localhost:8080/
```
**Expected Output:**
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

### 3. Inspect All Registered Tools
```bash
curl -s http://localhost:8080/tools
```

---

## Step 3: Test MCP Tools

### Tool 1: `search_courses`

**Case A — Keyword Search (`"Introduction"`):**
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "Introduction"}'
```
**Expected Output:**
```json
[
  {"course_code":"CS101","title":"Introduction to Programming","credits":4},
  {"course_code":"EE101","title":"Introduction to Digital Logic","credits":4},
  {"course_code":"MATH101","title":"Introduction to Calculus","credits":4}
]
```

**Case B — Keyword + Department Filter (`query="Programming", department_code="CS"`):**
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "Programming", "department_code": "CS"}'
```
**Expected Output:**
```json
[
  {"course_code":"CS101","title":"Introduction to Programming","credits":4},
  {"course_code":"CS201","title":"Systems Programming","credits":4}
]
```

**Case C — Non-Existent Query (Returns empty array `[]`):**
```bash
curl -s -X POST http://localhost:8080/tools/search_courses \
  -H "Content-Type: application/json" \
  -d '{"query": "QuantumWarpDrive"}'
```
**Expected Output:**
```json
[]
```

---

### Tool 2: `get_prerequisites`

**Case A — Course with Prerequisites (`CS102` requires `CS101`):**
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisites \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS102"}'
```
**Expected Output:**
```json
{
  "course_code": "CS102",
  "prerequisites": [
    {
      "course_code": "CS101",
      "title": "Introduction to Programming"
    }
  ]
}
```

**Case B — Course with NO Prerequisites (`CS101`):**
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisites \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS101"}'
```
**Expected Output:**
```json
{
  "course_code": "CS101",
  "prerequisites": []
}
```

---

### Tool 3: `lookup_instructor`

**Case A — Valid Instructor (`"Dr. Alan Turing"`):**
```bash
curl -s -X POST http://localhost:8080/tools/lookup_instructor \
  -H "Content-Type: application/json" \
  -d '{"instructor_name": "Dr. Alan Turing"}'
```
**Expected Output:**
```json
{
  "name": "Dr. Alan Turing",
  "email": "a.turing@university.edu",
  "department_name": "Computer Science"
}
```

**Case B — Non-Existent Instructor (Structured Error):**
```bash
curl -s -X POST http://localhost:8080/tools/lookup_instructor \
  -H "Content-Type: application/json" \
  -d '{"instructor_name": "Unknown Professor"}'
```
**Expected Output:**
```json
{
  "error": "Instructor not found"
}
```

---

### Tool 4: `get_prerequisite_graph`

**Multi-Level Dependency Chain for `CS301` (`CS101 -> CS102 -> CS201 -> CS301`):**
```bash
curl -s -X POST http://localhost:8080/tools/get_prerequisite_graph \
  -H "Content-Type: application/json" \
  -d '{"course_code": "CS301"}'
```
**Expected Output:**
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

## Step 4: Test MCP Contextual Resources

### Resource 1: `course_descriptions`
```bash
curl -s http://localhost:8080/resources/course_descriptions
```
**Expected Output (Formatted Directory):**
```text
[CS101] Introduction to Programming: A foundational course on programming principles, problem-solving, and algorithmic thinking using Python.
[CS102] Data Structures and Algorithms: Study of fundamental data structures such as lists, stacks, queues, trees, graphs, and algorithm design and analysis.
[CS201] Systems Programming: Covers low-level programming concepts, memory management, operating system interfaces, and concurrency in C/C++.
...
```

### Resource 2: `department_directory`
```bash
curl -s http://localhost:8080/resources/department_directory
```
**Expected Output:**
```text
Computer Science (CS)
Electrical Engineering (EE)
Mathematics (MATH)
Physics (PHYS)
```

---

## Step 5: Test MCP Prompt Template

### Prompt: `course_comparison_template`
```bash
curl -s http://localhost:8080/prompts/course_comparison_template
```
**Expected Output (Contains Placeholders `{{course_code_1}}` & `{{course_code_2}}`):**
```text
Create a table comparing the following two courses: {{course_code_1}} and {{course_code_2}}. Include columns for Title, Credits, Description, and Prerequisites.
```

---

## Step 6: Test Native MCP JSON-RPC 2.0 Protocol

### 1. MCP Initialization
```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```
**Expected Output:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true},
      "prompts": {"listChanged": true}
    },
    "serverInfo": {
      "name": "University Course Catalog Server",
      "version": "1.0.0"
    }
  }
}
```

### 2. Call Tool via JSON-RPC
```bash
curl -s -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_courses","arguments":{"query":"Calculus"}}}'
```
**Expected Output:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"course_code\": \"MATH101\",\n  \"title\": \"Introduction to Calculus\",\n  \"credits\": 4\n}"
      }
    ],
    "isError": false
  }
}
```

---

## Step 7: Run Full Pytest Suite

To run all 39 automated unit, integration, and MCP protocol tests locally:

```bash
source .venv/bin/activate
pytest -v
```
**Expected Result:**
```text
============================== 39 passed in 0.13s ==============================
```

---

## Step 8: Stop the Application

```bash
docker compose down
```

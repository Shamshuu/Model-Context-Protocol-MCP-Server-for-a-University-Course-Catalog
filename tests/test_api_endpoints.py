import json


def test_healthcheck_endpoint(client):
    """Test healthcheck endpoint returns 200 OK and healthy status."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_root_index_endpoint(client):
    """Test root endpoint provides service discovery metadata."""
    res = client.get("/")
    assert res.status_code == 200
    assert "University Course Catalog" in res.json()["name"]


def test_rest_search_courses(client):
    """Test REST endpoint for search_courses."""
    # Valid query
    res = client.post("/tools/search_courses", json={"query": "Introduction"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "course_code" in item
        assert "title" in item
        assert "credits" in item

    # Department filtered
    res = client.post("/tools/search_courses", json={"query": "Programming", "department_code": "CS"})
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Non-existent query returns empty list
    res = client.post("/tools/search_courses", json={"query": "NonExistentCourseStringXYZ"})
    assert res.status_code == 200
    assert res.json() == []


def test_rest_get_prerequisites(client):
    """Test REST endpoint for get_prerequisites."""
    # Course with prerequisites
    res = client.post("/tools/get_prerequisites", json={"course_code": "CS102"})
    assert res.status_code == 200
    data = res.json()
    assert data["course_code"] == "CS102"
    assert len(data["prerequisites"]) >= 1

    # Course with no prerequisites
    res = client.post("/tools/get_prerequisites", json={"course_code": "CS101"})
    assert res.status_code == 200
    assert res.json()["prerequisites"] == []


def test_rest_lookup_instructor(client):
    """Test REST endpoint for lookup_instructor."""
    # Valid instructor
    res = client.post("/tools/lookup_instructor", json={"instructor_name": "Dr. Alan Turing"})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Dr. Alan Turing"
    assert data["email"] == "a.turing@university.edu"
    assert data["department_name"] == "Computer Science"

    # Non-existent instructor returns structured error
    res = client.post("/tools/lookup_instructor", json={"instructor_name": "Unknown Doctor"})
    assert res.status_code == 200
    assert res.json() == {"error": "Instructor not found"}


def test_rest_get_prerequisite_graph(client):
    """Test REST endpoint for get_prerequisite_graph."""
    res = client.post("/tools/get_prerequisite_graph", json={"course_code": "CS301"})
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data and "edges" in data
    assert len(data["nodes"]) >= 4
    assert len(data["edges"]) >= 3


def test_rest_resources_endpoints(client):
    """Test REST endpoints for course_descriptions and department_directory."""
    # Text response
    res = client.get("/resources/course_descriptions")
    assert res.status_code == 200
    assert "[CS101]" in res.text
    assert "Introduction to Programming" in res.text

    # JSON response
    res = client.get("/resources/course_descriptions", headers={"Accept": "application/json"})
    assert res.status_code == 200
    assert "[CS101]" in res.json()["content"]

    # Department directory
    res = client.get("/resources/department_directory")
    assert res.status_code == 200
    assert "Computer Science (CS)" in res.text


def test_rest_prompt_endpoint(client):
    """Test REST endpoint for course_comparison_template."""
    res = client.get("/prompts/course_comparison_template")
    assert res.status_code == 200
    assert "{{course_code_1}}" in res.text
    assert "{{course_code_2}}" in res.text


def test_jsonrpc_dispatcher(client):
    """Test direct JSON-RPC 2.0 requests via POST."""
    # initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    res = client.post("/", json=init_req)
    assert res.status_code == 200
    assert res.json()["result"]["serverInfo"]["name"] == "University Course Catalog Server"

    # tools/list
    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    res = client.post("/", json=tools_req)
    assert res.status_code == 200
    tool_names = [t["name"] for t in res.json()["result"]["tools"]]
    assert "search_courses" in tool_names

    # tools/call
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_courses",
            "arguments": {"query": "Introduction"}
        }
    }
    res = client.post("/", json=call_req)
    assert res.status_code == 200
    assert res.json()["result"]["isError"] is False

    # resources/list
    res_req = {"jsonrpc": "2.0", "id": 4, "method": "resources/list"}
    res = client.post("/", json=res_req)
    assert res.status_code == 200
    res_names = [r["name"] for r in res.json()["result"]["resources"]]
    assert "course_descriptions" in res_names

    # prompts/list
    prompt_req = {"jsonrpc": "2.0", "id": 5, "method": "prompts/list"}
    res = client.post("/", json=prompt_req)
    assert res.status_code == 200
    p_names = [p["name"] for p in res.json()["result"]["prompts"]]
    assert "course_comparison_template" in p_names

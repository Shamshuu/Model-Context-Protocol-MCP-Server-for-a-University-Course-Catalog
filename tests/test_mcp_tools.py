import pytest
from app.mcp_server import mcp_server


@pytest.mark.asyncio
async def test_mcp_tools_listing():
    """Verify that all four required tools are registered with FastMCP."""
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_courses" in tool_names
    assert "get_prerequisites" in tool_names
    assert "lookup_instructor" in tool_names
    assert "get_prerequisite_graph" in tool_names


@pytest.mark.asyncio
async def test_mcp_call_search_courses():
    """Verify calling search_courses through FastMCP."""
    res = await mcp_server.call_tool("search_courses", {"query": "Introduction"})
    # Result tuple contains ([TextContent], raw_dict)
    assert len(res[0]) > 0
    raw_dict = res[1]
    assert "result" in raw_dict
    assert isinstance(raw_dict["result"], list)
    assert len(raw_dict["result"]) > 0


@pytest.mark.asyncio
async def test_mcp_call_search_courses_empty():
    """Verify calling search_courses with non-matching query returns empty list."""
    res = await mcp_server.call_tool("search_courses", {"query": "NonExistentXYZ"})
    raw_dict = res[1]
    assert raw_dict["result"] == []


@pytest.mark.asyncio
async def test_mcp_call_get_prerequisites():
    """Verify calling get_prerequisites through FastMCP."""
    res = await mcp_server.call_tool("get_prerequisites", {"course_code": "CS102"})
    raw_dict = res[1]
    assert raw_dict["result"]["course_code"] == "CS102"
    assert len(raw_dict["result"]["prerequisites"]) >= 1


@pytest.mark.asyncio
async def test_mcp_call_lookup_instructor():
    """Verify calling lookup_instructor through FastMCP."""
    res = await mcp_server.call_tool("lookup_instructor", {"instructor_name": "Dr. Alan Turing"})
    raw_dict = res[1]
    assert raw_dict["result"]["name"] == "Dr. Alan Turing"
    assert raw_dict["result"]["department_name"] == "Computer Science"


@pytest.mark.asyncio
async def test_mcp_call_lookup_instructor_not_found():
    """Verify calling lookup_instructor with non-existent name returns structured error."""
    res = await mcp_server.call_tool("lookup_instructor", {"instructor_name": "Unknown Person"})
    raw_dict = res[1]
    assert raw_dict["result"] == {"error": "Instructor not found"}


@pytest.mark.asyncio
async def test_mcp_call_get_prerequisite_graph():
    """Verify calling get_prerequisite_graph through FastMCP."""
    res = await mcp_server.call_tool("get_prerequisite_graph", {"course_code": "CS301"})
    raw_dict = res[1]
    assert "nodes" in raw_dict["result"]
    assert "edges" in raw_dict["result"]
    assert len(raw_dict["result"]["nodes"]) >= 4
    assert len(raw_dict["result"]["edges"]) >= 3

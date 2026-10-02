import pytest
from app.mcp_server import mcp_server


@pytest.mark.asyncio
async def test_mcp_resources_listing():
    """Verify that both course_descriptions and department_directory resources are listed."""
    resources = await mcp_server.list_resources()
    names = [r.name for r in resources]
    assert "course_descriptions" in names
    assert "department_directory" in names


@pytest.mark.asyncio
async def test_mcp_read_course_descriptions():
    """Verify reading course_descriptions resource."""
    resources = await mcp_server.list_resources()
    cd_resource = next(r for r in resources if r.name == "course_descriptions")
    contents = await mcp_server.read_resource(cd_resource.uri)
    assert len(contents) > 0
    text = contents[0].content if hasattr(contents[0], "content") else str(contents[0])
    assert isinstance(text, str)
    assert len(text) > 0
    assert "[CS101]" in text
    assert "Introduction to Programming" in text


@pytest.mark.asyncio
async def test_mcp_read_department_directory():
    """Verify reading department_directory resource."""
    resources = await mcp_server.list_resources()
    dept_resource = next(r for r in resources if r.name == "department_directory")
    contents = await mcp_server.read_resource(dept_resource.uri)
    assert len(contents) > 0
    text = contents[0].content if hasattr(contents[0], "content") else str(contents[0])
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Computer Science (CS)" in text
    assert "Mathematics (MATH)" in text


@pytest.mark.asyncio
async def test_mcp_prompts_listing():
    """Verify that course_comparison_template prompt is listed."""
    prompts = await mcp_server.list_prompts()
    prompt_names = [p.name for p in prompts]
    assert "course_comparison_template" in prompt_names


@pytest.mark.asyncio
async def test_mcp_get_prompt_placeholders():
    """Verify fetching prompt template contains placeholders {{course_code_1}} and {{course_code_2}}."""
    prompt = await mcp_server.get_prompt("course_comparison_template", {})
    text = prompt.messages[0].content.text
    assert "{{course_code_1}}" in text
    assert "{{course_code_2}}" in text


@pytest.mark.asyncio
async def test_mcp_get_prompt_with_arguments():
    """Verify fetching prompt template with specific course arguments replaces placeholders."""
    prompt = await mcp_server.get_prompt(
        "course_comparison_template",
        {"course_code_1": "CS101", "course_code_2": "CS102"}
    )
    text = prompt.messages[0].content.text
    assert "CS101" in text
    assert "CS102" in text

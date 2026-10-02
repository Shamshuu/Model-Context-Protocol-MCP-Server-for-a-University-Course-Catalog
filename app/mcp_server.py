from typing import Any, Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP

from app.database import get_db
from app.schemas import (
    CourseSummary,
    PrerequisitesOutput,
    PrerequisiteCourse,
    InstructorOutput,
    PrerequisiteGraphOutput,
    GraphNode,
    GraphEdge,
    ErrorResponse,
)
from app.services import (
    search_courses_service,
    get_prerequisites_service,
    lookup_instructor_service,
    get_prerequisite_graph_service,
    get_course_descriptions_service,
    get_department_directory_service,
    get_course_comparison_template_service,
)

# Initialize FastMCP Server
mcp_server = FastMCP(
    "University Course Catalog Server",
    instructions="MCP Server providing access to a university course catalog, prerequisite dependency graphs, instructor directories, and academic planning prompts."
)


# ============================================================================
# MCP Tools
# ============================================================================

@mcp_server.tool(name="search_courses")
def search_courses(query: str, department_code: Optional[str] = None) -> List[CourseSummary]:
    """
    Searches the university course catalog for courses matching a query string.
    Can be filtered by a specific department code.

    Parameters:
        query: Keyword to search within course codes, titles, or descriptions (e.g., 'Introduction', 'Algorithms').
        department_code: Optional academic department code filter (e.g., 'CS', 'MATH', 'EE', 'PHYS').

    Returns:
        List of matching courses containing course_code, title, and credits. Returns empty list if no matches.
    """
    with get_db() as db:
        raw_results = search_courses_service(db, query=query, department_code=department_code)
        return [CourseSummary(**item) for item in raw_results]


@mcp_server.tool(name="get_prerequisites")
def get_prerequisites(course_code: str) -> Union[PrerequisitesOutput, ErrorResponse]:
    """
    Retrieves the direct prerequisites for a given course code.

    Parameters:
        course_code: The course identifier to look up (e.g., 'CS102', 'CS301').

    Returns:
        A dictionary containing the course_code and an array of direct prerequisite courses
        with course_code and title. Returns an empty prerequisites array if the course has no prerequisites.
    """
    with get_db() as db:
        res = get_prerequisites_service(db, course_code=course_code)
        if "error" in res:
            return ErrorResponse(error=res["error"])
        return PrerequisitesOutput(
            course_code=res["course_code"],
            prerequisites=[PrerequisiteCourse(**p) for p in res["prerequisites"]]
        )


@mcp_server.tool(name="lookup_instructor")
def lookup_instructor(instructor_name: str) -> Union[InstructorOutput, ErrorResponse]:
    """
    Finds an instructor's contact details and department affiliation by their name.

    Parameters:
        instructor_name: Full or partial name of the faculty member (e.g., 'Dr. Alan Turing', 'Ada Lovelace').

    Returns:
        A dictionary containing the instructor's name, email, and department_name.
        Returns a structured error dict {"error": "Instructor not found"} if no matching instructor exists.
    """
    with get_db() as db:
        res = lookup_instructor_service(db, instructor_name=instructor_name)
        if "error" in res:
            return ErrorResponse(error=res["error"])
        return InstructorOutput(**res)


@mcp_server.tool(name="get_prerequisite_graph")
def get_prerequisite_graph(course_code: str) -> Union[PrerequisiteGraphOutput, ErrorResponse]:
    """
    Builds the full multi-level prerequisite dependency graph for a course.
    Returns an adjacency list of nodes and directed edges where each source course is a prerequisite for target.

    Parameters:
        course_code: The course code to generate the dependency chain for (e.g., 'CS350', 'CS301').

    Returns:
        A graph object with 'nodes' (list of course IDs) and 'edges' (list of {source, target} pairs).
    """
    with get_db() as db:
        res = get_prerequisite_graph_service(db, course_code=course_code)
        if "error" in res:
            return ErrorResponse(error=res["error"])
        return PrerequisiteGraphOutput(
            nodes=[GraphNode(**n) for n in res["nodes"]],
            edges=[GraphEdge(**e) for e in res["edges"]]
        )


# ============================================================================
# MCP Resources
# ============================================================================

@mcp_server.resource("catalog://course_descriptions", name="course_descriptions")
def course_descriptions_resource() -> str:
    """
    Comprehensive directory of all university courses and their catalog descriptions.
    Each entry is formatted as [CODE] Title: Description.
    """
    with get_db() as db:
        return get_course_descriptions_service(db)


@mcp_server.resource("catalog://department_directory", name="department_directory")
def department_directory_resource() -> str:
    """
    Directory of all academic departments and their corresponding abbreviation codes.
    Formatted as Department Name (CODE).
    """
    with get_db() as db:
        return get_department_directory_service(db)


# ============================================================================
# MCP Prompt Templates
# ============================================================================

@mcp_server.prompt("course_comparison_template")
def course_comparison_template_prompt(
    course_code_1: str = "{{course_code_1}}",
    course_code_2: str = "{{course_code_2}}"
) -> str:
    """
    Prompt template to guide an LLM in generating a structured side-by-side comparison between two courses.
    Includes placeholders for {{course_code_1}} and {{course_code_2}}.
    """
    template = get_course_comparison_template_service()
    if course_code_1 != "{{course_code_1}}" or course_code_2 != "{{course_code_2}}":
        return template.replace("{{course_code_1}}", course_code_1).replace("{{course_code_2}}", course_code_2)
    return template

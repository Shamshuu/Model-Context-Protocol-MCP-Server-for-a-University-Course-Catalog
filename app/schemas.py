from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Tool 1: search_courses
# ---------------------------------------------------------
class SearchCoursesInput(BaseModel):
    """Input parameters for searching courses in the catalog."""
    query: str = Field(..., description="Keyword to search in course code, title, or description.")
    department_code: Optional[str] = Field(
        default=None,
        description="Optional department code filter (e.g., 'CS', 'MATH', 'EE', 'PHYS')."
    )


class CourseSummary(BaseModel):
    """Summary of a course returned by search_courses."""
    course_code: str = Field(..., description="Unique course identifier (e.g., 'CS101').")
    title: str = Field(..., description="Official title of the course.")
    credits: int = Field(..., description="Number of academic credit hours.")


# ---------------------------------------------------------
# Tool 2: get_prerequisites
# ---------------------------------------------------------
class GetPrerequisitesInput(BaseModel):
    """Input parameters for retrieving course prerequisites."""
    course_code: str = Field(..., description="The course code to look up (e.g., 'CS102').")


class PrerequisiteCourse(BaseModel):
    """Information about a direct prerequisite course."""
    course_code: str = Field(..., description="Course code of the prerequisite course.")
    title: str = Field(..., description="Title of the prerequisite course.")


class PrerequisitesOutput(BaseModel):
    """Response containing direct prerequisites for a course."""
    course_code: str = Field(..., description="The queried course code.")
    prerequisites: List[PrerequisiteCourse] = Field(
        default_factory=list,
        description="List of direct prerequisite courses."
    )


# ---------------------------------------------------------
# Tool 3: lookup_instructor
# ---------------------------------------------------------
class LookupInstructorInput(BaseModel):
    """Input parameters for finding instructor details."""
    instructor_name: str = Field(..., description="Full or partial name of the instructor to find.")


class InstructorOutput(BaseModel):
    """Instructor profile and departmental affiliation."""
    name: str = Field(..., description="Full name of the instructor.")
    email: str = Field(..., description="Official university email address.")
    department_name: str = Field(..., description="Name of the department the instructor belongs to.")


# ---------------------------------------------------------
# Tool 4: get_prerequisite_graph
# ---------------------------------------------------------
class GetPrerequisiteGraphInput(BaseModel):
    """Input parameters for building a course prerequisite dependency graph."""
    course_code: str = Field(..., description="The target course code to analyze (e.g., 'CS350').")


class GraphNode(BaseModel):
    """Node representing a course in the prerequisite graph."""
    id: str = Field(..., description="Course code identifier of the node.")


class GraphEdge(BaseModel):
    """Directed edge representing prerequisite relationship (source is prerequisite for target)."""
    source: str = Field(..., description="Prerequisite course code.")
    target: str = Field(..., description="Dependent course code that requires the source.")


class PrerequisiteGraphOutput(BaseModel):
    """Adjacency list representation of prerequisite dependencies."""
    nodes: List[GraphNode] = Field(default_factory=list, description="All course nodes involved in the dependency tree.")
    edges: List[GraphEdge] = Field(default_factory=list, description="All prerequisite directed edges (source -> target).")


# ---------------------------------------------------------
# Generic Error Response
# ---------------------------------------------------------
class ErrorResponse(BaseModel):
    """Structured error message schema."""
    error: str = Field(..., description="Human-readable error description.")

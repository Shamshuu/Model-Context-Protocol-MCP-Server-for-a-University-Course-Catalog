from typing import Any, Dict, List, Optional
import networkx as nx
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Course, Department, Instructor


def search_courses_service(
    db: Session,
    query: str,
    department_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search courses by keyword matching course code, title, or description, with optional department filter."""
    stmt = db.query(Course).join(Department)

    clean_query = query.strip() if query else ""
    if clean_query:
        search_filter = or_(
            Course.course_code.ilike(f"%{clean_query}%"),
            Course.title.ilike(f"%{clean_query}%"),
            Course.description.ilike(f"%{clean_query}%")
        )
        stmt = stmt.filter(search_filter)

    if department_code and department_code.strip():
        stmt = stmt.filter(Department.code.ilike(department_code.strip()))

    courses = stmt.order_by(Course.course_code).all()
    return [
        {
            "course_code": c.course_code,
            "title": c.title,
            "credits": c.credits
        }
        for c in courses
    ]


def get_prerequisites_service(db: Session, course_code: str) -> Dict[str, Any]:
    """Retrieve direct prerequisites for a given course code."""
    clean_code = course_code.strip()
    course = db.query(Course).filter(Course.course_code.ilike(clean_code)).first()

    if not course:
        return {"error": f"Course '{course_code}' not found"}

    prereqs = sorted(course.prerequisites, key=lambda p: p.course_code)
    return {
        "course_code": course.course_code,
        "prerequisites": [
            {
                "course_code": p.course_code,
                "title": p.title
            }
            for p in prereqs
        ]
    }


def lookup_instructor_service(db: Session, instructor_name: str) -> Dict[str, Any]:
    """Find instructor details and department name by instructor name."""
    clean_name = instructor_name.strip()
    # Check exact match first
    instructor = db.query(Instructor).join(Department).filter(
        Instructor.name.ilike(clean_name)
    ).first()

    # Fallback to substring match
    if not instructor:
        instructor = db.query(Instructor).join(Department).filter(
            Instructor.name.ilike(f"%{clean_name}%")
        ).first()

    if not instructor:
        return {"error": "Instructor not found"}

    return {
        "name": instructor.name,
        "email": instructor.email,
        "department_name": instructor.department.name
    }


def get_prerequisite_graph_service(db: Session, course_code: str) -> Dict[str, Any]:
    """Build the full prerequisite dependency graph for a target course using NetworkX."""
    clean_code = course_code.strip()
    target_course = db.query(Course).filter(Course.course_code.ilike(clean_code)).first()

    if not target_course:
        return {"error": f"Course '{course_code}' not found"}

    # Build full dependency graph of catalog
    # Source is prerequisite for target: (prereq -> course)
    all_courses = db.query(Course).all()
    g = nx.DiGraph()

    for c in all_courses:
        g.add_node(c.course_code)
        for prereq in c.prerequisites:
            g.add_edge(prereq.course_code, c.course_code)

    target_id = target_course.course_code
    # Find all predecessors (all ancestors in the directed prerequisite graph)
    ancestor_nodes = nx.ancestors(g, target_id)
    relevant_nodes = ancestor_nodes | {target_id}

    subgraph = g.subgraph(relevant_nodes)

    # Sort nodes and edges for deterministic output
    nodes = [{"id": n} for n in sorted(subgraph.nodes())]
    edges = [
        {"source": u, "target": v}
        for u, v in sorted(subgraph.edges())
    ]

    return {
        "nodes": nodes,
        "edges": edges
    }


def get_course_descriptions_service(db: Session) -> str:
    """Generate a single formatted string listing all courses and their descriptions."""
    courses = db.query(Course).order_by(Course.course_code).all()
    lines = [
        f"[{c.course_code}] {c.title}: {c.description}"
        for c in courses
    ]
    return "\n".join(lines)


def get_department_directory_service(db: Session) -> str:
    """Generate a single formatted string listing all departments and their codes."""
    departments = db.query(Department).order_by(Department.name).all()
    lines = [
        f"{d.name} ({d.code})"
        for d in departments
    ]
    return "\n".join(lines)


def get_course_comparison_template_service() -> str:
    """Return the structured prompt template for comparing two courses."""
    return (
        "Create a table comparing the following two courses: "
        "{{course_code_1}} and {{course_code_2}}. "
        "Include columns for Title, Credits, Description, and Prerequisites."
    )

from app.services import (
    search_courses_service,
    get_prerequisites_service,
    lookup_instructor_service,
    get_prerequisite_graph_service,
    get_course_descriptions_service,
    get_department_directory_service,
    get_course_comparison_template_service,
)


def test_search_courses_by_keyword(db_session):
    """Test searching courses by keyword 'Introduction'."""
    results = search_courses_service(db_session, query="Introduction")
    assert len(results) > 0
    for course in results:
        assert "course_code" in course
        assert "title" in course
        assert "credits" in course
        assert "Introduction" in course["title"] or "Introduction" in course.get("description", "")


def test_search_courses_with_department_filter(db_session):
    """Test searching courses with department filter 'CS'."""
    results = search_courses_service(db_session, query="Programming", department_code="CS")
    assert len(results) == 2
    codes = [c["course_code"] for c in results]
    assert "CS101" in codes
    assert "CS201" in codes

    # Searching with department that doesn't match should return empty
    empty_results = search_courses_service(db_session, query="Programming", department_code="PHYS")
    assert empty_results == []


def test_search_courses_non_existent(db_session):
    """Test searching with a non-existent keyword returns empty list."""
    results = search_courses_service(db_session, query="QuantumTeleportation999")
    assert results == []


def test_get_prerequisites_with_prereqs(db_session):
    """Test get_prerequisites for a course known to have prerequisites (CS102 -> CS101)."""
    res = get_prerequisites_service(db_session, course_code="CS102")
    assert "error" not in res
    assert res["course_code"] == "CS102"
    assert len(res["prerequisites"]) >= 1
    codes = [p["course_code"] for p in res["prerequisites"]]
    assert "CS101" in codes
    assert any(p["title"] == "Introduction to Programming" for p in res["prerequisites"])


def test_get_prerequisites_no_prereqs(db_session):
    """Test get_prerequisites for a course with no prerequisites (CS101)."""
    res = get_prerequisites_service(db_session, course_code="CS101")
    assert "error" not in res
    assert res["course_code"] == "CS101"
    assert res["prerequisites"] == []


def test_get_prerequisites_non_existent(db_session):
    """Test get_prerequisites for a non-existent course code returns error."""
    res = get_prerequisites_service(db_session, course_code="INVALID999")
    assert "error" in res


def test_lookup_instructor_valid(db_session):
    """Test looking up an instructor by name."""
    res = lookup_instructor_service(db_session, instructor_name="Dr. Alan Turing")
    assert "error" not in res
    assert res["name"] == "Dr. Alan Turing"
    assert res["email"] == "a.turing@university.edu"
    assert res["department_name"] == "Computer Science"


def test_lookup_instructor_partial_case_insensitive(db_session):
    """Test looking up an instructor with partial name and mixed casing."""
    res = lookup_instructor_service(db_session, instructor_name="lovelace")
    assert "error" not in res
    assert res["name"] == "Dr. Ada Lovelace"


def test_lookup_instructor_non_existent(db_session):
    """Test looking up a non-existent instructor returns structured error."""
    res = lookup_instructor_service(db_session, instructor_name="Non Existent Professor")
    assert res == {"error": "Instructor not found"}


def test_get_prerequisite_graph_multilevel(db_session):
    """Test prerequisite graph for a course with multi-level dependencies (CS350 -> CS301 -> CS201 -> CS102 -> CS101)."""
    res = get_prerequisite_graph_service(db_session, course_code="CS301")
    assert "error" not in res
    node_ids = {n["id"] for n in res["nodes"]}
    # CS301 requires CS201, which requires CS102, which requires CS101
    assert {"CS101", "CS102", "CS201", "CS301"}.issubset(node_ids)

    # Verify edges: source is prerequisite for target
    edge_pairs = {(e["source"], e["target"]) for e in res["edges"]}
    assert ("CS101", "CS102") in edge_pairs
    assert ("CS102", "CS201") in edge_pairs
    assert ("CS201", "CS301") in edge_pairs


def test_get_prerequisite_graph_no_prereqs(db_session):
    """Test prerequisite graph for a course with no prerequisites (CS101)."""
    res = get_prerequisite_graph_service(db_session, course_code="CS101")
    assert "error" not in res
    assert res["nodes"] == [{"id": "CS101"}]
    assert res["edges"] == []


def test_get_prerequisite_graph_non_existent(db_session):
    """Test prerequisite graph for non-existent course returns error."""
    res = get_prerequisite_graph_service(db_session, course_code="UNKNOWN_COURSE")
    assert "error" in res


def test_resource_and_prompt_content(db_session):
    """Test resource generation and prompt template string."""
    course_desc = get_course_descriptions_service(db_session)
    assert isinstance(course_desc, str)
    assert "[CS101]" in course_desc
    assert "Introduction to Programming" in course_desc

    dept_dir = get_department_directory_service(db_session)
    assert isinstance(dept_dir, str)
    assert "Computer Science (CS)" in dept_dir
    assert "Mathematics (MATH)" in dept_dir

    prompt = get_course_comparison_template_service()
    assert "{{course_code_1}}" in prompt
    assert "{{course_code_2}}" in prompt

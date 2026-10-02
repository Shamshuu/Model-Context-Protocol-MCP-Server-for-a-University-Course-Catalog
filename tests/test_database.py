import sqlite3
from pathlib import Path
from app.models import Department, Instructor, Course, Prerequisite
from data.seed import seed_database


def test_catalog_db_file_exists(catalog_db_path: Path):
    """Verify that data/catalog.db file exists and is non-empty."""
    assert catalog_db_path.exists(), "data/catalog.db does not exist"
    assert catalog_db_path.stat().st_size > 0, "data/catalog.db is empty"


def test_database_tables_and_columns(catalog_db_path: Path):
    """Confirm the existence and exact schema of all 4 required tables."""
    conn = sqlite3.connect(catalog_db_path)
    cursor = conn.cursor()

    # Required tables
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    for expected in ["departments", "instructors", "courses", "prerequisites"]:
        assert expected in tables, f"Missing required table: {expected}"

    # Verify departments columns
    dept_cols = {row[1] for row in cursor.execute("PRAGMA table_info(departments)").fetchall()}
    assert {"id", "name", "code"}.issubset(dept_cols)

    # Verify instructors columns
    inst_cols = {row[1] for row in cursor.execute("PRAGMA table_info(instructors)").fetchall()}
    assert {"id", "name", "email", "department_id"}.issubset(inst_cols)

    # Verify courses columns
    course_cols = {row[1] for row in cursor.execute("PRAGMA table_info(courses)").fetchall()}
    assert {"id", "course_code", "title", "description", "credits", "instructor_id", "department_id"}.issubset(course_cols)

    # Verify prerequisites columns
    prereq_cols = {row[1] for row in cursor.execute("PRAGMA table_info(prerequisites)").fetchall()}
    assert {"course_id", "prerequisite_id"}.issubset(prereq_cols)

    conn.close()


def test_seed_minimum_counts(db_session):
    """Verify minimum seed counts: >=3 departments, >=5 instructors, >=10 courses, >=3 with prerequisites."""
    dept_count = db_session.query(Department).count()
    assert dept_count >= 3, f"Expected >=3 departments, got {dept_count}"

    inst_count = db_session.query(Instructor).count()
    assert inst_count >= 5, f"Expected >=5 instructors, got {inst_count}"

    course_count = db_session.query(Course).count()
    assert course_count >= 10, f"Expected >=10 courses, got {course_count}"

    prereq_courses_count = db_session.query(Prerequisite.course_id).distinct().count()
    assert prereq_courses_count >= 3, f"Expected >=3 courses with prerequisites, got {prereq_courses_count}"


def test_seed_idempotency():
    """Verify that calling seed_database multiple times without force does not duplicate data."""
    seeded = seed_database(force=False)
    assert seeded is False, "Second seed run should have been skipped as database is already seeded"

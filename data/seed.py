import os
import sys
from pathlib import Path

# Add project root to sys.path so app imports work when executed directly
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, engine, SessionLocal
from app.models import Department, Instructor, Course, Prerequisite


def seed_database(force: bool = False) -> bool:
    """Populate the course catalog database with departments, instructors, courses, and prerequisites."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if database is already seeded
        dept_count = session.query(Department).count()
        course_count = session.query(Course).count()

        if not force and dept_count >= 3 and course_count >= 10:
            print(f"[Seed] Database already contains {dept_count} departments and {course_count} courses. Skipping seed.")
            return False

        if force:
            print("[Seed] Force mode enabled: clearing existing data...")
            session.query(Prerequisite).delete()
            session.query(Course).delete()
            session.query(Instructor).delete()
            session.query(Department).delete()
            session.commit()

        print("[Seed] Seeding academic departments...")
        cs_dept = Department(name="Computer Science", code="CS")
        math_dept = Department(name="Mathematics", code="MATH")
        ee_dept = Department(name="Electrical Engineering", code="EE")
        phys_dept = Department(name="Physics", code="PHYS")

        session.add_all([cs_dept, math_dept, ee_dept, phys_dept])
        session.flush()

        print("[Seed] Seeding faculty instructors...")
        turing = Instructor(
            name="Dr. Alan Turing",
            email="a.turing@university.edu",
            office="Turing Hall 101",
            department_id=cs_dept.id
        )
        lovelace = Instructor(
            name="Dr. Ada Lovelace",
            email="a.lovelace@university.edu",
            office="Lovelace Lab 202",
            department_id=cs_dept.id
        )
        hopper = Instructor(
            name="Dr. Grace Hopper",
            email="g.hopper@university.edu",
            office="Hopper Hall 303",
            department_id=cs_dept.id
        )
        gauss = Instructor(
            name="Dr. Carl Gauss",
            email="c.gauss@university.edu",
            office="Euler Building 104",
            department_id=math_dept.id
        )
        shannon = Instructor(
            name="Dr. Claude Shannon",
            email="c.shannon@university.edu",
            office="Shannon Wing 205",
            department_id=ee_dept.id
        )
        curie = Instructor(
            name="Dr. Marie Curie",
            email="m.curie@university.edu",
            office="Curie Complex 306",
            department_id=phys_dept.id
        )

        session.add_all([turing, lovelace, hopper, gauss, shannon, curie])
        session.flush()

        print("[Seed] Seeding university courses...")
        # Computer Science Courses
        cs101 = Course(
            course_code="CS101",
            title="Introduction to Programming",
            description="A foundational course on programming principles, problem-solving, and algorithmic thinking using Python.",
            credits=4,
            instructor_id=turing.id,
            department_id=cs_dept.id
        )
        cs102 = Course(
            course_code="CS102",
            title="Data Structures and Algorithms",
            description="Study of fundamental data structures such as lists, stacks, queues, trees, graphs, and algorithm design and analysis.",
            credits=4,
            instructor_id=lovelace.id,
            department_id=cs_dept.id
        )
        cs201 = Course(
            course_code="CS201",
            title="Systems Programming",
            description="Covers low-level programming concepts, memory management, operating system interfaces, and concurrency in C/C++.",
            credits=4,
            instructor_id=hopper.id,
            department_id=cs_dept.id
        )
        cs301 = Course(
            course_code="CS301",
            title="Operating Systems",
            description="In-depth study of operating systems design including processes, threads, CPU scheduling, synchronization, and file systems.",
            credits=4,
            instructor_id=hopper.id,
            department_id=cs_dept.id
        )
        cs350 = Course(
            course_code="CS350",
            title="Distributed Systems",
            description="Principles and paradigms of distributed computing systems, consensus protocols, fault tolerance, and cloud computing.",
            credits=3,
            instructor_id=turing.id,
            department_id=cs_dept.id
        )
        cs250 = Course(
            course_code="CS250",
            title="Theory of Computation",
            description="Automata theory, regular and context-free languages, computability, Turing machines, and complexity classes P vs NP.",
            credits=3,
            instructor_id=lovelace.id,
            department_id=cs_dept.id
        )
        cs320 = Course(
            course_code="CS320",
            title="Artificial Intelligence",
            description="Heuristic search, knowledge representation, probabilistic reasoning, machine learning foundations, and intelligent agents.",
            credits=3,
            instructor_id=turing.id,
            department_id=cs_dept.id
        )

        # Mathematics Courses
        math101 = Course(
            course_code="MATH101",
            title="Introduction to Calculus",
            description="Differential and integral calculus of single-variable functions with applications to science and engineering.",
            credits=4,
            instructor_id=gauss.id,
            department_id=math_dept.id
        )
        math201 = Course(
            course_code="MATH201",
            title="Linear Algebra",
            description="Vector spaces, linear transformations, matrices, determinants, eigenvalues, eigenvectors, and inner product spaces.",
            credits=3,
            instructor_id=gauss.id,
            department_id=math_dept.id
        )
        math202 = Course(
            course_code="MATH202",
            title="Discrete Mathematics",
            description="Sets, relations, functions, propositional and predicate logic, combinatorics, and graph theory for computing.",
            credits=3,
            instructor_id=gauss.id,
            department_id=math_dept.id
        )

        # Electrical Engineering Courses
        ee101 = Course(
            course_code="EE101",
            title="Introduction to Digital Logic",
            description="Boolean algebra, combinational and sequential circuit analysis and design, flip-flops, counters, and registers.",
            credits=4,
            instructor_id=shannon.id,
            department_id=ee_dept.id
        )
        ee201 = Course(
            course_code="EE201",
            title="Computer Architecture",
            description="Instruction set architectures, processor pipelining, memory hierarchy, cache design, and hardware-software interface.",
            credits=4,
            instructor_id=shannon.id,
            department_id=ee_dept.id
        )

        # Physics Courses
        phys101 = Course(
            course_code="PHYS101",
            title="General Physics I",
            description="Classical mechanics, Newtonian dynamics, work and energy, conservation laws, oscillations, and wave mechanics.",
            credits=4,
            instructor_id=curie.id,
            department_id=phys_dept.id
        )
        phys102 = Course(
            course_code="PHYS102",
            title="General Physics II",
            description="Electricity and magnetism, Coulomb's law, electric fields, magnetic circuits, electromagnetic induction, and optics.",
            credits=4,
            instructor_id=curie.id,
            department_id=phys_dept.id
        )

        session.add_all([
            cs101, cs102, cs201, cs301, cs350, cs250, cs320,
            math101, math201, math202,
            ee101, ee201,
            phys101, phys102
        ])
        session.flush()

        print("[Seed] Seeding course prerequisite dependencies...")
        # Prerequisites: course_id requires prerequisite_id
        # Multi-level chain: CS101 -> CS102 -> CS201 -> CS301 -> CS350
        prereqs = [
            Prerequisite(course_id=cs102.id, prerequisite_id=cs101.id),
            Prerequisite(course_id=cs201.id, prerequisite_id=cs102.id),
            Prerequisite(course_id=cs301.id, prerequisite_id=cs201.id),
            Prerequisite(course_id=cs350.id, prerequisite_id=cs301.id),
            # CS250 requires CS102 and MATH202
            Prerequisite(course_id=cs250.id, prerequisite_id=cs102.id),
            Prerequisite(course_id=cs250.id, prerequisite_id=math202.id),
            # CS320 requires CS102 and MATH201
            Prerequisite(course_id=cs320.id, prerequisite_id=cs102.id),
            Prerequisite(course_id=cs320.id, prerequisite_id=math201.id),
            # Math prerequisites
            Prerequisite(course_id=math201.id, prerequisite_id=math101.id),
            Prerequisite(course_id=math202.id, prerequisite_id=math101.id),
            # EE201 requires EE101 and CS101
            Prerequisite(course_id=ee201.id, prerequisite_id=ee101.id),
            Prerequisite(course_id=ee201.id, prerequisite_id=cs101.id),
            # PHYS102 requires PHYS101 and MATH101
            Prerequisite(course_id=phys102.id, prerequisite_id=phys101.id),
            Prerequisite(course_id=phys102.id, prerequisite_id=math101.id),
        ]

        session.add_all(prereqs)
        session.commit()
        print(f"[Seed] Successfully seeded {session.query(Department).count()} departments, "
              f"{session.query(Instructor).count()} instructors, {session.query(Course).count()} courses, "
              f"and {session.query(Prerequisite).count()} prerequisite mappings.")
        return True
    except Exception as e:
        session.rollback()
        print(f"[Seed] Error during seeding: {e}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    force_seed = "--force" in sys.argv
    seed_database(force=force_seed)

import psycopg2

# Database connection parameters
conn_params = {
    'dbname': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'port': 5432
}

# SQL statements to create triggers and functions
triggers_sql = """

-- ============================
-- 1. LAB_MEMBER: MENTOR MUST BE FACULTY
-- ============================
CREATE OR REPLACE FUNCTION check_mentor_faculty()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mentor_mid IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM lab_member
            WHERE mid = NEW.mentor_mid
              AND member_type = 'Faculty'
        ) THEN
            RAISE EXCEPTION 'Mentor % must be a Faculty member.', NEW.mentor_mid;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_mentor_faculty ON lab_member;
CREATE TRIGGER trg_check_mentor_faculty
BEFORE INSERT OR UPDATE ON lab_member
FOR EACH ROW
EXECUTE FUNCTION check_mentor_faculty();

-- ============================
-- 2. STUDENT / FACULTY / COLLABORATOR: enforce subtype consistency
-- ============================

-- STUDENT
CREATE OR REPLACE FUNCTION check_student_type()
RETURNS TRIGGER AS $$
DECLARE memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType FROM lab_member WHERE mid = NEW.mid;
    IF memberType IS NULL THEN
        RAISE EXCEPTION 'Member % does not exist in LAB_MEMBER.', NEW.mid;
    ELSIF memberType <> 'Student' THEN
        RAISE EXCEPTION 'Member % is not of type Student in LAB_MEMBER.', NEW.mid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_student_type ON student;
CREATE TRIGGER trg_check_student_type
BEFORE INSERT OR UPDATE ON student
FOR EACH ROW
EXECUTE FUNCTION check_student_type();

-- FACULTY
CREATE OR REPLACE FUNCTION check_faculty_type()
RETURNS TRIGGER AS $$
DECLARE memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType FROM lab_member WHERE mid = NEW.mid;
    IF memberType IS NULL THEN
        RAISE EXCEPTION 'Member % does not exist in LAB_MEMBER.', NEW.mid;
    ELSIF memberType <> 'Faculty' THEN
        RAISE EXCEPTION 'Member % is not of type Faculty in LAB_MEMBER.', NEW.mid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_faculty_type ON faculty;
CREATE TRIGGER trg_check_faculty_type
BEFORE INSERT OR UPDATE ON faculty
FOR EACH ROW
EXECUTE FUNCTION check_faculty_type();

-- COLLABORATOR
CREATE OR REPLACE FUNCTION check_collaborator_type()
RETURNS TRIGGER AS $$
DECLARE memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType FROM lab_member WHERE mid = NEW.mid;
    IF memberType IS NULL THEN
        RAISE EXCEPTION 'Member % does not exist in LAB_MEMBER.', NEW.mid;
    ELSIF memberType <> 'Collaborator' THEN
        RAISE EXCEPTION 'Member % is not of type Collaborator in LAB_MEMBER.', NEW.mid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_collaborator_type ON collaborator;
CREATE TRIGGER trg_check_collaborator_type
BEFORE INSERT OR UPDATE ON collaborator
FOR EACH ROW
EXECUTE FUNCTION check_collaborator_type();

-- ============================
-- 3. PROJECT: FACULTYID MUST BE FACULTY
-- ============================
CREATE OR REPLACE FUNCTION check_project_faculty_type()
RETURNS TRIGGER AS $$
DECLARE memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType FROM lab_member WHERE mid = NEW.facultyid;
    IF memberType IS NULL THEN
        RAISE EXCEPTION 'FACULTYID % does not exist in LAB_MEMBER.', NEW.facultyid;
    ELSIF memberType <> 'Faculty' THEN
        RAISE EXCEPTION 'FACULTYID % is not of type Faculty in LAB_MEMBER.', NEW.facultyid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_project_faculty_type ON project;
CREATE TRIGGER trg_check_project_faculty_type
BEFORE INSERT OR UPDATE ON project
FOR EACH ROW
EXECUTE FUNCTION check_project_faculty_type();

-- ============================
-- 4. WORKS: WEEKLY HOURS ≤ 40
-- ============================
CREATE OR REPLACE FUNCTION check_member_week_hours()
RETURNS TRIGGER AS $$
DECLARE total_hours INT;
BEGIN
    SELECT COALESCE(SUM(hours),0) INTO total_hours
    FROM works
    WHERE mid = NEW.mid
      AND week = NEW.week
      AND (pid, mid) <> (NEW.pid, NEW.mid);
    IF total_hours + NEW.hours > 40 THEN
        RAISE EXCEPTION 'Total hours for member % in week % would be %, exceeding 40.', NEW.mid, NEW.week, total_hours + NEW.hours;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_member_week_hours ON works;
CREATE TRIGGER trg_check_member_week_hours
BEFORE INSERT OR UPDATE ON works
FOR EACH ROW
EXECUTE FUNCTION check_member_week_hours();

"""

# Connect to the database and execute triggers
try:
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    cursor.execute(triggers_sql)
    conn.commit()
    print("Triggers and constraints created successfully.")
except Exception as e:
    print("Error:", e)
finally:
    cursor.close()
    conn.close()

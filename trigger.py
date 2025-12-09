 #correct to this:
MEMBER_TYPE CHAR(20) NOT NULL DEFAULT 'MEMBER'


ALTER TABLE lab_member
ADD CONSTRAINT chk_member_type
CHECK (member_type IN ('Student', 'Faculty', 'Collaborator'));

ALTER TABLE lab_member
ADD CONSTRAINT chk_join_date
CHECK (join_date <= CURRENT_DATE);

ALTER TABLE student
ADD CONSTRAINT fk_student_mid
FOREIGN KEY (mid) REFERENCES lab_member(mid)
ON DELETE CASCADE;

ALTER TABLE student
ADD CONSTRAINT chk_student_type
CHECK (
    (SELECT member_type FROM lab_member WHERE lab_member.mid = student.mid) = 'Student'
);

ALTER TABLE faculty
ADD CONSTRAINT fk_faculty_mid
FOREIGN KEY (mid) REFERENCES lab_member(mid)
ON DELETE CASCADE;

ALTER TABLE faculty
ADD CONSTRAINT chk_faculty_type
CHECK (
    (SELECT member_type FROM lab_member WHERE lab_member.mid = faculty.mid) = 'Faculty'
);

ALTER TABLE collaborator
ADD CONSTRAINT fk_collab_mid
FOREIGN KEY (mid) REFERENCES lab_member(mid)
ON DELETE CASCADE;

ALTER TABLE collaborator
ADD CONSTRAINT chk_collab_type
CHECK (
    (SELECT member_type FROM lab_member WHERE lab_member.mid = collaborator.mid) = 'Collaborator'
);

CREATE OR REPLACE FUNCTION check_mentor_faculty()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mentor_mid IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM lab_member
            WHERE mid = NEW.mentor_mid
            AND member_type = 'Faculty'
        ) THEN
            RAISE EXCEPTION 'Mentor must be a Faculty member.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_mentor_faculty
BEFORE INSERT OR UPDATE ON lab_member
FOR EACH ROW
EXECUTE FUNCTION check_mentor_faculty();

ALTER TABLE lab_member
ADD CONSTRAINT chk_no_self_mentor
CHECK (mid <> mentor_mid);

ALTER TABLE student
ADD CONSTRAINT fk_student_mid
FOREIGN KEY (mid)
REFERENCES lab_member(mid)
ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION check_student_type()
RETURNS TRIGGER AS $$
DECLARE
    memberType VARCHAR(20);
BEGIN
    -- Get the type from LAB_MEMBER
    SELECT member_type INTO memberType
    FROM lab_member
    WHERE mid = NEW.mid;

    IF memberType <> 'Student' THEN
        RAISE EXCEPTION 'Member % is not a Student in LAB_MEMBER.', NEW.mid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_student_type
BEFORE INSERT OR UPDATE ON student
FOR EACH ROW
EXECUTE FUNCTION check_student_type();

ALTER TABLE faculty
ADD CONSTRAINT fk_faculty_mid
FOREIGN KEY (mid)
REFERENCES lab_member(mid)
ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION check_faculty_type()
RETURNS TRIGGER AS $$
DECLARE
    memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType
    FROM lab_member
    WHERE mid = NEW.mid;

    IF memberType <> 'Faculty' THEN
        RAISE EXCEPTION 'Member % is not a Faculty in LAB_MEMBER.', NEW.mid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_faculty_type
BEFORE INSERT OR UPDATE ON faculty
FOR EACH ROW
EXECUTE FUNCTION check_faculty_type();

ALTER TABLE collaborator
ADD CONSTRAINT fk_collaborator_mid
FOREIGN KEY (mid)
REFERENCES lab_member(mid)
ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION check_collaborator_type()
RETURNS TRIGGER AS $$
DECLARE
    memberType VARCHAR(20);
BEGIN
    SELECT member_type INTO memberType
    FROM lab_member
    WHERE mid = NEW.mid;

    IF memberType <> 'Collaborator' THEN
        RAISE EXCEPTION 'Member % is not a Collaborator in LAB_MEMBER.', NEW.mid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_collaborator_type
BEFORE INSERT OR UPDATE ON collaborator
FOR EACH ROW
EXECUTE FUNCTION check_collaborator_type();
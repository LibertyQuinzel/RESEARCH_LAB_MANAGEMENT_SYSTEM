import psycopg2
from datetime import date, timedelta


def get_connection():
    return psycopg2.connect(
        database="mydatabase",   
        user="myuser",           
        password="mypassword",   
        host="localhost",
        port=5432
    )


def main():
    conn = get_connection()
    cur = conn.cursor()
    print("Connected to PostgreSQL for inserts.")

    # ---------- FACULTY LAB_MEMBER + FACULTY (30) ----------
    base = date(2019, 1, 1)
    # Ensure lab_member rows for faculty exist before creating other members who may reference them as mentors
    for i in range(1, 31):
        mid = f'F{i:03}'
        name = f'Faculty {i}'.upper()
        member_type = 'Faculty'
        join_date = base + timedelta(days=i * 30)
        cur.execute(
            "INSERT INTO LAB_MEMBER (MID, NAME, MEMBER_TYPE, JOIN_DATE, MENTOR_MID) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;",
            (mid, name, member_type, join_date, None)
        )
        cur.execute("INSERT INTO FACULTY (MID, DEPARTMENT) VALUES (%s,%s) ON CONFLICT (MID) DO NOTHING;", (mid, 'BIOLOGY'))

    # ---------- LAB_MEMBER (30) ----------
    lab_members = []
    # MEMBER_TYPE must match the CHECK constraint in LAB_MEMBER (case-sensitive)
    types = ['Student', 'Faculty', 'Collaborator']
    for i in range(1, 31):
        mid = f'M{i:03}'
        name = f'Member {i}'.upper()
        # cycle types starting with 'Student' for i=1
        member_type = types[(i-1) % 3]
        join_date = base + timedelta(days=i * 30)
        # assign a faculty mentor for members after the first few
        mentor_mid = f'F{((i-1)%30)+1:03}' if i > 2 else None
        lab_members.append((mid, name, member_type, join_date, mentor_mid))
        cur.execute(
            "INSERT INTO LAB_MEMBER (MID, NAME, MEMBER_TYPE, JOIN_DATE, MENTOR_MID) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;",
            (mid, name, member_type, join_date, mentor_mid)
        )

    # ---------- STUDENT (30) ----------
    majors = ['BIOLOGY', 'CS', 'PHYSICS', 'CHEMISTRY']
    student_counter = 1
    for m in lab_members:
        mid = m[0]
        member_type = m[2]
        if member_type != 'Student':
            continue
        sid = f'S{student_counter:04}'
        level = ('UNDERGRADUATE' if student_counter % 2 == 0 else 'GRADUATE')
        major = majors[student_counter % len(majors)]
        cur.execute("INSERT INTO STUDENT (MID,SID,LEVEL,MAJOR) VALUES (%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;", (mid, sid.upper(), level, major))
        student_counter += 1

    # Keep a list of student MIDs for linking publications to students below.
    student_mids = [m[0] for m in lab_members if m[2] == 'Student']

    # ---------- COLLABORATOR (30) ----------
    # Ensure lab_member rows for collaborators exist before inserting into COLLABORATOR
    for i in range(1, 31):
        mid = f'C{i:03}'
        name = f'Collaborator {i}'.upper()
        member_type = 'Collaborator'
        join_date = base + timedelta(days=i * 30)
        cur.execute(
            "INSERT INTO LAB_MEMBER (MID, NAME, MEMBER_TYPE, JOIN_DATE, MENTOR_MID) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;",
            (mid, name, member_type, join_date, None)
        )
        bio = f'Collaborator bio {i}'.upper()
        aff = f'Affiliation {i}'.upper()
        cur.execute("INSERT INTO COLLABORATOR (MID, BIOGRAPHY, AFFILIATION) VALUES (%s,%s,%s) ON CONFLICT (MID) DO NOTHING;", (mid, bio, aff))

    # ---------- PUBLICATION (30) ----------
    for i in range(1, 31):
        pid = f'PUB{i:03}'
        venue = f'Journal {i}'.upper()
        title = f'Publication Title {i}'.upper()
        pub_date = date(2020, 1, 1) + timedelta(days=i * 45)
        doi = f'DOI-{i:03}'.upper()
        cur.execute("INSERT INTO PUBLICATION (PUBLICATIONID, VENUE, TITLE, PUBLICATION_DATE, DOI) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (PUBLICATIONID) DO NOTHING;", (pid, venue, title, pub_date, doi))

    # ---------- GRANTS (30) ----------
    for i in range(1, 31):
        gid = f'G{i:03}'
        source = f'Agency {i}'.upper()
        budget = 100000.00 + i * 1000
        start = date(2019, 6, 1) + timedelta(days=i * 30)
        duration = 12 + (i % 36)
        cur.execute("INSERT INTO GRANTS (GID,SOURCE,BUDGET,START_DATE,DURATION) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (GID) DO NOTHING;", (gid, source, budget, start, duration))

    # ---------- PROJECT (30) ----------
    for i in range(1, 31):
        pid = f'PR{i:03}'
        title = f'Project {i}'.upper()
        start_date = date(2020, 1, 1) + timedelta(days=i * 20)
        end_date = start_date + timedelta(days=180 + (i * 10))
        exp_duration = (end_date - start_date).days // 30
        faculty_id = f'F{((i-1)%30)+1:03}'
        cur.execute("INSERT INTO PROJECT (PID,TITLE,START_DATE,END_DATE,EXP_DURATION,FACULTYID) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (PID) DO NOTHING;",
                    (pid, title, start_date, end_date, exp_duration, faculty_id))

    # ---------- EQUIPMENT (30) ----------
    types = ["Microscope","Centrifuge","PCR Machine","Imaging System","Computer","Sensor"]
    # STATUS must match check constraint in EQUIPMENT (case-sensitive)
    statuses = ["Available","In Use","Under Maintenance","Retired"]
    # Keep track of equipment status for later USES seeding so we can create
    # an open usage row when equipment is 'In Use'.
    equipment_status = {}
    for i in range(1, 31):
        eid = f'E{i:03}'
        name = f'Equipment {i}'.upper()
        typ = types[i % len(types)]
        status = statuses[i % len(statuses)]
        pur_date = date(2018, 1, 1) + timedelta(days=i * 60)
        cur.execute("INSERT INTO EQUIPMENT (EID,NAME,TYPE,STATUS,PUR_DATE) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (EID) DO NOTHING;",
                    (eid, name, typ, status, pur_date))
        equipment_status[eid] = status

    # ---------- USES (30) ----------
    for i in range(1, 31):
        eid = f'E{((i-1)%30)+1:03}'
        mid = lab_members[(i-1) % len(lab_members)][0]
        purpose = f'Purpose {i}'.upper()
        # If the equipment is currently 'In Use' create an open usage row
        # (END_DATE = NULL, START_DATE = today). Otherwise create a
        # historical usage with a start and end date as before.
        if equipment_status.get(eid) == 'In Use':
            start_date = date.today()
            end_date = None
        else:
            start_date = date(2021, 1, 1) + timedelta(days=i * 5)
            end_date = start_date + timedelta(days=1 + (i % 10))

        cur.execute("INSERT INTO USES (EID,MID,PURPOSE,START_DATE,END_DATE) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (EID,MID,START_DATE) DO NOTHING;",
                    (eid, mid, purpose, start_date, end_date))

    # ---------- FUNDS (30) ----------
    for i in range(1, 31):
        gid = f'G{((i-1)%30)+1:03}'
        pid = f'PR{((i-1)%30)+1:03}'
        cur.execute("INSERT INTO FUNDS (GID,PID) VALUES (%s,%s) ON CONFLICT (GID,PID) DO NOTHING;", (gid, pid))

    # ---------- WORKS (30) ----------
    roles = ["RESEARCH ASSISTANT","LEAD PI","CO-PI","ANALYST","DEVELOPER","TECHNICIAN"]
    # For richer test data, assign multiple members to each project
    for i in range(1, 31):
        pid = f'PR{((i-1)%30)+1:03}'
        # attach 2-3 distinct members to each project
        mids_for_project = [lab_members[(i*2-1) % len(lab_members)][0], lab_members[(i*3-1) % len(lab_members)][0]]
        if i % 5 == 0:
            # occasionally add a third contributor
            mids_for_project.append(lab_members[(i*5-1) % len(lab_members)][0])
        for idx, mid in enumerate(mids_for_project):
            week = ((i + idx) % 52) + 1
            role = roles[(i + idx) % len(roles)]
            hours = 5 + ((i + idx) % 36)
            cur.execute("INSERT INTO WORKS (PID,MID,WEEK,ROLE,HOURS) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (PID,MID,WEEK) DO NOTHING;",
                        (pid, mid, week, role, hours))

    # ---------- PUBLISHED (30) ----------
    # Ensure publications are associated with STUDENTs so average per-major
    # metrics are non-zero. If no students exist, fall back to any lab_member.
    fallback_mids = [m[0] for m in lab_members]
    mids_source = student_mids if student_mids else fallback_mids
    for i in range(1, 31):
        pubid = f'PUB{((i-1)%30)+1:03}'
        # pick a student MID (or fallback) to link the publication to a student
        mid = mids_source[(i*3-1) % len(mids_source)]
        cur.execute("INSERT INTO PUBLISHED (PUBLICATIONID,MID) VALUES (%s,%s) ON CONFLICT (PUBLICATIONID,MID) DO NOTHING;",
                    (pubid, mid))

    # ---------- ADD MENTOR WORKS ----------
    # For every works row where the member has a mentor, ensure the mentor
    # also has a works entry for the same project with role 'MENTOR' and 0 hours.
    try:
        cur.execute("""
            SELECT DISTINCT w.pid, w.mid AS mentee_mid, lm.mentor_mid
            FROM works w
            JOIN lab_member lm ON lm.mid = w.mid
            WHERE lm.mentor_mid IS NOT NULL
        """)
        mentor_rows = cur.fetchall()
        inserted_mentors = 0
        for pid, mentee_mid, mentor_mid in mentor_rows:
            if mentor_mid is None:
                continue
            cur.execute("SELECT 1 FROM works WHERE pid=%s AND mid=%s LIMIT 1;", (pid, mentor_mid))
            if cur.fetchone():
                continue
            # Determine a week value that doesn't conflict for this mentor+pid
            cur.execute("SELECT COALESCE(MAX(week),0) + 1 FROM works WHERE pid=%s AND mid=%s;", (pid, mentor_mid))
            week = cur.fetchone()[0] or 1
            try:
                # use a savepoint so a failure inserting one mentor doesn't roll back all seed data
                cur.execute("SAVEPOINT sp_insert_mentor")
                cur.execute(
                    "INSERT INTO works (PID,MID,WEEK,ROLE,HOURS) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (PID,MID,WEEK) DO NOTHING;",
                    (pid, mentor_mid, week, 'MENTOR', 0)
                )
                cur.execute("RELEASE SAVEPOINT sp_insert_mentor")
                inserted_mentors += 1
            except Exception as e:
                # rollback just the savepoint and continue
                try:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_insert_mentor")
                except Exception:
                    pass
                print(f"Failed inserting mentor {mentor_mid} for project {pid}: {e}")
    except Exception as e:
        print(f"Failed to add mentor works: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print("Inserted 30 rows into each table (where applicable).")


if __name__ == "__main__":
    main()

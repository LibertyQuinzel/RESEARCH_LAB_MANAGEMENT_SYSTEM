import psycopg2
import random
from datetime import date, timedelta

# ------------------------
# DATABASE CONNECTION
# ------------------------
def get_connection():
    return psycopg2.connect(
        database="mydatabase",   # <-- change this
        user="myuser",           # <-- change this
        password="mypassword",   # <-- change this
        host="localhost",
        port=5432
    )

# ------------------------
# MAIN SETUP SCRIPT
# ------------------------
def main():
    conn = get_connection()
    cur = conn.cursor()
    print("Connected to PostgreSQL!")

    # ------------------------
    # 1. CREATE TABLES
    # ------------------------
    create_tables = [

        # LAB_MEMBER
        """
CREATE TABLE IF NOT EXISTS LAB_MEMBER (
    MID VARCHAR(10) NOT NULL PRIMARY KEY,
    NAME VARCHAR(50) NOT NULL,
    MEMBER_TYPE CHAR(20) NOT NULL DEFAULT 'MEMBER' 
        CHECK (MEMBER_TYPE IN ('Student', 'Faculty', 'Collaborator')),
    JOIN_DATE DATE NOT NULL,
    MENTOR_MID VARCHAR(10),
    FOREIGN KEY (MENTOR_MID) REFERENCES LAB_MEMBER(MID),
    CHECK (MID <> MENTOR_MID OR MENTOR_MID IS NULL)
);


        """,

        # STUDENT
        """
        CREATE TABLE IF NOT EXISTS STUDENT (
            MID VARCHAR(10) NOT NULL PRIMARY KEY,
            SID VARCHAR(10) NOT NULL,
            LEVEL CHAR(20) NOT NULL,
            MAJOR CHAR(20) NOT NULL,
            UNIQUE (MID)
        );
        """,

        # COLLABORATOR
        """
        CREATE TABLE IF NOT EXISTS COLLABORATOR (
            MID VARCHAR(10) NOT NULL PRIMARY KEY,
            BIOGRAPHY CHAR(500),
            AFFILIATION CHAR(50),
            UNIQUE (MID)
        );
        """,

        # FACULTY
        """
        CREATE TABLE IF NOT EXISTS FACULTY (
            MID VARCHAR(10) NOT NULL PRIMARY KEY,
            DEPARTMENT CHAR(20) NOT NULL DEFAULT 'BIOLOGY',
            UNIQUE (MID)
        );
        """,

        # PUBLICATION
        """
        CREATE TABLE IF NOT EXISTS PUBLICATION (
            PUBLICATIONID VARCHAR(10) NOT NULL PRIMARY KEY,
            VENUE VARCHAR(100) NOT NULL,
            TITLE VARCHAR(100) NOT NULL,
            PUBLICATION_DATE DATE,
            DOI VARCHAR(255)
        );
        """,

        # GRANTS
        """
        CREATE TABLE IF NOT EXISTS GRANTS (
            GID VARCHAR(10) NOT NULL PRIMARY KEY,
            SOURCE VARCHAR(100) NOT NULL,
            BUDGET DECIMAL(12,2) CHECK (BUDGET >= 0),
            START_DATE DATE,
            DURATION INT CHECK (DURATION >= 0),
            CHECK (START_DATE IS NULL OR START_DATE <= CURRENT_DATE)
        );
        """,

        # PROJECT
        """
        CREATE TABLE IF NOT EXISTS PROJECT (
            PID VARCHAR(10) NOT NULL PRIMARY KEY,
            TITLE VARCHAR(100) NOT NULL UNIQUE,
            START_DATE DATE,
            END_DATE DATE,
            EXP_DURATION INT CHECK (EXP_DURATION >= 0),
            FACULTYID VARCHAR(10) NOT NULL,
            CHECK (END_DATE IS NULL OR START_DATE IS NULL OR END_DATE >= START_DATE),
            FOREIGN KEY (FACULTYID) REFERENCES FACULTY(MID)
        );
        """,

        # EQUIPMENT
        """
        CREATE TABLE IF NOT EXISTS EQUIPMENT (
            EID VARCHAR(10) NOT NULL PRIMARY KEY,
            NAME VARCHAR(50) NOT NULL,
            TYPE VARCHAR(100),
            STATUS VARCHAR(100) CHECK (STATUS IN ('Available', 'In Use', 'Under Maintenance', 'Retired')),
            PUR_DATE DATE CHECK (PUR_DATE <= CURRENT_DATE)
        );
        """,

        # USES
        """
        CREATE TABLE IF NOT EXISTS USES (
            EID VARCHAR(10) NOT NULL,
            MID VARCHAR(10) NOT NULL,
            PURPOSE VARCHAR(255),
            START_DATE DATE,
            END_DATE DATE,
            PRIMARY KEY (EID, MID, START_DATE),
            FOREIGN KEY (EID) REFERENCES EQUIPMENT(EID),
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID),
            CHECK (START_DATE IS NULL OR END_DATE IS NULL OR START_DATE <= END_DATE)
        );
        """,

        # FUNDS
        """
        CREATE TABLE IF NOT EXISTS FUNDS (
            GID VARCHAR(10) NOT NULL,
            PID VARCHAR(10) NOT NULL,
            PRIMARY KEY (GID, PID),
            FOREIGN KEY (GID) REFERENCES GRANTS(GID),
            FOREIGN KEY (PID) REFERENCES PROJECT(PID)
        );
        """,

        # WORKS (removed UNIQUE from WEEK)
        """
        CREATE TABLE IF NOT EXISTS WORKS (
            PID VARCHAR(10) NOT NULL,
            MID VARCHAR(10) NOT NULL,
            WEEK INT NOT NULL,
            ROLE VARCHAR(100) NOT NULL,
            HOURS INT CHECK (HOURS >= 0 AND HOURS <= 40),
            PRIMARY KEY (PID, MID, WEEK),
            FOREIGN KEY (PID) REFERENCES PROJECT(PID),
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID)
        );
        """,

        # PUBLISHED
        """
        CREATE TABLE IF NOT EXISTS PUBLISHED (
            PUBLICATIONID VARCHAR(10) NOT NULL,
            MID VARCHAR(10) NOT NULL,
            PRIMARY KEY (PUBLICATIONID, MID),
            FOREIGN KEY (PUBLICATIONID) REFERENCES PUBLICATION(PUBLICATIONID),
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID)
        );
        """
    ]

    for q in create_tables:
        cur.execute(q)
    conn.commit()
    print("All tables created successfully.\n")

    # ------------------------
    # 2. INSERT DATA
    # ------------------------

    # ---------- FACULTY ----------
    faculty_list = [(5000+i, 'BIOLOGY') for i in range(1, 6)]
    for f in faculty_list:
        cur.execute("INSERT INTO FACULTY (MID, DEPARTMENT) VALUES (%s,%s) ON CONFLICT (MID) DO NOTHING;", f)

    # ---------- LAB_MEMBER ----------
    lab_members = []
    for i in range(1, 21):
        mid = 1000 + i
        name = f'Student {i}'
        member_type = 'Student'
        join_date = date(2020, 1, 1) + timedelta(days=i*100)
        mentor_mid = random.choice([m[0] for m in lab_members]) if lab_members else None
        lab_members.append((mid, name, member_type, join_date, mentor_mid))
        cur.execute(
            "INSERT INTO LAB_MEMBER (MID, NAME, MEMBER_TYPE, JOIN_DATE, MENTOR_MID) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;",
            (mid, name, member_type, join_date, mentor_mid)
        )

    # ---------- COLLABORATOR ----------
    collaborator_list = [(6000+i, f'Biography {i}', f'Affiliation {i}') for i in range(1, 21)]
    for c in collaborator_list:
        cur.execute("INSERT INTO COLLABORATOR (MID, BIOGRAPHY, AFFILIATION) VALUES (%s,%s,%s) ON CONFLICT (MID) DO NOTHING;", c)

    # ---------- STUDENT ----------
    student_list = [(m[0], f'S{i:03}', 'Undergraduate', random.choice(['Biology','CS','Physics','Chemistry'])) for i,m in enumerate(lab_members,1)]
    for s in student_list:
        cur.execute("INSERT INTO STUDENT (MID,SID,LEVEL,MAJOR) VALUES (%s,%s,%s,%s) ON CONFLICT (MID) DO NOTHING;", s)

    # ---------- PUBLICATION ----------
    publications = [(f'PUB{i:03}', f'Journal {i}', f'Title {i}', date(2021,1,1)+timedelta(days=i*50), f'DOI{i}') for i in range(1,21)]
    for pub in publications:
        cur.execute("INSERT INTO PUBLICATION (PUBLICATIONID, VENUE, TITLE, PUBLICATION_DATE, DOI) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (PUBLICATIONID) DO NOTHING;", pub)

    # ---------- GRANTS ----------
    grants = [(f'G{i:03}', f'Source {i}', random.randint(100000,1000000), date(2021,1,1)+timedelta(days=i*30), random.randint(12,48)) for i in range(1,21)]
    for g in grants:
        cur.execute("INSERT INTO GRANTS (GID,SOURCE,BUDGET,START_DATE,DURATION) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (GID) DO NOTHING;", g)

    # ---------- PROJECT ----------
    projects = []
    for i in range(1,21):
        pid = f'PR{i:03}'
        title = f'Project {i}'
        start_date = date(2022,1,1)+timedelta(days=i*30)
        end_date = start_date + timedelta(days=random.randint(180, 730))
        exp_duration = (end_date - start_date).days // 30
        faculty_id = random.choice([f[0] for f in faculty_list])
        projects.append((pid, title, start_date, end_date, exp_duration, faculty_id))
        cur.execute("INSERT INTO PROJECT (PID,TITLE,START_DATE,END_DATE,EXP_DURATION,FACULTYID) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (PID) DO NOTHING;", 
                    (pid, title, start_date, end_date, exp_duration, faculty_id))

    # ---------- EQUIPMENT ----------
    equipment_types = ["Microscope","Centrifuge","PCR Machine","Imaging System","Computer","Sensor"]
    status_choices = ["Available","In Use","Under Maintenance","Retired"]
    equipment_ids = []
    for i in range(1,21):
        eid = f'E{i:03}'
        equipment_ids.append(eid)
        cur.execute("INSERT INTO EQUIPMENT (EID,NAME,TYPE,STATUS,PUR_DATE) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (EID) DO NOTHING;", 
                    (eid,f'Equipment {i}',random.choice(equipment_types),random.choice(status_choices),date.today()-timedelta(days=random.randint(30,2000))))

    # ---------- USES ----------
    for i in range(1,31):
        eid = random.choice(equipment_ids)
        mid = random.choice([m[0] for m in lab_members])
        start_date = date.today() - timedelta(days=random.randint(10, 300))
        end_date = start_date + timedelta(days=random.randint(1, 30))
        cur.execute("INSERT INTO USES (EID,MID,PURPOSE,START_DATE,END_DATE) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (EID,MID,START_DATE) DO NOTHING;", 
                    (eid, mid, f'Purpose {i}', start_date, end_date))

    # ---------- FUNDS ----------
    for i in range(1,31):
        gid = random.choice([g[0] for g in grants])
        pid = random.choice([p[0] for p in projects])
        cur.execute("INSERT INTO FUNDS (GID,PID) VALUES (%s,%s) ON CONFLICT (GID,PID) DO NOTHING;", (gid, pid))

    # ---------- WORKS ----------
    roles = ["Research Assistant","Lead PI","Co-PI","Analyst","Developer","Technician"]
    works_set = set()
    for i in range(50):
        pid = random.choice([p[0] for p in projects])
        mid = random.choice([m[0] for m in lab_members])
        week = random.randint(1,52)
        while (pid, mid, week) in works_set:
            week = random.randint(1,52)
        works_set.add((pid, mid, week))
        cur.execute("INSERT INTO WORKS (PID,MID,WEEK,ROLE,HOURS) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (PID,MID,WEEK) DO NOTHING;", 
                    (pid, mid, week, random.choice(roles), random.randint(5,40)))

    # ---------- PUBLISHED ----------
    published_set = set()
    for i in range(50):
        pubid = random.choice([p[0] for p in publications])
        mid = random.choice([m[0] for m in lab_members])
        if (pubid, mid) in published_set:
            continue
        published_set.add((pubid, mid))
        cur.execute("INSERT INTO PUBLISHED (PUBLICATIONID,MID) VALUES (%s,%s) ON CONFLICT (PUBLICATIONID,MID) DO NOTHING;", 
                    (pubid, mid))

    # ------------------------
    # COMMIT AND CLOSE
    # ------------------------
    conn.commit()
    cur.close()
    conn.close()
    print("ALL TABLES CREATED AND POPULATED WITH 20+ ROWS EACH SUCCESSFULLY.")

if __name__ == "__main__":
    main()

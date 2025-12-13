import psycopg2

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
    FOREIGN KEY (MENTOR_MID) REFERENCES LAB_MEMBER(MID) ON DELETE SET NULL,
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
            FOREIGN KEY (EID) REFERENCES EQUIPMENT(EID) ON DELETE CASCADE,
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID) ON DELETE CASCADE,
            CHECK (START_DATE IS NULL OR END_DATE IS NULL OR START_DATE <= END_DATE)
        );
        """,

        # FUNDS
        """
        CREATE TABLE IF NOT EXISTS FUNDS (
            GID VARCHAR(10) NOT NULL,
            PID VARCHAR(10) NOT NULL,
            PRIMARY KEY (GID, PID),
            FOREIGN KEY (GID) REFERENCES GRANTS(GID) ON DELETE CASCADE,
            FOREIGN KEY (PID) REFERENCES PROJECT(PID) ON DELETE CASCADE
        );
        """,

        # WORKS
        """
        CREATE TABLE IF NOT EXISTS WORKS (
            PID VARCHAR(10) NOT NULL,
            MID VARCHAR(10) NOT NULL,
            WEEK INT NOT NULL,
            ROLE VARCHAR(100) NOT NULL,
            HOURS INT CHECK (HOURS >= 0 AND HOURS <= 40),
            PRIMARY KEY (PID, MID, WEEK),
            FOREIGN KEY (PID) REFERENCES PROJECT(PID) ON DELETE CASCADE,
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID) ON DELETE CASCADE
        );
        """,

        # PUBLISHED
        """
        CREATE TABLE IF NOT EXISTS PUBLISHED (
            PUBLICATIONID VARCHAR(10) NOT NULL,
            MID VARCHAR(10) NOT NULL,
            PRIMARY KEY (PUBLICATIONID, MID),
            FOREIGN KEY (PUBLICATIONID) REFERENCES PUBLICATION(PUBLICATIONID) ON DELETE CASCADE,
            FOREIGN KEY (MID) REFERENCES LAB_MEMBER(MID) ON DELETE CASCADE
        );
        """
    ]

    for q in create_tables:
        cur.execute(q)
    conn.commit()
    print("All tables created successfully.\n")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()

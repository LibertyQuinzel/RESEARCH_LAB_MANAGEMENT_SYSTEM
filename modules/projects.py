def projects_menu(db):
    while True:
        print("\n--- Projects Menu ---")
        print("1. View all projects")
        print("2. Add project")
        print("3. Update project title")
        print("4. Delete project")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            rows = db.execute_query("SELECT * FROM project ORDER BY pid;", fetch=True)
            for r in rows:
                print(r)

        elif choice == "2":
            pid = input("PID: ")
            title = input("Title: ")
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            dur = input("Expected Duration (days): ")
            fid = input("FacultyID: ")

            query = """
                INSERT INTO project (pid, title, start_date, end_date, exp_duration, facultyid)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            db.execute_query(query, (pid, title, start, end, dur, fid))

        elif choice == "3":
            pid = input("Enter PID: ")
            newtitle = input("Enter new title: ")
            db.execute_query("UPDATE project SET title=%s WHERE pid=%s;", (newtitle, pid))

        elif choice == "4":
            pid = input("Enter PID: ")
            db.execute_query("DELETE FROM project WHERE pid=%s;", (pid,))

        elif choice == "5":
            break
        else:
            print("Invalid option.")

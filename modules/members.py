def members_menu(db):
    while True:
        print("\n--- Members Menu ---")
        print("1. View all members")
        print("2. Add member")
        print("3. Update member name")
        print("4. Delete member")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            rows = db.execute_query("SELECT * FROM lab_member ORDER BY mid;", fetch=True)
            for r in rows:
                print(r)

        elif choice == "2":
            mid = input("MID: ")
            name = input("Name: ")
            mtype = input("Member Type (Student/Faculty/Collaborator): ")
            join = input("Join Date (YYYY-MM-DD): ")
            mentor = input("Mentor MID (or NULL): ")

            query = """
                INSERT INTO lab_member (mid, name, member_type, join_date, mentor_mid)
                VALUES (%s, %s, %s, %s, %s);
            """

            db.execute_query(query, (mid, name, mtype, join, mentor))

        elif choice == "3":
            mid = input("Enter MID to update: ")
            newname = input("Enter new name: ")

            db.execute_query(
                "UPDATE lab_member SET name=%s WHERE mid=%s;",
                (newname, mid)
            )

        elif choice == "4":
            mid = input("Enter MID to delete: ")
            db.execute_query("DELETE FROM lab_member WHERE mid=%s;", (mid,))

        elif choice == "5":
            break
        else:
            print("Invalid option.")

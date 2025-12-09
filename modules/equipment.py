def equipment_menu(db):
    while True:
        print("\n--- Equipment Menu ---")
        print("1. View equipment")
        print("2. Add equipment")
        print("3. Update equipment status")
        print("4. Delete equipment")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            rows = db.execute_query("SELECT * FROM equipment ORDER BY eid;", fetch=True)
            for r in rows:
                print(r)

        elif choice == "2":
            eid = input("EID: ")
            name = input("Name: ")
            etype = input("Type: ")
            status = input("Status: ")
            pdate = input("Purchase Date (YYYY-MM-DD): ")

            query = """
                INSERT INTO equipment (eid, name, type, status, pur_date)
                VALUES (%s, %s, %s, %s, %s);
            """
            db.execute_query(query, (eid, name, etype, status, pdate))

        elif choice == "3":
            eid = input("EID: ")
            newstatus = input("New status: ")
            db.execute_query("UPDATE equipment SET status=%s WHERE eid=%s;", (newstatus, eid))

        elif choice == "4":
            eid = input("EID: ")
            db.execute_query("DELETE FROM equipment WHERE eid=%s;", (eid,))

        elif choice == "5":
            break
        else:
            print("Invalid option.")

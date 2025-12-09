from modules.members import members_menu
from modules.projects import projects_menu
from modules.equipment import equipment_menu
from database import Database

def main():
    # Create DB connection
    db = Database(
        dbname="mydatabase",
        user="myuser",
        password="mypassword",
        host="localhost",
        port=5432
    )

    while True:
        print("\n--- Research Lab Management System ---")
        print("1. Manage Members")
        print("2. Manage Projects")
        print("3. Manage Equipment")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            members_menu(db)
        elif choice == "2":
            projects_menu(db)
        elif choice == "3":
            equipment_menu(db)
        elif choice == "4":
            db.close()
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()

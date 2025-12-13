import tkinter as tk
from tkinter import messagebox

from modules.members import members_menu
from modules.projects import projects_menu
from modules.equipment import equipment_menu
from database import Database


def create_db():
	return Database(
		dbname="mydatabase",
		user="myuser",
		password="mypassword",
		host="localhost",
		port=5432,
	)


def on_exit(root, db):
	if messagebox.askokcancel("Exit", "Do you want to exit?"):
		try:
			db.close()
		except Exception:
			pass
		root.quit()


def main():
	db = create_db()

	root = tk.Tk()
	root.title("Research Lab Management System")
	# Larger main menu window
	root.geometry("1000x700")
	root.minsize(800, 600)
	# Styling
	try:
		from tkinter import ttk
		style = ttk.Style()
		try:
			style.theme_use('clam')
		except Exception:
			pass
	except Exception:
		ttk = None

	# Main frame with colored header
	header = tk.Frame(root, bg="#283593", height=80)
	header.pack(fill=tk.X)
	tk.Label(header, text="Research Lab Management System", fg="white", bg="#283593",
			 font=(None, 20, 'bold')).pack(pady=18)

	frm = tk.Frame(root, padx=30, pady=20, bg="#fafafa")
	frm.pack(fill=tk.BOTH, expand=True)

	# Centered button area
	btn_frame = tk.Frame(frm, bg="#fafafa")
	btn_frame.place(relx=0.5, rely=0.45, anchor='center')

	# Larger, colorful buttons with new labels
	btn_kwargs = {"width": 34, "height": 2}
	tk.Button(btn_frame, text="PROJECT MANAGEMENT", bg="#2196f3", fg="white",
			  font=(None, 12, 'bold'), command=lambda: projects_menu(db), **btn_kwargs).pack(pady=8)
	tk.Button(btn_frame, text="MEMBER MANAGEMENT", bg="#4caf50", fg="white",
			  font=(None, 12, 'bold'), command=lambda: members_menu(db), **btn_kwargs).pack(pady=8)
	tk.Button(btn_frame, text="EQUIPMENT USAGE TRACKING", bg="#ff5722", fg="white",
			  font=(None, 12, 'bold'), command=lambda: equipment_menu(db), **btn_kwargs).pack(pady=8)
	# Placeholder for reporting feature
	from modules.reporting import reporting_menu
	tk.Button(btn_frame, text="GRANT AND PUBLICATION REPORTING", bg="#6a1b9a", fg="white",
			  font=(None, 12, 'bold'), command=lambda: reporting_menu(db), **btn_kwargs).pack(pady=8)
	tk.Button(btn_frame, text="EXIT", bg="#9e9e9e", fg="white",
			  font=(None, 12, 'bold'), command=lambda: on_exit(root, db), **btn_kwargs).pack(pady=(18, 0))

	root.protocol("WM_DELETE_WINDOW", lambda: on_exit(root, db))
	root.mainloop()


if __name__ == "__main__":
	main()


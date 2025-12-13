import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


def projects_menu(db):
    # Ensure there is a root Tk instance. If not, create one and keep it hidden.
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    window = tk.Toplevel(root)
    window.title("Manage Projects")
    # Larger dialog
    window.geometry("1000x700")
    window.configure(bg="#fff3e0")

    # Table frame
    table_frame = tk.Frame(window)
    table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    columns = ("PID", "Title", "Start Date", "End Date", "Duration", "FacultyID")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Style Treeview
    try:
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Treeview", rowheight=22, font=(None, 10))
        style.configure("Treeview.Heading", font=(None, 10, 'bold'), background="#6a1b9a", foreground="white")
    except Exception:
        pass
    tree.tag_configure('odd', background='#ffffff')
    tree.tag_configure('even', background='#fff3e0')

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_table():
        # Fetch rows first; if fetch fails, do not clear the existing table.
        try:
            rows = db.execute_query(
                "SELECT pid, title, start_date, end_date, exp_duration, facultyid FROM project ORDER BY pid;",
                fetch=True,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch projects: {e}")
            return

        # Clear and repopulate only after successful fetch
        for row in tree.get_children():
            tree.delete(row)

        for idx, r in enumerate(rows):
            if isinstance(r, dict):
                vals = tuple(r.values())
            else:
                vals = tuple(r)
            tag = 'odd' if idx % 2 == 0 else 'even'
            tree.insert("", tk.END, values=vals, tags=(tag,))

        # Auto-adjust columns based on header and actual cell values
        for i, col in enumerate(columns):
            max_val_len = 0
            for child in tree.get_children():
                try:
                    cell = tree.item(child, "values")[i]
                except Exception:
                    cell = ""
                max_val_len = max(max_val_len, len(str(cell)))
            header_len = len(col)
            width = max(80, max(header_len * 10, max_val_len * 10))
            tree.column(col, width=width)

    refresh_table()

    # Form frame
    form_frame = tk.Frame(window, bg="#fff3e0")
    form_frame.pack(pady=10)

    labels = ["PID", "Title", "Start Date", "End Date", "Duration", "FacultyID"]
    entries = {}
    null_vars = {}
    # Fields that are NOT NULL in the DB - do not offer a 'Set NULL' checkbox for these
    no_null_allowed = {"PID", "Title", "FacultyID"}
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label, bg="#fff3e0").grid(row=i, column=0)
        entries[label] = tk.Entry(form_frame)
        entries[label].grid(row=i, column=1)
        # Only create a Set NULL checkbox for fields that allow NULL in the DB
        if label not in no_null_allowed:
            null_vars[label] = tk.BooleanVar(value=False)
            def make_toggle(l):
                def toggle():
                    if null_vars[l].get():
                        entries[l].delete(0, tk.END)
                        entries[l].insert(0, "Null")
                        entries[l].config(state='disabled')
                    else:
                        entries[l].config(state='normal')
                        entries[l].delete(0, tk.END)
                return toggle
            cb = tk.Checkbutton(form_frame, text="Set NULL", bg="#fff3e0", variable=null_vars[label], command=make_toggle(label))
            cb.grid(row=i, column=2, padx=6)
        else:
            # Explicitly mark that this field has no nullable toggle
            null_vars[label] = None

    def add_project():
        # Helper to require explicit 'Null' typing for intentional SQL NULL
        def get_input(label, required=False):
            # If the Set NULL checkbox is ticked, treat as explicit NULL
            if null_vars.get(label) and null_vars[label] and null_vars[label].get():
                return True, None
            v = entries[label].get().strip()
            if v == "":
                if required:
                    # If this field allows explicit NULL via checkbox, mention it; otherwise require a value
                    if null_vars.get(label):
                        messagebox.showwarning("Validation", f"{label} is required. Please enter a value or tick 'Set NULL' to set it explicitly to NULL.")
                    else:
                        messagebox.showwarning("Validation", f"{label} is required. Please enter a value.")
                else:
                    messagebox.showinfo(
                        "Confirmation needed",
                        f"Field '{label}' is empty. If you intend to set SQL NULL, tick the 'Set NULL' checkbox for that field and press the action again."
                    )
                return False, None
            if v.lower() == "null":
                return True, None
            # Dates left as-is
            if label in ("Start Date", "End Date"):
                return True, v
            if label == "Duration":
                return True, v
            # For textual fields, convert to uppercase
            return True, v.upper()

        ok, pid = get_input("PID", required=True)
        if not ok:
            return
        ok, title = get_input("Title", required=True)
        if not ok:
            return
        ok, start_date_str = get_input("Start Date", required=True)
        if not ok:
            return
        ok, end_date_str = get_input("End Date", required=False)
        if not ok:
            return
        ok, duration = get_input("Duration", required=False)
        if not ok:
            return
        ok, facultyid = get_input("FacultyID", required=True)
        if not ok:
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str is not None else None
        except Exception:
            messagebox.showwarning("Validation", "Start Date must be in YYYY-MM-DD format.")
            return

        if end_date_str is not None:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except Exception:
                messagebox.showwarning("Validation", "End Date must be in YYYY-MM-DD format or type 'Null'.")
                return
        else:
            end_date = None
        # Convert duration to int if provided
        if duration is not None:
            try:
                duration_val = int(duration)
            except Exception:
                messagebox.showwarning("Validation", "Duration must be an integer or type 'Null'.")
                return
        else:
            duration_val = None

        query = "INSERT INTO project (pid, title, start_date, end_date, exp_duration, facultyid) VALUES (%s, %s, %s, %s, %s, %s);"
        try:
            db.execute_query(query, (pid, title, start_date, end_date, duration_val, facultyid))
            messagebox.showinfo("Success", "Project added!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_project():
        pid = entries["PID"].get().strip()
        if not pid:
            messagebox.showwarning("Validation", "PID is required to update a project.")
            return
        if null_vars.get("Title") and null_vars["Title"] and null_vars["Title"].get():
            title = None
        else:
            title = entries["Title"].get().strip()
            if title == "":
                # Title is NOT NULL in DB and there is no Set NULL checkbox for it.
                if null_vars.get("Title"):
                    messagebox.showinfo("Confirmation needed", "Field 'Title' is empty. If you intend SQL NULL, tick the 'Set NULL' checkbox for Title and press Update again.")
                else:
                    messagebox.showwarning("Validation", "Title is required to update. Please enter a value.")
                return
            if title.lower() == "null":
                title = None
            else:
                title = title.upper()

        query = "UPDATE project SET title=%s WHERE pid=%s;"
        try:
            db.execute_query(query, (title, pid))
            messagebox.showinfo("Success", "Project updated!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_project():
        pid = entries["PID"].get().strip().upper()
        if not pid:
            messagebox.showwarning("Validation", "PID is required to delete a project.")
            return
        query = "DELETE FROM project WHERE PID=%s;"
        try:
            db.execute_query(query, (pid,))
            messagebox.showinfo("Success", "Project deleted!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Buttons
    btn_frame = tk.Frame(window, bg="#fff3e0")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add Project", bg="#4caf50", fg="white", command=add_project).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update Title", bg="#2196f3", fg="white", command=update_project).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete Project", bg="#f44336", fg="white", command=delete_project).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Refresh Table", bg="#ff9800", fg="white", command=refresh_table).grid(row=0, column=3, padx=5)
    # Mentorship: open a small dialog to enter PID and show mentor/mentee relations
    def open_mentorship_dialog():
        dlg = tk.Toplevel(window)
        dlg.title("Mentorship by Project")
        dlg.geometry("520x120")
        tk.Label(dlg, text="Project PID:", bg="#fff3e0").pack(padx=8, pady=(10,0))
        pid_box = tk.Entry(dlg)
        pid_box.pack(padx=8, pady=6)

        def on_show():
            pid = pid_box.get().strip()
            if not pid:
                messagebox.showinfo("Input needed", "Enter PID")
                return
            try:
                q = (
                    "SELECT DISTINCT lm.mid AS mentee_mid, lm.name AS mentee_name, "
                    "mentor.mid AS mentor_mid, mentor.name AS mentor_name "
                    "FROM works w "
                    "JOIN lab_member lm ON lm.mid = w.mid "
                    "JOIN lab_member mentor ON mentor.mid = lm.mentor_mid "
                    "JOIN works mw ON mw.mid = mentor.mid AND mw.pid = w.pid "
                    "WHERE w.pid = %s "
                    "ORDER BY mentor_mid, mentee_mid;"
                )
                rows = db.execute_query(q, (pid,), fetch=True)
                if not rows:
                    messagebox.showinfo("Mentorship", f"No mentorship relations found for project {pid}.")
                    return

                # show results in a new dialog
                results = tk.Toplevel(dlg)
                results.title(f"Mentorship relations for {pid}")
                cols = ("Mentee MID", "Mentee Name", "Mentor MID", "Mentor Name")
                tv = ttk.Treeview(results, columns=cols, show='headings')
                for c in cols:
                    tv.heading(c, text=c)
                    tv.column(c, width=180, anchor='w')
                tv.pack(fill=tk.BOTH, expand=True)
                for r in rows:
                    if isinstance(r, dict):
                        vals = (r.get('mentee_mid'), r.get('mentee_name'), r.get('mentor_mid'), r.get('mentor_name'))
                    else:
                        vals = (r[0], r[1], r[2], r[3])
                    tv.insert('', tk.END, values=vals)
                tk.Button(results, text='Close', command=results.destroy).pack(pady=6)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dlg, text="Show", bg="#7b1fa2", fg="white", command=on_show).pack(pady=(0,10))

    tk.Button(btn_frame, text="Mentorship (by Project)", bg="#7b1fa2", fg="white", command=open_mentorship_dialog).grid(row=0, column=4, padx=6)

    # Show status of a project (by PID)
    def show_project_status():
        def run():
            pid = pid_entry.get().strip()
            if not pid:
                messagebox.showinfo("Input needed", "Enter PID")
                return
            try:
                q = "SELECT pid, title, start_date, end_date FROM project WHERE pid = %s;"
                rows = db.execute_query(q, (pid,), fetch=True)
                if not rows:
                    messagebox.showinfo("Not found", "Project not found")
                    return
                r = rows[0]
                if isinstance(r, dict):
                    start = r.get('start_date')
                    end = r.get('end_date')
                    title = r.get('title')
                else:
                    title, start, end = r[1], r[2], r[3]
                status = 'Active' if (end is None) or (str(end) == '') else 'Closed'
                messagebox.showinfo("Project Status", f"PID: {pid}\nTitle: {title}\nStatus: {status}\nStart: {start}\nEnd: {end}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        row = tk.Frame(window, bg="#fff3e0")
        row.pack(pady=(6, 10))
        tk.Label(row, text="PID:", bg="#fff3e0").pack(side=tk.LEFT)
        pid_entry = tk.Entry(row)
        pid_entry.pack(side=tk.LEFT, padx=6)
        tk.Button(row, text="Show Project Status", bg="#1976d2", fg="white", command=run).pack(side=tk.LEFT, padx=6)

    # Projects funded by a grant active during a period
    def projects_active_in_period():
        def run():
            gid = gid_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()
            if not gid or not start or not end:
                messagebox.showinfo("Input needed", "Enter grant id, start date and end date")
                return
            try:
                # Join FUNDS to find projects funded by the grant and check active period
                q = (
                    "SELECT COUNT(DISTINCT p.pid) AS cnt FROM project p "
                    "JOIN funds f ON f.pid = p.pid "
                    "WHERE f.gid = %s AND (p.start_date <= %s AND (p.end_date IS NULL OR p.end_date >= %s));"
                )
                rows = db.execute_query(q, (gid, end, start), fetch=True)
                cnt = rows[0].get('cnt') if isinstance(rows[0], dict) else rows[0][0]
                messagebox.showinfo("Count", f"Projects funded by grant {gid} active in period: {cnt}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        frm2 = tk.Frame(window, bg="#fff3e0")
        frm2.pack(pady=(6, 10))
        tk.Label(frm2, text="Grant ID:", bg="#fff3e0").pack(side=tk.LEFT)
        gid_entry = tk.Entry(frm2)
        gid_entry.pack(side=tk.LEFT, padx=4)
        tk.Label(frm2, text="Start(YYYY-MM-DD):", bg="#fff3e0").pack(side=tk.LEFT)
        start_entry = tk.Entry(frm2)
        start_entry.pack(side=tk.LEFT, padx=4)
        tk.Label(frm2, text="End(YYYY-MM-DD):", bg="#fff3e0").pack(side=tk.LEFT)
        end_entry = tk.Entry(frm2)
        end_entry.pack(side=tk.LEFT, padx=4)
        tk.Button(frm2, text="Count Projects", bg="#fb8c00", fg="white", command=run).pack(side=tk.LEFT, padx=6)

    show_project_status()
    projects_active_in_period()

    # Mentorship moved to button above for better visibility

    # Make the window modal with respect to the (possibly hidden) root and wait until closed
    try:
        window.transient(root)
        window.grab_set()
    except Exception:
        pass

    window.wait_window()

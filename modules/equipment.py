import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


def equipment_menu(db):
    # Ensure there is a root Tk instance. If not, create one and keep it hidden.
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    window = tk.Toplevel(root)
    window.title("Manage Equipment")
    # Larger dialog
    window.geometry("1000x700")
    window.configure(bg="#e8f5e9")

    table_frame = tk.Frame(window)
    table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    columns = ("EID", "Name", "Type", "Status", "Purchase Date")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Treeview styling
    try:
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Treeview", rowheight=22, font=(None, 10))
        style.configure("Treeview.Heading", font=(None, 10, 'bold'), background="#2e7d32", foreground="white")
    except Exception:
        pass
    tree.tag_configure('odd', background='#ffffff')
    tree.tag_configure('even', background='#e8f5e9')

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_table():
        # Fetch rows first. If fetch fails, leave the current table intact.
        try:
            rows = db.execute_query(
                "SELECT eid, name, type, status, pur_date FROM equipment ORDER BY eid;",
                fetch=True,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch equipment: {e}")
            return

        # Only clear and repopulate the tree when fetch succeeded
        for row in tree.get_children():
            tree.delete(row)

        for idx, r in enumerate(rows):
            if isinstance(r, dict):
                vals = tuple(r.values())
            else:
                vals = tuple(r)
            tag = 'odd' if idx % 2 == 0 else 'even'
            tree.insert("", tk.END, values=vals, tags=(tag,))

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
    form_frame = tk.Frame(window, bg="#e8f5e9")
    form_frame.pack(pady=10)

    labels = ["EID", "Name", "Type", "Status", "Purchase Date"]
    entries = {}
    null_vars = {}
    # Fields that are NOT NULL in the DB - do not offer a 'Set NULL' checkbox for these
    no_null_allowed = {"EID", "Name"}
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label, bg="#e8f5e9").grid(row=i, column=0)
        entries[label] = tk.Entry(form_frame)
        entries[label].grid(row=i, column=1)
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
            cb = tk.Checkbutton(form_frame, text="Set NULL", bg="#e8f5e9", variable=null_vars[label], command=make_toggle(label))
            cb.grid(row=i, column=2, padx=6)
        else:
            null_vars[label] = None

    def add_equipment():
        def get_input(label, required=False):
            v = entries[label].get().strip()
            if v == "":
                if required:
                    messagebox.showwarning("Validation", f"{label} is required. Please enter a value.")
                else:
                    messagebox.showinfo(
                        "Confirmation needed",
                        f"Field '{label}' is empty. If you intend to set SQL NULL, type 'Null' (without quotes) into the field and press the action again."
                    )
                return False, None
            if v.lower() == "null":
                return True, None
            return True, v

        ok, eid = get_input("EID", required=True)
        if not ok:
            return
        ok, name = get_input("Name", required=True)
        if not ok:
            return
        ok, typ = get_input("Type", required=True)
        if not ok:
            return
        ok, status = get_input("Status", required=True)
        if not ok:
            return
        ok, pur_date_str = get_input("Purchase Date", required=False)
        if not ok:
            return

        allowed_status = {"In Use", "Available", "Under Maintenance","Retired"}
        if status is not None and status not in allowed_status:
            messagebox.showwarning("Validation", f"Status must be one of: {', '.join(allowed_status)}")
            return

        if pur_date_str is not None:
            try:
                pur_date = datetime.strptime(pur_date_str, "%Y-%m-%d").date()
            except Exception:
                messagebox.showwarning("Validation", "Purchase Date must be in YYYY-MM-DD format or type 'Null'.")
                return
        else:
            pur_date = None

        query = "INSERT INTO equipment (eid, name, type, status, pur_date) VALUES (%s, %s, %s, %s, %s);"
        try:
            db.execute_query(query, (eid, name, typ, status, pur_date))
            messagebox.showinfo("Success", "Equipment added!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_status():
        eid = entries["EID"].get().strip()
        status = entries["Status"].get().strip()
        if not eid:
            messagebox.showwarning("Validation", "EID is required to update status.")
            return
        if status == "":
            messagebox.showinfo("Confirmation needed", "Field 'Status' is empty. If you intend SQL NULL, type 'Null' into the Status field and press Update again.")
            return
        if status.lower() == "null":
            status = None

        allowed_status = {"In Use", "Available", "Under Maintenance","Retired"}
        if status is not None and status not in allowed_status:
            messagebox.showwarning("Validation", f"Status must be one of: {', '.join(allowed_status)}")
            return
        query = "UPDATE equipment SET status=%s WHERE eid=%s;"
        try:
            db.execute_query(query, (status, eid))
            messagebox.showinfo("Success", "Status updated!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_equipment():
        eid = entries["EID"].get().strip().upper()
        if not eid:
            messagebox.showwarning("Validation", "EID is required to delete equipment.")
            return
        query = "DELETE FROM equipment WHERE eid=%s;"
        try:
            db.execute_query(query, (eid,))
            messagebox.showinfo("Success", "Equipment deleted!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(window, bg="#e8f5e9")
    btn_frame.pack(pady=10)

    # Equipment action buttons (consistent sizes)
    btn_kwargs = dict(width=14, pady=4)
    tk.Button(btn_frame, text="Add Equipment", bg="#4caf50", fg="white", command=add_equipment, **btn_kwargs).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Delete Equipment", bg="#f44336", fg="white", command=delete_equipment, **btn_kwargs).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Update Status", bg="#2196f3", fg="white", command=update_status, **btn_kwargs).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Show Status", bg="#607d8b", fg="white", command=lambda: show_status(), **btn_kwargs).grid(row=0, column=3, padx=5)
    tk.Button(btn_frame, text="Refresh Table", bg="#ff9800", fg="white", command=refresh_table, **btn_kwargs).grid(row=0, column=4, padx=5)

    def show_status():
        # Display equipment status and a short summary for given EID
        eid = entries["EID"].get().strip()
        if not eid:
            messagebox.showinfo("Input needed", "Enter EID in the EID field above.")
            return
        try:
            q = "SELECT eid, name, status, pur_date FROM equipment WHERE eid = %s;"
            rows = db.execute_query(q, (eid,), fetch=True)
            if not rows:
                messagebox.showinfo("Not found", f"No equipment found with EID {eid}.")
                return
            r = rows[0] if isinstance(rows[0], dict) else { 'eid': rows[0][0], 'name': rows[0][1], 'status': rows[0][2], 'pur_date': rows[0][3] }

            # Count current users
            q2 = "SELECT COUNT(*) AS cnt FROM uses WHERE eid = %s AND (end_date IS NULL OR end_date > CURRENT_DATE);"
            cnt_rows = db.execute_query(q2, (eid,), fetch=True)
            cnt = 0
            if cnt_rows:
                cnt = int(cnt_rows[0].get('cnt') if isinstance(cnt_rows[0], dict) else cnt_rows[0][0])

            name = r.get('name')
            status = r.get('status')
            pur_date = r.get('pur_date')
            msg = f"EID: {eid}\nName: {name}\nStatus: {status}\nPurchase date: {pur_date}\nCurrent active users: {cnt}"
            messagebox.showinfo(f"Status of {eid}", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # The explicit Show Status button above is replaced by the labeled button
    # created earlier with shortcut text.

    # Equipment usage management (assumes table equipment_usage with eid, member_mid, pid, start_time, end_time)
    usage_frame = tk.LabelFrame(window, text="Equipment Usage", bg="#e8f5e9")
    usage_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(5, 10))

    tk.Label(usage_frame, text="EID:", bg="#e8f5e9").grid(row=0, column=0)
    eid_entry = tk.Entry(usage_frame)
    eid_entry.grid(row=0, column=1)
    tk.Label(usage_frame, text="Member MID:", bg="#e8f5e9").grid(row=0, column=2)
    mid_entry = tk.Entry(usage_frame)
    mid_entry.grid(row=0, column=3)
    tk.Label(usage_frame, text="Purpose:", bg="#e8f5e9").grid(row=0, column=4)
    pid_entry = tk.Entry(usage_frame)
    pid_entry.grid(row=0, column=5)

    def add_usage():
        # Use USES table (schema) with START_DATE, END_DATE columns
        q = "INSERT INTO USES (EID, MID, PURPOSE, START_DATE) VALUES (%s, %s, %s, CURRENT_DATE);"
        try:
            db.execute_query(q, (eid_entry.get(), mid_entry.get(), pid_entry.get()))
            messagebox.showinfo("Success", "Usage started")
            refresh_usage()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def end_usage():
        # Close an active usage row. Use RETURNING to know whether any row
        # was actually updated so we can inform the user if nothing matched.
        eid = eid_entry.get().strip()
        mid = mid_entry.get().strip()
        if not eid or not mid:
            messagebox.showwarning("Validation", "Both EID and Member MID are required to end usage.")
            return

        # Match case-insensitively to avoid issues with entered casing
        q = (
            "UPDATE USES SET END_DATE = GREATEST(COALESCE(START_DATE, CURRENT_DATE - INTERVAL '1 day'), CURRENT_DATE - INTERVAL '1 day') "
            "WHERE UPPER(EID) = UPPER(%s) AND UPPER(MID) = UPPER(%s) AND END_DATE IS NULL "
            "RETURNING START_DATE, END_DATE;"
        )
        try:
            rows = db.execute_query(q, (eid, mid), fetch=True)
            if rows:
                messagebox.showinfo("Success", "Usage ended")
            else:
                messagebox.showinfo("No active usage", "No open usage found for that EID/MID.")
            refresh_usage()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(usage_frame, text="Start Usage", bg="#4caf50", fg="white", command=add_usage).grid(row=1, column=1, pady=6)
    tk.Button(usage_frame, text="End Usage", bg="#2196f3", fg="white", command=end_usage).grid(row=1, column=3, pady=6)

    # Button to show current users of a given equipment and their projects
    def show_current_users():
        eid = eid_entry.get().strip()
        if not eid:
            messagebox.showinfo("Input needed", "Enter EID in the EID field above.")
            return
        try:
            q = (
                "SELECT u.mid, lm.name, u.purpose, p.title FROM uses u "
                "LEFT JOIN lab_member lm ON lm.mid = u.mid "
                "LEFT JOIN project p ON p.pid = u.purpose "
                "WHERE u.eid = %s AND (u.end_date IS NULL OR u.end_date > CURRENT_DATE)"
            )
            rows = db.execute_query(q, (eid,), fetch=True)
            if not rows:
                messagebox.showinfo("No users", "No current users found for this equipment.")
                return

            # Show results in dialog. Make the dialog a child of the
            # equipment `window` so it receives events while the main
            # equipment window is using grab_set(). Also make it transient
            # and give it a local grab so it's modal relative to the
            # equipment window.
            dlg = tk.Toplevel(window)
            dlg.title(f"Current users of {eid}")
            try:
                dlg.transient(window)
                dlg.grab_set()
            except Exception:
                pass
            cols = ("MID", "Name", "Purpose", "Project Title")
            tv = ttk.Treeview(dlg, columns=cols, show='headings')
            for c in cols:
                tv.heading(c, text=c)
                tv.column(c, width=200, anchor='w')
            tv.pack(fill=tk.BOTH, expand=True)
            for r in rows:
                if isinstance(r, dict):
                    vals = (r.get('mid'), r.get('name'), r.get('purpose'), r.get('title'))
                else:
                    vals = (r[0], r[1] if len(r)>1 else '', r[2] if len(r)>2 else '', r[3] if len(r)>3 else '')
                tv.insert('', tk.END, values=vals)
            tk.Button(dlg, text='Close', command=lambda: (dlg.grab_release() if hasattr(dlg, 'grab_release') else None, dlg.destroy())).pack(pady=6)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(usage_frame, text="Show Current Users", bg="#7b1fa2", fg="white", command=show_current_users).grid(row=1, column=5, padx=6)

    # Usage table
    usage_table_frame = tk.Frame(window)
    usage_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    usage_cols = ("EID", "Member MID", "Purpose", "Start Time", "End Time")
    usage_tree = ttk.Treeview(usage_table_frame, columns=usage_cols, show='headings')
    for c in usage_cols:
        usage_tree.heading(c, text=c)
        usage_tree.column(c, width=120, anchor='center')
    usage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    usage_scroll = ttk.Scrollbar(usage_table_frame, orient='vertical', command=usage_tree.yview)
    usage_tree.configure(yscrollcommand=usage_scroll.set)
    usage_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_usage():
        # Fetch usage rows first. If fetch fails, keep existing usage table intact.
        try:
            rows = db.execute_query("SELECT EID, MID, PURPOSE, START_DATE, END_DATE FROM USES ORDER BY START_DATE DESC;", fetch=True)
        except Exception:
            # If table missing or query failed, skip updating the usage table
            return

        for r in usage_tree.get_children():
            usage_tree.delete(r)

        for r in rows:
            if isinstance(r, dict):
                vals = (r.get('eid'), r.get('mid'), r.get('purpose'), r.get('start_date'), r.get('end_date'))
            else:
                vals = tuple(r)
            usage_tree.insert('', tk.END, values=vals)

    refresh_usage()

    # Make the window modal with respect to the (possibly hidden) root and wait until closed
    try:
        window.transient(root)
        window.grab_set()
    except Exception:
        pass

    window.wait_window()

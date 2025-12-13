import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

def members_menu(db):
    # Ensure root exists
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    # --- Window setup ---
    window = tk.Toplevel(root)
    window.title("Manage Members")
    window.geometry("1000x700")
    window.configure(bg="#e0f7fa")

    # --- Table Frame ---
    table_frame = tk.Frame(window)
    table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    columns = ("MID", "Name", "Type", "Join Date", "Mentor MID")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Treeview styling
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    style.configure("Treeview", rowheight=22, font=(None, 10))
    style.configure("Treeview.Heading", font=(None, 10, 'bold'), background="#455a64", foreground="white")
    tree.tag_configure('odd', background='#ffffff')
    tree.tag_configure('even', background='#f1f8e9')

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Form Frame ---
    form_frame = tk.Frame(window, bg="#e0f7fa")
    form_frame.pack(pady=10)

    labels = ["MID", "Name", "Member Type", "Join Date", "Mentor MID"]
    entries = {}
    null_vars = {}

    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label, bg="#e0f7fa").grid(row=i, column=0, sticky="w")
        entries[label] = tk.Entry(form_frame)
        entries[label].grid(row=i, column=1, padx=5, pady=2)

        # Only Mentor MID is nullable
        if label == "Mentor MID":
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
            cb = tk.Checkbutton(form_frame, text="Set NULL", bg="#e0f7fa",
                                variable=null_vars[label], command=make_toggle(label))
            cb.grid(row=i, column=2, padx=6)

    # --- Treeview refresh ---
    def refresh_table():
        # Fetch rows first. If fetch fails, leave table intact and show an error.
        try:
            rows = db.execute_query(
                "SELECT mid, name, member_type, join_date, mentor_mid FROM lab_member ORDER BY mid;",
                fetch=True
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch members: {e}")
            return

        # Clear and repopulate only after successful fetch
        for row in tree.get_children():
            tree.delete(row)

        for idx, r in enumerate(rows):
            vals = tuple(r.values()) if isinstance(r, dict) else tuple(r)
            tag = 'odd' if idx % 2 == 0 else 'even'
            tree.insert("", tk.END, values=vals, tags=(tag,))

        # Auto-adjust column widths
        for i, col in enumerate(columns):
            max_len = max([len(str(tree.item(child, "values")[i])) for child in tree.get_children()] + [len(col)])
            tree.column(col, width=max(80, max_len * 10))

    # --- Input helper ---
    def get_input(label, required=False):
        if label == "Mentor MID" and null_vars.get(label) and null_vars[label].get():
            return True, None
        value = entries[label].get().strip()
        if required and not value:
            messagebox.showwarning("Validation", f"{label} is required!")
            return False, None
        if value.lower() == "null":
            return True, None
        if label == "Member Type":
            mapping = {"STUDENT":"Student", "FACULTY":"Faculty", "COLLABORATOR":"Collaborator"}
            return True, mapping.get(value.upper(), value.title())
        return True, value.upper() if value else None

    # --- CRUD operations ---
    def add_member():
        ok, mid = get_input("MID", required=True)
        if not ok: return
        ok, name = get_input("Name", required=True)
        if not ok: return
        ok, member_type = get_input("Member Type", required=True)
        if not ok: return
        ok, join_date_str = get_input("Join Date", required=True)
        if not ok: return
        ok, mentor = get_input("Mentor MID", required=False)
        if not ok: return

        try:
            join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()
        except Exception:
            messagebox.showwarning("Validation", "Join Date must be YYYY-MM-DD.")
            return

        query = "INSERT INTO lab_member (mid, name, member_type, join_date, mentor_mid) VALUES (%s, %s, %s, %s, %s);"
        try:
            db.execute_query(query, (mid, name, member_type, join_date, mentor))
            messagebox.showinfo("Success", "Member added!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Insert failed: {e}")

    def update_member():
        mid = entries["MID"].get().strip()
        if not mid:
            messagebox.showwarning("Validation", "MID is required to update a member.")
            return
        ok, name = get_input("Name", required=True)
        if not ok: return

        query = "UPDATE lab_member SET name=%s WHERE mid=%s;"
        try:
            db.execute_query(query, (name, mid))
            messagebox.showinfo("Success", "Member updated!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_member():
        mid = entries["MID"].get().strip().upper()
        if not mid:
            messagebox.showwarning("Validation", "MID is required to delete a member.")
            return
        query = "DELETE FROM lab_member WHERE mid=%s;"
        try:
            db.execute_query(query, (mid,))
            messagebox.showinfo("Success", "Member deleted!")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Members who worked on projects funded by a given grant ---
    def show_members_by_grant():
        # Ask for Grant ID and show member list who worked on projects funded by it
        def run():
            gid = gid_entry.get().strip().upper()
            if not gid:
                messagebox.showinfo("Input needed", "Enter Grant ID")
                return
            try:
                q = (
                    "SELECT DISTINCT lm.mid, lm.name "
                    "FROM lab_member lm "
                    "JOIN works w ON w.mid = lm.mid "
                    "JOIN funds f ON f.pid = w.pid "
                    "WHERE f.gid = %s ORDER BY lm.mid;"
                )
                rows = db.execute_query(q, (gid,), fetch=True)
                if not rows:
                    messagebox.showinfo("No results", f"No members found for grant {gid}.")
                    return

                # Show results in a simple dialog treeview
                root = tk._default_root
                if root is None:
                    root = tk.Tk(); root.withdraw()
                dlg = tk.Toplevel(root)
                dlg.title(f"Members for Grant {gid}")
                cols = ("MID", "Name")
                tv = ttk.Treeview(dlg, columns=cols, show='headings')
                for c in cols:
                    tv.heading(c, text=c)
                    tv.column(c, width=180, anchor='w')
                tv.pack(fill=tk.BOTH, expand=True)
                for r in rows:
                    if isinstance(r, dict):
                        vals = (r.get('mid'), r.get('name'))
                    else:
                        vals = (r[0], r[1])
                    tv.insert('', tk.END, values=vals)
                tk.Button(dlg, text='Close', command=dlg.destroy).pack(pady=6)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        frm = tk.Frame(window, bg="#e0f7fa")
        frm.pack(pady=(6, 10))
        tk.Label(frm, text="Grant ID:", bg="#e0f7fa").pack(side=tk.LEFT)
        gid_entry = tk.Entry(frm)
        gid_entry.pack(side=tk.LEFT, padx=6)
        tk.Button(frm, text="Show Members for Grant", bg="#7b1fa2", fg="white", command=run).pack(side=tk.LEFT, padx=6)

    # NOTE: Mentorship-by-project view moved to Projects menu. See modules/projects.py

    # --- Buttons ---
    btn_frame = tk.Frame(window, bg="#e0f7fa")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add Member", bg="#4caf50", fg="white", command=add_member).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update Name", bg="#2196f3", fg="white", command=update_member).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete Member", bg="#f44336", fg="white", command=delete_member).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Refresh Table", bg="#ff9800", fg="white", command=refresh_table).grid(row=0, column=3, padx=5)
    # Mentorship report moved to Projects menu

    # --- Initial load ---
    refresh_table()

    # --- Make window modal ---
    try:
        window.transient(root)
        window.grab_set()
    except Exception:
        pass
    window.wait_window()

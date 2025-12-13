import tkinter as tk
from tkinter import ttk, messagebox


def reporting_menu(db):
    # Base root
    root = tk._default_root
    if root is None:
        root = tk.Tk()
        root.withdraw()

    window = tk.Toplevel(root)
    window.title("Grant & Publication Reporting")
    window.geometry("1000x700")
    window.configure(bg="#f3e5f5")

    frame = tk.Frame(window, bg="#f3e5f5", padx=12, pady=12)
    frame.pack(fill=tk.BOTH, expand=True)

    # Controls row
    ctrl = tk.Frame(frame, bg="#f3e5f5")
    ctrl.pack(fill=tk.X)

    # ============================================================
    # 1) TOP PUBLISHERS
    # ============================================================
    def top_publishers():
        try:
            rows = db.execute_query(
                """
                SELECT lm.mid, lm.name, COUNT(p.publicationid) AS pubs
                FROM lab_member lm
                LEFT JOIN published p ON p.mid = lm.mid
                GROUP BY lm.mid, lm.name
                ORDER BY pubs DESC;
                """,
                fetch=True,
            )

            if not rows:
                messagebox.showinfo("Top Publishers", "No publication data found.")
                return

            # Handle dict row or tuple
            first = rows[0]
            max_pubs = first["pubs"] if isinstance(first, dict) else first[2]

            top = []
            for r in rows:
                pubs = r["pubs"] if isinstance(r, dict) else r[2]
                if pubs == max_pubs:
                    mid = r["mid"] if isinstance(r, dict) else r[0]
                    name = r["name"] if isinstance(r, dict) else r[1]
                    top.append((mid, name, pubs))

            text = f"Top publisher(s) with {max_pubs} publication(s):\n"
            for mid, name, pubs in top:
                text += f"- {mid} — {name} ({pubs})\n"

            messagebox.showinfo("Top Publishers", text)

        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {e}")

    tk.Button(
        ctrl,
        text="Member(s) with Highest Publications",
        command=top_publishers,
        bg="#6a1b9a",
        fg="white"
    ).pack(side=tk.LEFT, padx=6, pady=6)

    # ============================================================
    # 2) AVERAGE STUDENT PUBLISHING BY MAJOR
    # ============================================================
    def avg_student_pubs():
        try:
            rows = db.execute_query(
                """
                SELECT s.major, COUNT(pub.publicationid) AS pubs,
                       COUNT(DISTINCT m.mid) AS students
                FROM lab_member m
                JOIN student s ON s.mid = m.mid
                LEFT JOIN published pub ON pub.mid = m.mid
                WHERE TRIM(m.member_type) ILIKE 'student'
                GROUP BY s.major;
                """,
                fetch=True,
            )

            if not rows:
                messagebox.showinfo("Average Student Publications", "No data available.")
                return

            text = "Average student publications per major:\n"

            for r in rows:
                major = r["major"] if isinstance(r, dict) else r[0]
                pubs = r["pubs"] if isinstance(r, dict) else r[1]
                students = r["students"] if isinstance(r, dict) else r[2]
                avg = pubs / students if students > 0 else 0
                text += f"{major}: {avg:.2f}\n"

            messagebox.showinfo("Average Student Publications", text)

        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {e}")

    tk.Button(
        ctrl,
        text="Avg Student Pubs per Major",
        command=avg_student_pubs,
        bg="#00897b",
        fg="white"
    ).pack(side=tk.LEFT, padx=6, pady=6)

    # ============================================================
    # 3) TOP 3 PUBLISHERS FOR A GIVEN GRANT
    # ============================================================
    def top3_for_grant():
        row = tk.Frame(frame, bg="#f3e5f5")
        row.pack(fill=tk.X, pady=(10, 0))

        tk.Label(row, text="Grant ID:", bg="#f3e5f5").pack(side=tk.LEFT, padx=6)
        grant_entry = tk.Entry(row)
        grant_entry.pack(side=tk.LEFT, padx=6)

        def run():
            gid = grant_entry.get().strip()
            if not gid:
                messagebox.showinfo("Input Needed", "Enter a grant ID.")
                return

            try:
                rows = db.execute_query(
                    """
                    SELECT w.mid AS member_mid, COUNT(pub.publicationid) AS pubs
                    FROM works w
                    JOIN funds f ON f.pid = w.pid
                    LEFT JOIN published pub ON pub.mid = w.mid
                    WHERE f.gid = %s
                    GROUP BY w.mid
                    ORDER BY pubs DESC
                    LIMIT 3;
                    """,
                    (gid,),
                    fetch=True,
                )

                if not rows:
                    messagebox.showinfo("Top 3", "No matching data found.")
                    return

                text = f"Top 3 prolific members for grant {gid}:\n"
                for r in rows:
                    mid = r["member_mid"] if isinstance(r, dict) else r[0]
                    pubs = r["pubs"] if isinstance(r, dict) else r[1]
                    text += f"{mid}: {pubs} publications\n"

                messagebox.showinfo("Top 3", text)

            except Exception as e:
                messagebox.showerror("Error", f"Query failed: {e}")

        tk.Button(
            row,
            text="Top 3 for Grant",
            command=run,
            bg="#ef6c00",
            fg="white"
        ).pack(side=tk.LEFT, padx=6)

    top3_for_grant()

    # ============================================================
    # 4) SHOW GRANTS TABLE
    # ============================================================
    def show_grants():
        try:
            rows = db.execute_query(
                "SELECT gid, source, budget, start_date, duration FROM grants ORDER BY gid;",
                fetch=True,
            )

            if not rows:
                messagebox.showinfo("Grants", "No grants found.")
                return

            dlg = tk.Toplevel(window)
            dlg.title("Grants")

            cols = ("GID", "Source", "Budget", "Start Date", "Duration")
            tv = ttk.Treeview(dlg, columns=cols, show="headings")
            for c in cols:
                tv.heading(c, text=c)
                tv.column(c, width=160, anchor="w")
            tv.pack(fill=tk.BOTH, expand=True)

            for r in rows:
                if isinstance(r, dict):
                    vals = (r["gid"], r["source"], r["budget"], r["start_date"], r["duration"])
                else:
                    vals = r
                tv.insert("", tk.END, values=vals)

            tk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=6)

        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {e}")

    tk.Button(
        ctrl,
        text="Show Grants",
        command=show_grants,
        bg="#3949ab",
        fg="white"
    ).pack(side=tk.LEFT, padx=6, pady=6)

    # ============================================================
    # 5) SHOW ALL PUBLICATIONS
    # ============================================================
    def show_publications():
        try:
            rows = db.execute_query(
                """
                SELECT publicationid, title, venue, publication_date, doi
                FROM publication
                ORDER BY publication_date DESC NULLS LAST;
                """,
                fetch=True,
            )

            if not rows:
                messagebox.showinfo("Publications", "No publications found.")
                return

            dlg = tk.Toplevel(window)
            dlg.title("Publications")

            cols = ("PubID", "Title", "Venue", "Date", "DOI")
            tv = ttk.Treeview(dlg, columns=cols, show="headings")
            for c in cols:
                tv.heading(c, text=c)
                tv.column(c, width=220, anchor="w")
            tv.pack(fill=tk.BOTH, expand=True)

            for r in rows:
                vals = (r[0], r[1], r[2], r[3], r[4]) if not isinstance(r, dict) else (
                    r["publicationid"], r["title"], r["venue"], r["publication_date"], r["doi"]
                )
                tv.insert("", tk.END, values=vals)

            tk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=6)

        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {e}")

    tk.Button(
        ctrl,
        text="Show Publications",
        command=show_publications,
        bg="#1e88e5",
        fg="white"
    ).pack(side=tk.LEFT, padx=6, pady=6)

    # Grabbing window
    try:
        window.transient(root)
        window.grab_set()
    except Exception:
        pass

    window.wait_window()

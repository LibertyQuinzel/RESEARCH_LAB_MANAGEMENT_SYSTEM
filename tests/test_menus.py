import types
import builtins
import pytest

from types import SimpleNamespace

# Helper fake DB to drive different query results
class FakeDB:
    def __init__(self, responses=None, raise_on=None):
        # responses: dict of query substring -> return value
        self.responses = responses or {}
        self.raise_on = raise_on or set()
        self.executed = []

    def execute_query(self, query, params=None, fetch=False):
        self.executed.append((query, params, fetch))
        if any(r in query for r in self.raise_on):
            raise Exception("forced error")
        for k, v in self.responses.items():
            if k in query:
                return v
        # default: empty list for fetch, True otherwise
        return [] if fetch else True


# Minimal dummy tkinter/ttk components used by the menus
class DummyWidget:
    def __init__(self, *a, **k):
        self._children = []
        self._text = ''

    def pack(self, *a, **k):
        return None
    def grid(self, *a, **k):
        return None
    def pack_forget(self, *a, **k):
        return None
    def config(self, *a, **k):
        return None
    def configure(self, *a, **k):
        return None
    def withdraw(self):
        return None
    def title(self, *a, **k):
        return None
    def geometry(self, *a, **k):
        return None
    def destroy(self):
        return None
    def transient(self, *a, **k):
        return None
    def grab_set(self):
        return None
    def grab_release(self):
        return None
    def wait_window(self):
        # do not block in tests
        return None

class DummyEntry(DummyWidget):
    def __init__(self, *a, **k):
        super().__init__()
        self._val = ''
        self._state = 'normal'
    def get(self):
        return self._val
    def insert(self, idx, val):
        self._val = val
    def delete(self, a, b=None):
        self._val = ''
    def config(self, **k):
        if 'state' in k:
            self._state = k['state']

class DummyTreeview(DummyWidget):
    def __init__(self, *a, **k):
        super().__init__()
        self._rows = []
        self._columns = []
    def heading(self, *a, **k):
        return None
    def column(self, *a, **k):
        return None
    def insert(self, parent, index, values=None, tags=None):
        self._rows.append(values)
        return 'id'
    def get_children(self):
        return list(range(len(self._rows)))
    def item(self, child, option=None):
        return { 'values': self._rows[child] }
    def delete(self, child):
        # accept anything
        return None
    def configure(self, **k):
        return None
    def yview(self, *a, **k):
        return None

class DummyStyle:
    def theme_use(self, *a, **k):
        return None
    def configure(self, *a, **k):
        return None

class DummyScrollbar(DummyWidget):
    def __init__(self, *a, **k):
        super().__init__()
    def set(self, *a, **k):
        return None

# Message capture
class MsgCapture:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.errors = []
    def showinfo(self, title, msg):
        self.infos.append((title, msg))
    def showwarning(self, title, msg):
        self.warnings.append((title, msg))
    def showerror(self, title, msg):
        self.errors.append((title, msg))


@pytest.fixture(autouse=True)
def patch_tkinter(monkeypatch):
    """Patch tkinter and ttk components used by the modules to dummy implementations."""
    import importlib
    # Create dummy namespaces
    dummy_tk = SimpleNamespace()
    dummy_tk.Tk = lambda *a, **k: DummyWidget()
    dummy_tk.Toplevel = lambda *a, **k: DummyWidget()
    dummy_tk.Frame = lambda *a, **k: DummyWidget()
    dummy_tk.Label = lambda *a, **k: DummyWidget()
    dummy_tk.Entry = lambda *a, **k: DummyEntry()
    dummy_tk.Button = lambda *a, **k: DummyWidget()
    dummy_tk.Checkbutton = lambda *a, **k: DummyWidget()
    dummy_tk.LabelFrame = lambda *a, **k: DummyWidget()
    dummy_tk._default_root = None

    dummy_ttk = SimpleNamespace()
    dummy_ttk.Treeview = DummyTreeview
    dummy_ttk.Style = DummyStyle
    dummy_ttk.Scrollbar = DummyScrollbar

    msg = MsgCapture()

    # Patch modules that import tkinter directly
    import modules.equipment as equipment_mod
    import modules.members as members_mod
    import modules.projects as projects_mod
    import modules.reporting as reporting_mod

    for mod in (equipment_mod, members_mod, projects_mod, reporting_mod):
        monkeypatch.setattr(mod, 'tk', dummy_tk)
        monkeypatch.setattr(mod, 'ttk', dummy_ttk)
        monkeypatch.setattr(mod, 'messagebox', msg)

    return msg


def test_equipment_menu_runs_and_handles_empty_db(patch_tkinter):
    import modules.equipment as equipment_mod
    # DB returns empty lists so menus should show info dialogs for missing data
    fake_db = FakeDB(responses={'FROM equipment': []})
    # Call the menu; should not raise
    equipment_mod.equipment_menu(fake_db)


def test_members_menu_add_update_delete_and_reports(patch_tkinter):
    import modules.members as members_mod
    # Simulate DB responses for refresh_table and grant member listing
    fake_db = FakeDB(responses={
        'FROM lab_member': [],
        'FROM works': []
    })
    members_mod.members_menu(fake_db)


def test_projects_menu_and_helpers(patch_tkinter):
    import modules.projects as projects_mod
    fake_db = FakeDB(responses={
        'FROM project': [],
        'FROM works': [],
        'FROM funds': []
    })
    projects_mod.projects_menu(fake_db)


def test_reporting_menu_queries(patch_tkinter):
    import modules.reporting as reporting_mod
    # Prepare fake rows as list of dicts and tuples to exercise both branches
    rows_publishers = [ {'mid':'M001','name':'ALICE','pubs':3}, {'mid':'M002','name':'BOB','pubs':1} ]
    rows_avg = [ {'major':'CS','pubs':4,'students':2} ]
    rows_top3 = [ {'member_mid':'M001','pubs':5} ]
    rows_grants = [ {'gid':'G001','source':'AGENCY','budget':1000,'start_date':None,'duration':12} ]
    rows_pubs = [ ('PUB001','TITLE','VENUE','2020-01-01','DOI-1') ]
    fake_db = FakeDB(responses={
        'published': rows_publishers,
        'FROM student': rows_avg,
        'FROM works': rows_top3,
        'FROM grants': rows_grants,
        'FROM publication': rows_pubs,
    })
    reporting_mod.reporting_menu(fake_db)


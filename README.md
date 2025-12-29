# RESEARCH LAB MANAGEMENT SYSTEM
This repository provides a small Python-based management system with modules for equipment, members, projects and reporting. It exposes a simple interactive menu (`menu.py`) to perform operations.

## Requirements

- Python 3.8+ (3.10+ recommended)
- No external dependencies required by default.
- PostgreSQL 

## Quick start

1. (Optional) create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Run the interactive menu:

```bash
python3 menu.py
```

The menu will guide you through creating and managing equipment, members, projects and reports.

## Project layout

- `menu.py` — main CLI entrypoint
- `create.py`, `insert.py`, `database.py`, `triggers.py` — DB and setup helpers
- `modules/` — core application modules
  - `equipment.py` — equipment-related functions
  - `members.py` — member management
  - `projects.py` — project handling
  - `reporting.py` — report generation
- `scripts/` — utility scripts

## Contributing

Open an issue or submit a pull request. Keep changes small and add tests where relevant.

## Screenshots

The repository includes a `screenshots/` folder with UI captures. Embed images by referencing the relative paths below.

- Main UI / List view:

![Main UI - list view](screenshots/lab_management_system_main.png)

- Projects management:

![Manage Projects](screenshots/manage_projects.png)

- Members management:

![Manage Members](screenshots/manage_members.png)

- Equipment management:

![Manage Equipment](screenshots/manage_equipment.png)

- Grants / Statistics view:

![Grant Statistics](screenshots/grant_statistics.png)

## Tests

There is a test suite in the `tests/` directory. The tests use `pytest` and `pytest-cov` to run and report coverage.

Run tests from the project root (use the repository virtualenv if available):

```bash
# install test deps if needed
pip install pytest pytest-cov

# run tests with coverage (ensure PYTHONPATH points to the repo root)
PYTHONPATH=$(pwd) .venv/bin/pytest -q --cov=. --cov-report=term-missing
```

See `tests/test_database.py` and `tests/test_menus.py` for examples covering the DB helper and UI menus.

````

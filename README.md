#RESEARCH LAB MANAGEMENT SYSTEM
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


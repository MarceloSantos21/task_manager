# 📝 Task Manager CLI

A command-line task manager built with Python and SQLite. Manage tasks with priorities, categories, deadlines and color-coded output — all from your terminal.

## Features
- ➕ Add tasks with priority (high/medium/low), category and due date
- 📋 List tasks with filters (priority, category, status)
- ✅ Mark tasks as complete
- 🗑️ Delete tasks
- 📊 View statistics
- ⚠️ Overdue task warnings (highlighted in red)
- 💾 Persistent storage with SQLite (no setup required)

## Requirements
```
Python 3.8+
No external libraries needed — uses only the standard library!
```

## Usage

```bash
# Add a task
python task_manager.py add "Fix login bug" -p high -c backend --due 2024-12-01

# List all tasks
python task_manager.py list

# List only pending high-priority tasks
python task_manager.py list --pending -p high

# Mark task #3 as done
python task_manager.py done 3

# Delete task #5
python task_manager.py delete 5

# View statistics
python task_manager.py stats
```

## Project Structure
```
1_task_manager/
├── task_manager.py   # Main application
├── tasks.db          # SQLite database (auto-created on first run)
└── README.md
```

## Skills Demonstrated
- SQLite with the `sqlite3` standard library
- Argparse for CLI interface design
- ANSI terminal colors and formatting
- CRUD operations and filtering
- Date handling and validation

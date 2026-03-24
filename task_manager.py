"""
Task Manager CLI
================
A command-line task manager with SQLite, priorities, deadlines and colors.
"""

import sqlite3
import argparse
from datetime import datetime, date
from typing import Optional

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PRIORITY_COLORS = {
    "high": RED,
    "medium": YELLOW,
    "low": GREEN,
}

DB_FILE = "tasks.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                description TEXT,
                priority    TEXT    NOT NULL DEFAULT 'medium',
                category    TEXT,
                due_date    TEXT,
                done        INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL
            )
        """)
        conn.commit()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def add_task(title: str, description: str = "", priority: str = "medium",
             category: str = "", due_date: Optional[str] = None):
    if priority not in ("high", "medium", "low"):
        print(f"{RED}Priority must be: high, medium or low.{RESET}")
        return

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (title, description, priority, category, due_date, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, priority, category, due_date,
             datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        conn.commit()
    print(f"{GREEN}✔ Task '{title}' added successfully!{RESET}")


def list_tasks(filter_done: Optional[bool] = None, priority: Optional[str] = None,
               category: Optional[str] = None):
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list = []

    if filter_done is not None:
        query += " AND done = ?"
        params.append(int(filter_done))
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    if not rows:
        print(f"{YELLOW}No tasks found.{RESET}")
        return

    _print_header()
    for row in rows:
        _print_row(row)
    print()


def complete_task(task_id: int):
    with get_connection() as conn:
        cur = conn.execute("UPDATE tasks SET done = 1 WHERE id = ? AND done = 0", (task_id,))
        conn.commit()
    if cur.rowcount:
        print(f"{GREEN}✔ Task #{task_id} marked as done!{RESET}")
    else:
        print(f"{YELLOW}Task #{task_id} not found or already done.{RESET}")


def delete_task(task_id: int):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    if cur.rowcount:
        print(f"{RED}Task #{task_id} deleted.{RESET}")
    else:
        print(f"{YELLOW}Task #{task_id} not found.{RESET}")


def show_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done = conn.execute("SELECT COUNT(*) FROM tasks WHERE done=1").fetchone()[0]
        pending = total - done
        high = conn.execute("SELECT COUNT(*) FROM tasks WHERE priority='high' AND done=0").fetchone()[0]

    print(f"\n{BOLD}{CYAN}📊 Statistics{RESET}")
    print(f"  Total tasks   : {total}")
    print(f"  {GREEN}Completed     : {done}{RESET}")
    print(f"  {YELLOW}Pending       : {pending}{RESET}")
    print(f"  {RED}High priority : {high}{RESET}\n")


# ── Display helpers ───────────────────────────────────────────────────────────

def _print_header():
    print(f"\n{BOLD}{CYAN}{'ID':<5} {'Title':<30} {'Priority':<10} {'Category':<15} {'Due':<12} {'Status'}{RESET}")
    print("─" * 82)


def _print_row(row):
    color = PRIORITY_COLORS.get(row["priority"], RESET)
    status = f"{GREEN}✔ Done{RESET}" if row["done"] else f"{YELLOW}Pending{RESET}"
    due = row["due_date"] or "—"

    # Warn if overdue
    if row["due_date"] and not row["done"]:
        try:
            if date.fromisoformat(row["due_date"]) < date.today():
                due = f"{RED}{due} ⚠{RESET}"
        except ValueError:
            pass

    title = row["title"][:28] + ".." if len(row["title"]) > 30 else row["title"]
    print(f"{row['id']:<5} {title:<30} {color}{row['priority']:<10}{RESET} "
          f"{(row['category'] or '—'):<15} {due:<12} {status}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    init_db()

    parser = argparse.ArgumentParser(
        prog="task_manager",
        description="📝 Task Manager CLI — Manage your tasks from the terminal",
    )
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("-d", "--description", default="", help="Task description")
    p_add.add_argument("-p", "--priority", default="medium",
                       choices=["high", "medium", "low"], help="Priority level")
    p_add.add_argument("-c", "--category", default="", help="Category / project tag")
    p_add.add_argument("--due", dest="due_date", metavar="YYYY-MM-DD", help="Due date")

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--done", action="store_true", help="Show only completed tasks")
    p_list.add_argument("--pending", action="store_true", help="Show only pending tasks")
    p_list.add_argument("-p", "--priority", choices=["high", "medium", "low"])
    p_list.add_argument("-c", "--category")

    # done
    p_done = sub.add_parser("done", help="Mark a task as completed")
    p_done.add_argument("id", type=int, help="Task ID")

    # delete
    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")

    # stats
    sub.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.title, args.description, args.priority, args.category, args.due_date)
    elif args.command == "list":
        filter_done = True if args.done else (False if args.pending else None)
        list_tasks(filter_done, args.priority, args.category)
    elif args.command == "done":
        complete_task(args.id)
    elif args.command == "delete":
        delete_task(args.id)
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

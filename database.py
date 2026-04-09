"""
Database layer for the Household Chore Tracker.
Uses SQLite for simple, file-based persistence.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chores.db")

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database schema."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#4A90D9',
                avatar TEXT NOT NULL DEFAULT '👤',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#6B7280',
                icon TEXT NOT NULL DEFAULT '📋',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                assigned_to INTEGER REFERENCES people(id) ON DELETE SET NULL,
                due_date DATE NOT NULL,
                due_time TEXT DEFAULT NULL,
                is_completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT NULL,
                recurrence TEXT DEFAULT NULL,  -- 'daily', 'weekly', 'biweekly', 'monthly', or NULL
                recurrence_parent_id INTEGER DEFAULT NULL,
                priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
            CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category_id);
        """)

def seed_defaults():
    """Seed default people and categories if empty."""
    with get_db() as conn:
        # Check if already seeded
        count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO people (name, color, avatar) VALUES (?, ?, ?)",
                [
                    ("Justin", "#4A90D9", "👨"),
                    ("Wife", "#E91E8A", "👩"),
                ]
            )

        count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO categories (name, color, icon) VALUES (?, ?, ?)",
                [
                    ("Cleaning", "#10B981", "🧹"),
                    ("Kitchen", "#F59E0B", "🍳"),
                    ("Laundry", "#8B5CF6", "👕"),
                    ("Yard Work", "#059669", "🌿"),
                    ("Errands", "#EF4444", "🚗"),
                    ("Pets", "#F97316", "🐾"),
                    ("Home Maintenance", "#6366F1", "🔧"),
                    ("Groceries", "#14B8A6", "🛒"),
                ]
            )

# --- CRUD: People ---

def get_people():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM people ORDER BY name").fetchall()]

def add_person(name, color, avatar="👤"):
    with get_db() as conn:
        conn.execute("INSERT INTO people (name, color, avatar) VALUES (?, ?, ?)", (name, color, avatar))

def update_person(person_id, name, color, avatar):
    with get_db() as conn:
        conn.execute("UPDATE people SET name=?, color=?, avatar=? WHERE id=?", (name, color, avatar, person_id))

def delete_person(person_id):
    with get_db() as conn:
        conn.execute("DELETE FROM people WHERE id=?", (person_id,))

# --- CRUD: Categories ---

def get_categories():
    with get_db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM categories ORDER BY name").fetchall()]

def add_category(name, color, icon="📋"):
    with get_db() as conn:
        conn.execute("INSERT INTO categories (name, color, icon) VALUES (?, ?, ?)", (name, color, icon))

def update_category(cat_id, name, color, icon):
    with get_db() as conn:
        conn.execute("UPDATE categories SET name=?, color=?, icon=? WHERE id=?", (name, color, icon, cat_id))

def delete_category(cat_id):
    with get_db() as conn:
        conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))

# --- CRUD: Tasks ---

def get_tasks_for_week(start_date: date):
    """Get all tasks for a 7-day window starting from start_date."""
    end_date = start_date + timedelta(days=6)
    with get_db() as conn:
        rows = conn.execute("""
            SELECT t.*, p.name as person_name, p.color as person_color, p.avatar as person_avatar,
                   c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM tasks t
            LEFT JOIN people p ON t.assigned_to = p.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.due_date BETWEEN ? AND ?
            ORDER BY t.due_date, t.due_time, t.priority DESC
        """, (start_date.isoformat(), end_date.isoformat())).fetchall()
        return [dict(r) for r in rows]

def get_tasks_for_date(target_date: date):
    """Get all tasks for a specific date."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT t.*, p.name as person_name, p.color as person_color, p.avatar as person_avatar,
                   c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM tasks t
            LEFT JOIN people p ON t.assigned_to = p.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.due_date = ?
            ORDER BY t.due_time, t.priority DESC
        """, (target_date.isoformat(),)).fetchall()
        return [dict(r) for r in rows]

def add_task(title, due_date, category_id=None, assigned_to=None, due_time=None,
             description="", recurrence=None, priority="medium"):
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO tasks (title, due_date, category_id, assigned_to, due_time,
                             description, recurrence, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, due_date, category_id, assigned_to, due_time, description, recurrence, priority))
        task_id = cursor.lastrowid

        # If recurring, generate future instances
        if recurrence:
            _generate_recurring_tasks(conn, task_id, title, due_date, category_id,
                                       assigned_to, due_time, description, recurrence, priority)
        return task_id

def _generate_recurring_tasks(conn, parent_id, title, start_date, category_id,
                                assigned_to, due_time, description, recurrence, priority, weeks_ahead=8):
    """Generate recurring task instances for the next N weeks."""
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    current = start_date
    for _ in range(weeks_ahead * 7 if recurrence == 'daily' else weeks_ahead):
        if recurrence == 'daily':
            current += timedelta(days=1)
        elif recurrence == 'weekly':
            current += timedelta(weeks=1)
        elif recurrence == 'biweekly':
            current += timedelta(weeks=2)
        elif recurrence == 'monthly':
            # Approximate: add 30 days
            current += timedelta(days=30)

        conn.execute("""
            INSERT INTO tasks (title, due_date, category_id, assigned_to, due_time,
                             description, recurrence, recurrence_parent_id, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, current.isoformat(), category_id, assigned_to, due_time,
              description, recurrence, parent_id, priority))

def update_task(task_id, **kwargs):
    """Update a task with given keyword arguments."""
    allowed = {'title', 'description', 'category_id', 'assigned_to', 'due_date',
               'due_time', 'is_completed', 'priority', 'recurrence'}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return

    if 'is_completed' in updates and updates['is_completed']:
        updates['completed_at'] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [task_id]

    with get_db() as conn:
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE id=?", values)

def delete_task(task_id, delete_future=False):
    """Delete a task. Optionally delete all future recurring instances."""
    with get_db() as conn:
        if delete_future:
            # Delete this task and all future instances from same recurrence chain
            task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if task:
                parent_id = task['recurrence_parent_id'] or task['id']
                conn.execute("""
                    DELETE FROM tasks
                    WHERE (id=? OR recurrence_parent_id=?) AND due_date >= ?
                """, (parent_id, parent_id, task['due_date']))
        else:
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))

def toggle_task_complete(task_id):
    """Toggle a task's completion status."""
    with get_db() as conn:
        task = conn.execute("SELECT is_completed FROM tasks WHERE id=?", (task_id,)).fetchone()
        if task:
            new_status = 0 if task['is_completed'] else 1
            completed_at = datetime.now().isoformat() if new_status else None
            conn.execute("UPDATE tasks SET is_completed=?, completed_at=? WHERE id=?",
                        (new_status, completed_at, task_id))

def get_stats(start_date: date, end_date: date):
    """Get completion stats for a date range."""
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE due_date BETWEEN ? AND ?",
            (start_date.isoformat(), end_date.isoformat())
        ).fetchone()[0]

        completed = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE due_date BETWEEN ? AND ? AND is_completed=1",
            (start_date.isoformat(), end_date.isoformat())
        ).fetchone()[0]

        by_person = conn.execute("""
            SELECT p.name, p.color, p.avatar,
                   COUNT(*) as total,
                   SUM(CASE WHEN t.is_completed=1 THEN 1 ELSE 0 END) as done
            FROM tasks t
            JOIN people p ON t.assigned_to = p.id
            WHERE t.due_date BETWEEN ? AND ?
            GROUP BY p.id
        """, (start_date.isoformat(), end_date.isoformat())).fetchall()

        return {
            "total": total,
            "completed": completed,
            "by_person": [dict(r) for r in by_person]
        }

def get_equity_stats(weeks_back=4):
    """
    Get workload balance stats across household members over recent weeks.
    Designed to be blameless — focuses on distribution, not judgment.
    """
    end = date.today()
    start = end - timedelta(weeks=weeks_back)

    with get_db() as conn:
        # Tasks assigned per person
        assigned = conn.execute("""
            SELECT p.id, p.name, p.color, p.avatar,
                   COUNT(*) as assigned_count,
                   SUM(CASE WHEN t.is_completed=1 THEN 1 ELSE 0 END) as completed_count
            FROM tasks t
            JOIN people p ON t.assigned_to = p.id
            WHERE t.due_date BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY p.name
        """, (start.isoformat(), end.isoformat())).fetchall()

        # Tasks by category per person
        by_category = conn.execute("""
            SELECT p.name as person_name, p.color as person_color,
                   c.name as category_name, c.icon as category_icon, c.color as category_color,
                   COUNT(*) as count
            FROM tasks t
            JOIN people p ON t.assigned_to = p.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.due_date BETWEEN ? AND ?
            GROUP BY p.id, c.id
            ORDER BY p.name, count DESC
        """, (start.isoformat(), end.isoformat())).fetchall()

        # Weekly trend per person
        weekly_trend = conn.execute("""
            SELECT p.name, p.color,
                   strftime('%Y-W%W', t.due_date) as week,
                   COUNT(*) as count
            FROM tasks t
            JOIN people p ON t.assigned_to = p.id
            WHERE t.due_date BETWEEN ? AND ?
            GROUP BY p.id, week
            ORDER BY week, p.name
        """, (start.isoformat(), end.isoformat())).fetchall()

        # Unassigned tasks
        unassigned = conn.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE assigned_to IS NULL AND due_date BETWEEN ? AND ?
        """, (start.isoformat(), end.isoformat())).fetchone()[0]

        return {
            "assigned": [dict(r) for r in assigned],
            "by_category": [dict(r) for r in by_category],
            "weekly_trend": [dict(r) for r in weekly_trend],
            "unassigned": unassigned,
            "period_start": start,
            "period_end": end,
        }

# Initialize on import
init_db()
seed_defaults()

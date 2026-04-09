"""
Database layer for the Household Chore Tracker.
Uses Supabase (PostgreSQL) for cloud-based persistence.
"""

import streamlit as st
import os
from datetime import datetime, date, timedelta
from supabase import create_client, Client

# Initialize Supabase client
def _get_supabase_client() -> Client:
    """Get or create a Supabase client with credentials from secrets or env."""
    # Try st.secrets first (for Streamlit Cloud), then env vars, then hardcoded defaults
    supabase_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL") or "https://zlbucvsbihigtqpeuxgw.supabase.co"
    supabase_key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpsYnVjdnNiaWhpZ3RxcGV1eGd3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3Njg3MTksImV4cCI6MjA5MTM0NDcxOX0.0OYOf30DCYxYq9pnOehFe_JciUxUsmPiKq1or4v9ujA"

    return create_client(supabase_url, supabase_key)

@st.cache_resource
def get_supabase():
    """Cached Supabase client."""
    return _get_supabase_client()

def init_db():
    """Initialize the database schema (tables should already exist in Supabase)."""
    # Tables are pre-created in Supabase, but we'll seed defaults if needed
    seed_defaults()

def seed_defaults():
    """Seed default people and categories if empty."""
    supabase = get_supabase()

    # Check if people table is empty
    people_count = supabase.table("people").select("id", count="exact").execute()
    if people_count.count == 0:
        supabase.table("people").insert([
            {"name": "Justin", "color": "#4A90D9", "avatar": "👨"},
            {"name": "Wife", "color": "#E91E8A", "avatar": "👩"},
        ]).execute()

    # Check if categories table is empty
    categories_count = supabase.table("categories").select("id", count="exact").execute()
    if categories_count.count == 0:
        supabase.table("categories").insert([
            {"name": "Cleaning", "color": "#10B981", "icon": "🧹"},
            {"name": "Kitchen", "color": "#F59E0B", "icon": "🍳"},
            {"name": "Laundry", "color": "#8B5CF6", "icon": "👕"},
            {"name": "Yard Work", "color": "#059669", "icon": "🌿"},
            {"name": "Errands", "color": "#EF4444", "icon": "🚗"},
            {"name": "Pets", "color": "#F97316", "icon": "🐾"},
            {"name": "Home Maintenance", "color": "#6366F1", "icon": "🔧"},
            {"name": "Groceries", "color": "#14B8A6", "icon": "🛒"},
        ]).execute()

# --- CRUD: People ---

def get_people():
    """Get all people, ordered by name."""
    supabase = get_supabase()
    response = supabase.table("people").select("*").order("name").execute()
    return response.data if response.data else []

def add_person(name, color, avatar="👤"):
    """Add a new person."""
    supabase = get_supabase()
    supabase.table("people").insert({
        "name": name,
        "color": color,
        "avatar": avatar
    }).execute()

def update_person(person_id, name, color, avatar):
    """Update a person's details."""
    supabase = get_supabase()
    supabase.table("people").update({
        "name": name,
        "color": color,
        "avatar": avatar
    }).eq("id", person_id).execute()

def delete_person(person_id):
    """Delete a person."""
    supabase = get_supabase()
    supabase.table("people").delete().eq("id", person_id).execute()

# --- CRUD: Categories ---

def get_categories():
    """Get all categories, ordered by name."""
    supabase = get_supabase()
    response = supabase.table("categories").select("*").order("name").execute()
    return response.data if response.data else []

def add_category(name, color, icon="📋"):
    """Add a new category."""
    supabase = get_supabase()
    supabase.table("categories").insert({
        "name": name,
        "color": color,
        "icon": icon
    }).execute()

def update_category(cat_id, name, color, icon):
    """Update a category's details."""
    supabase = get_supabase()
    supabase.table("categories").update({
        "name": name,
        "color": color,
        "icon": icon
    }).eq("id", cat_id).execute()

def delete_category(cat_id):
    """Delete a category."""
    supabase = get_supabase()
    supabase.table("categories").delete().eq("id", cat_id).execute()

# --- CRUD: Tasks ---

def _merge_task_with_relations(task, people_map, categories_map):
    """Merge task with related person and category data."""
    if task.get("assigned_to") and task["assigned_to"] in people_map:
        person = people_map[task["assigned_to"]]
        task["person_name"] = person["name"]
        task["person_color"] = person["color"]
        task["person_avatar"] = person["avatar"]
    else:
        task["person_name"] = None
        task["person_color"] = None
        task["person_avatar"] = None

    if task.get("category_id") and task["category_id"] in categories_map:
        category = categories_map[task["category_id"]]
        task["category_name"] = category["name"]
        task["category_color"] = category["color"]
        task["category_icon"] = category["icon"]
    else:
        task["category_name"] = None
        task["category_color"] = None
        task["category_icon"] = None

    return task

def get_tasks_for_week(start_date: date):
    """Get all tasks for a 7-day window starting from start_date."""
    end_date = start_date + timedelta(days=6)
    supabase = get_supabase()

    # Fetch tasks in date range
    response = supabase.table("tasks").select("*").gte("due_date", start_date.isoformat()).lte("due_date", end_date.isoformat()).order("due_date").order("due_time").order("priority", desc=True).execute()
    tasks = response.data if response.data else []

    # Fetch all people and categories for mapping
    people_response = supabase.table("people").select("id, name, color, avatar").execute()
    people_map = {p["id"]: p for p in people_response.data} if people_response.data else {}

    categories_response = supabase.table("categories").select("id, name, color, icon").execute()
    categories_map = {c["id"]: c for c in categories_response.data} if categories_response.data else {}

    # Merge relations
    return [_merge_task_with_relations(task, people_map, categories_map) for task in tasks]

def get_tasks_for_date(target_date: date):
    """Get all tasks for a specific date."""
    supabase = get_supabase()

    # Fetch tasks for the specific date
    response = supabase.table("tasks").select("*").eq("due_date", target_date.isoformat()).order("due_time").order("priority", desc=True).execute()
    tasks = response.data if response.data else []

    # Fetch all people and categories for mapping
    people_response = supabase.table("people").select("id, name, color, avatar").execute()
    people_map = {p["id"]: p for p in people_response.data} if people_response.data else {}

    categories_response = supabase.table("categories").select("id, name, color, icon").execute()
    categories_map = {c["id"]: c for c in categories_response.data} if categories_response.data else {}

    # Merge relations
    return [_merge_task_with_relations(task, people_map, categories_map) for task in tasks]

def add_task(title, due_date, category_id=None, assigned_to=None, due_time=None,
             description="", recurrence=None, priority="medium"):
    """Add a new task and generate recurring instances if applicable."""
    supabase = get_supabase()

    # Insert the task
    response = supabase.table("tasks").insert({
        "title": title,
        "due_date": due_date.isoformat() if isinstance(due_date, date) else due_date,
        "category_id": category_id,
        "assigned_to": assigned_to,
        "due_time": due_time,
        "description": description,
        "recurrence": recurrence,
        "priority": priority
    }).execute()

    task_id = response.data[0]["id"] if response.data else None

    # If recurring, generate future instances
    if recurrence and task_id:
        _generate_recurring_tasks(task_id, title, due_date, category_id,
                                  assigned_to, due_time, description, recurrence, priority)

    return task_id

def _generate_recurring_tasks(parent_id, title, start_date, category_id,
                              assigned_to, due_time, description, recurrence, priority, weeks_ahead=8):
    """Generate recurring task instances for the next N weeks."""
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    supabase = get_supabase()
    tasks_to_insert = []

    current = start_date
    for _ in range(weeks_ahead * 7 if recurrence == 'daily' else weeks_ahead):
        if recurrence == 'daily':
            current += timedelta(days=1)
        elif recurrence == 'weekly':
            current += timedelta(weeks=1)
        elif recurrence == 'biweekly':
            current += timedelta(weeks=2)
        elif recurrence == 'monthly':
            current += timedelta(days=30)

        tasks_to_insert.append({
            "title": title,
            "due_date": current.isoformat(),
            "category_id": category_id,
            "assigned_to": assigned_to,
            "due_time": due_time,
            "description": description,
            "recurrence": recurrence,
            "parent_task_id": parent_id,
            "priority": priority
        })

    # Insert all at once
    if tasks_to_insert:
        supabase.table("tasks").insert(tasks_to_insert).execute()

def update_task(task_id, **kwargs):
    """Update a task with given keyword arguments."""
    allowed = {'title', 'description', 'category_id', 'assigned_to', 'due_date',
               'due_time', 'is_completed', 'priority', 'recurrence'}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return

    # Handle date/datetime conversions
    if 'due_date' in updates and isinstance(updates['due_date'], date):
        updates['due_date'] = updates['due_date'].isoformat()

    if 'is_completed' in updates and updates['is_completed']:
        updates['completed_at'] = datetime.now().isoformat()

    supabase = get_supabase()
    supabase.table("tasks").update(updates).eq("id", task_id).execute()

def delete_task(task_id, delete_future=False):
    """Delete a task. Optionally delete all future recurring instances."""
    supabase = get_supabase()

    if delete_future:
        # Fetch the task to get recurrence info
        response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if response.data:
            task = response.data[0]
            parent_id = task.get("parent_task_id") or task["id"]
            task_date = task["due_date"]

            # Delete future instances that share the same parent
            supabase.table("tasks").delete().eq(
                "parent_task_id", parent_id
            ).gte("due_date", task_date).execute()

            # Also delete the parent task itself if it's on or after task_date
            parent_resp = supabase.table("tasks").select("due_date").eq("id", parent_id).execute()
            if parent_resp.data and parent_resp.data[0]["due_date"] >= task_date:
                supabase.table("tasks").delete().eq("id", parent_id).execute()

            # Delete the task itself (in case it IS the parent or has no parent_task_id)
            supabase.table("tasks").delete().eq("id", task_id).execute()
    else:
        supabase.table("tasks").delete().eq("id", task_id).execute()

def toggle_task_complete(task_id):
    """Toggle a task's completion status."""
    supabase = get_supabase()

    # Fetch current task
    response = supabase.table("tasks").select("is_completed").eq("id", task_id).execute()
    if response.data:
        task = response.data[0]
        new_status = not task["is_completed"]
        completed_at = datetime.now().isoformat() if new_status else None

        supabase.table("tasks").update({
            "is_completed": new_status,
            "completed_at": completed_at
        }).eq("id", task_id).execute()

def get_stats(start_date: date, end_date: date):
    """Get completion stats for a date range."""
    supabase = get_supabase()

    # Total tasks in range
    total_response = supabase.table("tasks").select("id", count="exact").gte("due_date", start_date.isoformat()).lte("due_date", end_date.isoformat()).execute()
    total = total_response.count if total_response.count is not None else 0

    # Completed tasks in range
    completed_response = supabase.table("tasks").select("id", count="exact").gte("due_date", start_date.isoformat()).lte("due_date", end_date.isoformat()).eq("is_completed", True).execute()
    completed = completed_response.count if completed_response.count is not None else 0

    # Tasks by person
    all_tasks_response = supabase.table("tasks").select("*").gte("due_date", start_date.isoformat()).lte("due_date", end_date.isoformat()).execute()
    all_tasks = all_tasks_response.data if all_tasks_response.data else []

    people_response = supabase.table("people").select("*").execute()
    people = people_response.data if people_response.data else []

    by_person = []
    for person in people:
        person_tasks = [t for t in all_tasks if t.get("assigned_to") == person["id"]]
        if person_tasks:
            total_count = len(person_tasks)
            done_count = sum(1 for t in person_tasks if t.get("is_completed"))
            by_person.append({
                "name": person["name"],
                "color": person["color"],
                "avatar": person["avatar"],
                "total": total_count,
                "done": done_count
            })

    return {
        "total": total,
        "completed": completed,
        "by_person": by_person
    }

def get_equity_stats(weeks_back=4):
    """
    Get workload balance stats across household members over recent weeks.
    Designed to be blameless — focuses on distribution, not judgment.
    """
    end = date.today()
    start = end - timedelta(weeks=weeks_back)

    supabase = get_supabase()

    # Fetch all relevant tasks and people
    tasks_response = supabase.table("tasks").select("*").gte("due_date", start.isoformat()).lte("due_date", end.isoformat()).execute()
    tasks = tasks_response.data if tasks_response.data else []

    people_response = supabase.table("people").select("*").execute()
    people = people_response.data if people_response.data else []

    categories_response = supabase.table("categories").select("*").execute()
    categories = categories_response.data if categories_response.data else []

    # Tasks assigned per person
    assigned = []
    for person in people:
        person_tasks = [t for t in tasks if t.get("assigned_to") == person["id"]]
        if person_tasks:
            assigned_count = len(person_tasks)
            completed_count = sum(1 for t in person_tasks if t.get("is_completed"))
            assigned.append({
                "id": person["id"],
                "name": person["name"],
                "color": person["color"],
                "avatar": person["avatar"],
                "assigned_count": assigned_count,
                "completed_count": completed_count
            })

    # Tasks by category per person
    by_category = []
    for person in people:
        person_tasks = [t for t in tasks if t.get("assigned_to") == person["id"]]
        if person_tasks:
            # Group by category
            category_counts = {}
            for task in person_tasks:
                cat_id = task.get("category_id")
                if cat_id not in category_counts:
                    category_counts[cat_id] = 0
                category_counts[cat_id] += 1

            # Convert to entries with category details
            for cat_id, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                category = next((c for c in categories if c["id"] == cat_id), None)
                by_category.append({
                    "person_name": person["name"],
                    "person_color": person["color"],
                    "category_name": category["name"] if category else None,
                    "category_icon": category["icon"] if category else None,
                    "category_color": category["color"] if category else None,
                    "count": count
                })

    # Weekly trend per person (simplified: group by week number)
    weekly_trend = []
    for person in people:
        person_tasks = [t for t in tasks if t.get("assigned_to") == person["id"]]
        if person_tasks:
            # Group by ISO calendar week
            week_counts = {}
            for task in person_tasks:
                task_date = date.fromisoformat(task["due_date"])
                week_key = task_date.isocalendar()[1]  # Week number
                if week_key not in week_counts:
                    week_counts[week_key] = 0
                week_counts[week_key] += 1

            for week, count in sorted(week_counts.items()):
                weekly_trend.append({
                    "name": person["name"],
                    "color": person["color"],
                    "week": f"W{week:02d}",
                    "count": count
                })

    # Unassigned tasks
    unassigned = sum(1 for t in tasks if t.get("assigned_to") is None)

    return {
        "assigned": assigned,
        "by_category": by_category,
        "weekly_trend": weekly_trend,
        "unassigned": unassigned,
        "period_start": start,
        "period_end": end,
    }

# Initialize on import
init_db()

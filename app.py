"""
🏠 Home Command Center — Household Chore & Task Tracker
A Skylight-inspired local web app for managing household chores and tasks.
"""

import streamlit as st
from datetime import date, timedelta, datetime, time
import database as db

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Home Command Center",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Dark/Gray Theme CSS — IMPROVED
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* ---- Base dark theme — softer colors ---- */
    .stApp { background-color: #1e1e32; color: #e0e0e0; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    

    /* Force all Streamlit text white */
    .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp .stMarkdown, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #e0e0e0 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #16213e; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stMarkdown hr { border-color: #334155; }

    /* Expander styling */
    [data-testid="stExpander"] { border-color: #334155 !important; }
    [data-testid="stExpander"] summary span { color: #cbd5e1 !important; }

    /* Input fields */
    .stTextInput input, .stSelectbox select, .stDateInput input {
        background-color: #222640 !important; color: #e0e0e0 !important;
        border-color: #475569 !important;
    }
    [data-testid="stDateInput"] input { background-color: #222640 !important; color: #e0e0e0 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #16213e; border-radius: 8px; padding: 0.25rem; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent; color: #94a3b8 !important;
        border-radius: 6px; padding: 0.5rem 1.5rem; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f3460 !important; color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px; background-color: #222640; color: #e0e0e0;
        border: 1px solid #475569;
    }
    .stButton > button:hover { background-color: #334155; border-color: #64748b; }
    .stButton > button[kind="primary"] {
        background-color: #0f3460; color: white; border: 1px solid #1a5276;
    }
    .stButton > button[kind="primary"]:hover { background-color: #1a5276; }

    /* Info boxes */
    [data-testid="stAlert"] { background-color: #222640; color: #94a3b8; border: 1px solid #334155; }

    /* ---- Top banner ---- */
    .top-banner {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        color: #f1f5f9; padding: 1.2rem 2rem; border-radius: 12px; margin-bottom: 1rem;
        display: flex; justify-content: space-between; align-items: center;
        border: 1px solid #1a5276;
    }
    .top-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: #f1f5f9 !important; }
    .top-banner .date-display { font-size: 1.1rem; color: #94a3b8 !important; }

    /* ---- Today's Focus Section ---- */
    .todays-focus {
        background: linear-gradient(135deg, #1a3a52, #0f3460);
        border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 1.5rem;
        border: 1px solid #1a5276; display: flex; align-items: center; gap: 1rem;
    }
    .todays-focus .focus-icon { font-size: 1.8rem; }
    .todays-focus .focus-text h3 { margin: 0; color: #38bdf8 !important; font-size: 1.1rem; }
    .todays-focus .focus-text p { margin: 0.2rem 0 0 0; color: #94a3b8 !important; font-size: 0.9rem; }

    /* ---- Day column headers ---- */
    .day-header {
        text-align: center; padding: 0.6rem 0.3rem; border-radius: 10px;
        margin-bottom: 0.5rem; font-weight: 600;
    }
    .day-header.today {
        background: linear-gradient(135deg, #0f3460, #1a5276);
        color: #ffffff; border: 1px solid #2980b9;
    }
    .day-header.other { background: #222640; color: #94a3b8; border: 1px solid #334155; }
    .day-header .day-name {
        font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;
        color: inherit !important;
    }
    .day-header .day-num { font-size: 1.4rem; font-weight: 700; color: inherit !important; }

    /* ---- Task cards ---- */
    .task-card {
        border-radius: 10px; padding: 0.5rem 0.6rem; margin-bottom: 0.5rem;
        border-left: 4px solid; background: #222640;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3); font-size: 0.85rem;
        transition: transform 0.1s; cursor: pointer;
    }
    .task-card:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    .task-card.completed { opacity: 0.35; text-decoration: line-through; }
    .task-card.completed .task-title::before { content: "✓ "; color: #10b981; }
    .task-card .task-title { font-weight: 600; margin-bottom: 0.2rem; color: #f1f5f9 !important; }
    .task-card .task-meta {
        display: flex; justify-content: space-between; align-items: center;
        font-size: 0.75rem; color: #94a3b8 !important;
    }
    .task-card .person-badge {
        display: inline-flex; align-items: center; gap: 0.25rem;
        padding: 0.1rem 0.4rem; border-radius: 12px; font-size: 0.7rem; font-weight: 500;
    }
    .priority-high { border-right: 3px solid #ef4444; }
    .priority-low { border-right: 3px solid #64748b; }

    /* ---- Add task form card ---- */
    .add-task-card {
        background: linear-gradient(135deg, #222640, #1e293b);
        border-radius: 12px; padding: 1.5rem;
        border: 1px solid #334155; margin-bottom: 1.5rem;
    }
    .add-task-card h3 { margin-top: 0; color: #38bdf8 !important; }

    /* ---- Stat cards ---- */
    .stat-card {
        background: #222640; border-radius: 12px; padding: 1rem; text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3); border: 1px solid #334155;
    }
    .stat-card .stat-number { font-size: 2rem; font-weight: 700; color: #38bdf8 !important; }
    .stat-card .stat-label { font-size: 0.85rem; color: #94a3b8 !important; }

    /* ---- Progress bars ---- */
    .progress-container {
        background: #334155; border-radius: 999px; height: 10px; overflow: hidden; margin: 0.5rem 0;
    }
    .progress-fill {
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, #0ea5e9, #38bdf8); transition: width 0.3s;
    }

    /* ---- Chips & tags ---- */
    .person-chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.3rem 0.7rem; border-radius: 20px; font-size: 0.85rem;
        font-weight: 500; margin: 0.2rem; color: white !important;
    }
    .cat-tag {
        display: inline-flex; align-items: center; gap: 0.2rem;
        padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.7rem; font-weight: 500;
    }

    /* ---- Empty states ---- */
    .empty-day {
        color: #64748b !important; font-style: italic; font-size: 0.8rem;
        padding: 1rem 0; text-align: center;
    }
    .empty-day-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }

    /* ---- Misc ---- */
    .recurrence-badge {
        font-size: 0.65rem; background: #1e3a5f; color: #7dd3fc !important;
        padding: 0.1rem 0.35rem; border-radius: 4px;
    }
    .stCheckbox label span { color: #cbd5e1 !important; }

    /* ---- Mobile spacing improvements ---- */
    @media (max-width: 768px) {
        .task-card {
            padding: 0.4rem 0.5rem;
            font-size: 0.8rem;
        }
        .day-header {
            padding: 0.4rem 0.2rem;
        }
        .top-banner {
            flex-direction: column;
            gap: 0.5rem;
            padding: 1rem;
        }
        .top-banner h1 {
            font-size: 1.4rem;
        }
        .add-task-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "current_week_start" not in st.session_state:
    today = date.today()
    st.session_state.current_week_start = today - timedelta(days=today.weekday())

if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

if "calendar_view" not in st.session_state:
    st.session_state.calendar_view = "week"

if "current_month" not in st.session_state:
    st.session_state.current_month = date.today().replace(day=1)

if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today()

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=2)
def load_people():
    return db.get_people()

@st.cache_data(ttl=2)
def load_categories():
    return db.get_categories()

def load_week_tasks(start_date):
    return db.get_tasks_for_week(start_date)

def load_day_tasks(target_date):
    return db.get_tasks_for_date(target_date)

@st.cache_data(ttl=2)
def load_month_tasks(year, month):
    return db.get_tasks_for_month(year, month)

@st.cache_data(ttl=2)
def load_grocery_items():
    return db.get_grocery_items()

# ---------------------------------------------------------------------------
# TOP BANNER
# ---------------------------------------------------------------------------
today = date.today()
st.markdown(f"""
<div class="top-banner">
    <div><h1>🏠 Home Command Center</h1></div>
    <div class="date-display">📅 {today.strftime('%A, %B %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    with st.expander("👥 Household Members", expanded=False):
        people = load_people()
        for p in people:
            cols = st.columns([1, 3, 1])
            with cols[0]:
                st.write(p['avatar'])
            with cols[1]:
                st.markdown(f"<span class='person-chip' style='background:{p['color']}'>{p['name']}</span>",
                           unsafe_allow_html=True)
            with cols[2]:
                if st.button("🗑️", key=f"del_person_{p['id']}", help=f"Remove {p['name']}"):
                    db.delete_person(p['id'])
                    st.cache_data.clear()
                    st.toast(f"Removed {p['name']}")
                    st.rerun()

        st.markdown("---")
        st.markdown("**Add Member**")
        new_name = st.text_input("Name", key="new_person_name", placeholder="e.g. Alex")
        new_color = st.color_picker("Color", value="#4A90D9", key="new_person_color")
        new_avatar = st.selectbox("Avatar", ["👨", "👩", "👦", "👧", "🧑", "👴", "👵"],
                                  key="new_person_avatar")
        if st.button("➕ Add Member", key="add_person_btn"):
            if new_name:
                db.add_person(new_name.strip(), new_color, new_avatar)
                st.cache_data.clear()
                st.toast(f"Added {new_name}!")
                st.rerun()

    with st.expander("🏷️ Categories", expanded=False):
        categories = load_categories()
        for c in categories:
            cols = st.columns([1, 3, 1])
            with cols[0]:
                st.write(c['icon'])
            with cols[1]:
                st.markdown(f"<span class='cat-tag' style='background:{c['color']}30; color:{c['color']}'>{c['name']}</span>",
                           unsafe_allow_html=True)
            with cols[2]:
                if st.button("🗑️", key=f"del_cat_{c['id']}", help=f"Remove {c['name']}"):
                    db.delete_category(c['id'])
                    st.cache_data.clear()
                    st.toast(f"Removed {c['name']}")
                    st.rerun()

        st.markdown("---")
        st.markdown("**Add Category**")
        cat_name = st.text_input("Name", key="new_cat_name", placeholder="e.g. Cooking")
        cat_color = st.color_picker("Color", value="#6B7280", key="new_cat_color")
        cat_icon = st.text_input("Icon (emoji)", value="📋", key="new_cat_icon")
        if st.button("➕ Add Category", key="add_cat_btn"):
            if cat_name:
                db.add_category(cat_name.strip(), cat_color, cat_icon)
                st.cache_data.clear()
                st.toast(f"Added {cat_name}!")
                st.rerun()

    st.markdown("---")

    # Weekly Stats
    st.markdown("## 📊 This Week")
    week_start = st.session_state.current_week_start
    week_end = week_start + timedelta(days=6)
    stats = db.get_stats(week_start, week_end)

    if stats['total'] > 0:
        pct = int(stats['completed'] / stats['total'] * 100)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['completed']}/{stats['total']}</div>
            <div class="stat-label">Tasks Completed</div>
            <div class="progress-container">
                <div class="progress-fill" style="width: {pct}%"></div>
            </div>
            <div class="stat-label">{pct}% done</div>
        </div>
        """, unsafe_allow_html=True)

        if stats['by_person']:
            st.markdown("#### By Person")
            for bp in stats['by_person']:
                p_pct = int(bp['done'] / bp['total'] * 100) if bp['total'] > 0 else 0
                st.markdown(f"""
                <div style="margin: 0.3rem 0;">
                    <span style="color:#cbd5e1 !important;">{bp['avatar']} {bp['name']}: {bp['done']}/{bp['total']}</span>
                    <div class="progress-container">
                        <div class="progress-fill" style="width: {p_pct}%; background: {bp['color']}"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tasks this week yet!")

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab_calendar, tab_grocery, tab_balance = st.tabs(["📅 Calendar", "🛒 Grocery List", "⚖️ Balance Board"])

# ===========================================================================
# TAB 1: WEEKLY CALENDAR
# ===========================================================================
with tab_calendar:
    # View mode selector
    view_cols = st.columns([1, 1, 1, 3, 1])
    with view_cols[0]:
        if st.button("Day", use_container_width=True,
                      type="primary" if st.session_state.calendar_view == "day" else "secondary"):
            st.session_state.calendar_view = "day"
            st.rerun()
    with view_cols[1]:
        if st.button("Week", use_container_width=True,
                      type="primary" if st.session_state.calendar_view == "week" else "secondary"):
            st.session_state.calendar_view = "week"
            st.rerun()
    with view_cols[2]:
        if st.button("Month", use_container_width=True,
                      type="primary" if st.session_state.calendar_view == "month" else "secondary"):
            st.session_state.calendar_view = "month"
            st.rerun()
    with view_cols[3]:
        pass
    with view_cols[4]:
        if st.button("➕ Add Task", use_container_width=True, type="primary"):
            st.session_state.show_add_task = not st.session_state.show_add_task
            st.rerun()

    # --- Navigation for each view ---
    if st.session_state.calendar_view == "week":
        nav_cols = st.columns([1, 1, 3, 1])
        with nav_cols[0]:
            if st.button("⬅️ Prev", use_container_width=True, key="prev_week"):
                st.session_state.current_week_start -= timedelta(weeks=1)
                st.rerun()
        with nav_cols[1]:
            if st.button("📍 Today", use_container_width=True, key="today_week"):
                st.session_state.current_week_start = today - timedelta(days=today.weekday())
                st.rerun()
        with nav_cols[2]:
            ws = st.session_state.current_week_start
            we = ws + timedelta(days=6)
            st.markdown(
                f"<div style='text-align:center; font-size:1.2rem; font-weight:600; padding-top:0.3rem; color:#f1f5f9 !important;'>"
                f"{ws.strftime('%b %d')} — {we.strftime('%b %d, %Y')}</div>",
                unsafe_allow_html=True
            )
        with nav_cols[3]:
            if st.button("Next ➡️", use_container_width=True, key="next_week"):
                st.session_state.current_week_start += timedelta(weeks=1)
                st.rerun()

    elif st.session_state.calendar_view == "day":
        nav_cols = st.columns([1, 1, 3, 1])
        with nav_cols[0]:
            if st.button("⬅️ Prev", use_container_width=True, key="prev_day"):
                st.session_state.selected_day -= timedelta(days=1)
                st.rerun()
        with nav_cols[1]:
            if st.button("📍 Today", use_container_width=True, key="today_day"):
                st.session_state.selected_day = today
                st.rerun()
        with nav_cols[2]:
            sd = st.session_state.selected_day
            st.markdown(
                f"<div style='text-align:center; font-size:1.2rem; font-weight:600; padding-top:0.3rem; color:#f1f5f9 !important;'>"
                f"{sd.strftime('%A, %B %d, %Y')}</div>",
                unsafe_allow_html=True
            )
        with nav_cols[3]:
            if st.button("Next ➡️", use_container_width=True, key="next_day"):
                st.session_state.selected_day += timedelta(days=1)
                st.rerun()

    elif st.session_state.calendar_view == "month":
        nav_cols = st.columns([1, 1, 3, 1])
        with nav_cols[0]:
            if st.button("⬅️ Prev", use_container_width=True, key="prev_month"):
                cm = st.session_state.current_month
                st.session_state.current_month = (cm.replace(day=1) - timedelta(days=1)).replace(day=1)
                st.rerun()
        with nav_cols[1]:
            if st.button("📍 Today", use_container_width=True, key="today_month"):
                st.session_state.current_month = today.replace(day=1)
                st.rerun()
        with nav_cols[2]:
            cm = st.session_state.current_month
            st.markdown(
                f"<div style='text-align:center; font-size:1.2rem; font-weight:600; padding-top:0.3rem; color:#f1f5f9 !important;'>"
                f"{cm.strftime('%B %Y')}</div>",
                unsafe_allow_html=True
            )
        with nav_cols[3]:
            if st.button("Next ➡️", use_container_width=True, key="next_month"):
                cm = st.session_state.current_month
                next_m = cm.replace(day=28) + timedelta(days=4)
                st.session_state.current_month = next_m.replace(day=1)
                st.rerun()

    # ===== WEEK VIEW =====
    if st.session_state.calendar_view == "week":

        # Today's focus section
        week_start = st.session_state.current_week_start
    today_tasks = [t for t in load_week_tasks(week_start) if date.fromisoformat(t['due_date']) == today]
    todays_count = len([t for t in today_tasks if not t['is_completed']])

    if todays_count > 0 or len(today_tasks) > 0:
        completed_count = len([t for t in today_tasks if t['is_completed']])
        focus_msg = f"You have {todays_count} task{'s' if todays_count != 1 else ''} today"
        if completed_count > 0:
            focus_msg += f" ({completed_count} done)"
        st.markdown(f"""
        <div class="todays-focus">
            <div class="focus-icon">🎯</div>
            <div class="focus-text">
                <h3>Today's Focus</h3>
                <p>{focus_msg}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Add task form — polished card style
    if st.session_state.show_add_task:
        st.markdown('<div class="add-task-card">', unsafe_allow_html=True)
        st.markdown("### ✏️ New Task")
        people = load_people()
        categories = load_categories()

        form_cols = st.columns([2, 1, 1, 1])
        with form_cols[0]:
            task_title = st.text_input("What needs to be done?", placeholder="e.g. Vacuum living room")
        with form_cols[1]:
            task_date = st.date_input("Due Date", value=today)
        with form_cols[2]:
            use_time = st.checkbox("Set time?", value=False)
            task_time = None
            if use_time:
                task_time = st.time_input("Time", value=time(9, 0))
        with form_cols[3]:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)

        form_cols2 = st.columns([1, 1, 1, 1])
        with form_cols2[0]:
            person_options = {p['id']: f"{p['avatar']} {p['name']}" for p in people}
            person_options[None] = "👤 Unassigned"
            assigned = st.selectbox("Assign to", options=list(person_options.keys()),
                                     format_func=lambda x: person_options[x])
        with form_cols2[1]:
            cat_options = {c['id']: f"{c['icon']} {c['name']}" for c in categories}
            cat_options[None] = "📋 No Category"
            category = st.selectbox("Category", options=list(cat_options.keys()),
                                     format_func=lambda x: cat_options[x])
        with form_cols2[2]:
            recurrence = st.selectbox("Repeat", [None, "daily", "weekly", "biweekly", "monthly"],
                                       format_func=lambda x: {
                                           None: "🔂 No repeat",
                                           "daily": "📆 Daily",
                                           "weekly": "🗓️ Weekly",
                                           "biweekly": "📅 Every 2 weeks",
                                           "monthly": "📅 Monthly"
                                       }.get(x, x))
        with form_cols2[3]:
            description = st.text_input("Notes (optional)", placeholder="Any extra details...")

        col_save, col_cancel, _ = st.columns([1, 1, 4])
        with col_save:
            if st.button("💾 Save Task", type="primary", use_container_width=True):
                if task_title:
                    time_str = task_time.strftime("%H:%M") if task_time else None
                    db.add_task(
                        title=task_title.strip(),
                        due_date=task_date.isoformat(),
                        category_id=category,
                        assigned_to=assigned,
                        due_time=time_str,
                        description=description,
                        recurrence=recurrence,
                        priority=priority,
                    )
                    st.session_state.show_add_task = False
                    st.cache_data.clear()
                    st.toast("Task added!")
                    st.rerun()
                else:
                    st.warning("Please enter a task title!")
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_add_task = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

    # Weekly calendar grid
    week_start = st.session_state.current_week_start
    tasks = load_week_tasks(week_start)

    tasks_by_date = {}
    for i in range(7):
        d = week_start + timedelta(days=i)
        tasks_by_date[d] = []

    for t in tasks:
        d = date.fromisoformat(t['due_date'])
        if d in tasks_by_date:
            tasks_by_date[d].append(t)

    day_cols = st.columns(7)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i, col in enumerate(day_cols):
        d = week_start + timedelta(days=i)
        is_today = d == today
        day_class = "today" if is_today else "other"

        with col:
            st.markdown(f"""
            <div class="day-header {day_class}">
                <div class="day-name">{day_names[i]}</div>
                <div class="day-num">{d.day}</div>
            </div>
            """, unsafe_allow_html=True)

            day_tasks = tasks_by_date.get(d, [])

            if not day_tasks:
                st.markdown('<div class="empty-day"><div class="empty-day-icon">🌙</div>Nothing planned</div>', unsafe_allow_html=True)
            else:
                for t in day_tasks:
                    completed_class = "completed" if t['is_completed'] else ""
                    priority_class = f"priority-{t['priority']}"
                    border_color = t.get('category_color') or t.get('person_color') or '#475569'

                    person_html = ""
                    if t.get('person_name'):
                        person_html = (
                            f"<span class='person-badge' style='background:{t['person_color']}25; "
                            f"color:{t['person_color']} !important'>{t['person_avatar']} {t['person_name']}</span>"
                        )

                    cat_html = ""
                    if t.get('category_name'):
                        cat_html = (
                            f"<span class='cat-tag' style='background:{t['category_color']}25; "
                            f"color:{t['category_color']} !important'>{t['category_icon']} {t['category_name']}</span>"
                        )

                    time_html = ""
                    if t.get('due_time'):
                        try:
                            t_obj = datetime.strptime(t['due_time'], "%H:%M")
                            time_html = f"<span style='color:#94a3b8 !important'>🕐 {t_obj.strftime('%I:%M %p')}</span>"
                        except ValueError:
                            time_html = f"<span style='color:#94a3b8 !important'>🕐 {t['due_time']}</span>"

                    rec_html = ""
                    if t.get('recurrence'):
                        rec_labels = {'daily': '🔄 Daily', 'weekly': '🔄 Weekly',
                                      'biweekly': '🔄 Bi-weekly', 'monthly': '🔄 Monthly'}
                        rec_html = f"<span class='recurrence-badge'>{rec_labels.get(t['recurrence'], '')}</span>"

                    st.markdown(f"""
                    <div class="task-card {completed_class} {priority_class}"
                         style="border-left-color: {border_color};">
                        <div class="task-title">{t['title']}</div>
                        <div class="task-meta">
                            {person_html} {cat_html}
                        </div>
                        <div class="task-meta" style="margin-top:0.2rem;">
                            {time_html} {rec_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = "✅" if not t['is_completed'] else "↩️"
                    btn_help = "Mark complete" if not t['is_completed'] else "Mark incomplete"
                    bcol1, bcol2, bcol3 = st.columns(3)
                    with bcol1:
                        if st.button(btn_label, key=f"toggle_{t['id']}", help=btn_help):
                            db.toggle_task_complete(t['id'])
                            st.cache_data.clear()
                            completion_status = "completed" if not t['is_completed'] else "reopened"
                            st.toast(f"Task {completion_status}!")
                            st.rerun()
                    with bcol2:
                        if st.button("✏️", key=f"edit_{t['id']}", help="Edit task"):
                            st.session_state.editing_task_id = t['id']
                            st.rerun()
                    with bcol3:
                        if t.get('recurrence'):
                            dc1, dc2 = st.columns(2)
                            with dc1:
                                if st.button("🗑️", key=f"del_{t['id']}", help="Delete this one"):
                                    db.delete_task(t['id'])
                                    st.cache_data.clear()
                                    st.toast("Task deleted")
                                    st.rerun()
                            with dc2:
                                if st.button("🗑️🔄", key=f"del_all_{t['id']}", help="Delete all future"):
                                    db.delete_task(t['id'], delete_future=True)
                                    st.cache_data.clear()
                                    st.toast("All future recurring tasks deleted")
                                    st.rerun()
                        else:
                            if st.button("🗑️", key=f"del_{t['id']}", help="Delete task"):
                                db.delete_task(t['id'])
                                st.cache_data.clear()
                                st.toast("Task deleted")
                                st.rerun()

                    # --- Inline edit form ---
                    if st.session_state.editing_task_id == t['id']:
                        st.markdown("---")
                        people = load_people()
                        categories = load_categories()

                        ed_title = st.text_input("Title", value=t['title'], key=f"ed_title_{t['id']}")

                        ed_c1, ed_c2 = st.columns(2)
                        with ed_c1:
                            try:
                                current_date = date.fromisoformat(t['due_date'])
                            except (ValueError, TypeError):
                                current_date = date.today()
                            ed_date = st.date_input("Due Date", value=current_date, key=f"ed_date_{t['id']}")
                        with ed_c2:
                            current_time = None
                            if t.get('due_time'):
                                try:
                                    current_time = datetime.strptime(t['due_time'], "%H:%M").time()
                                except ValueError:
                                    current_time = None
                            ed_use_time = st.checkbox("Set time?", value=current_time is not None, key=f"ed_usetime_{t['id']}")
                            ed_time = None
                            if ed_use_time:
                                ed_time = st.time_input("Time", value=current_time or time(9, 0), key=f"ed_time_{t['id']}")

                        ed_c3, ed_c4 = st.columns(2)
                        with ed_c3:
                            person_opts = {}
                            for p in people:
                                label = "%s %s" % (p['avatar'], p['name'])
                                person_opts[p['id']] = label
                            person_opts[None] = "Unassigned"
                            person_keys = list(person_opts.keys())
                            cur_p_idx = 0
                            if t.get('assigned_to') in person_keys:
                                cur_p_idx = person_keys.index(t['assigned_to'])
                            ed_assigned = st.selectbox("Assign to", options=person_keys,
                                                        index=cur_p_idx,
                                                        format_func=lambda x: person_opts[x],
                                                        key=f"ed_person_{t['id']}")
                        with ed_c4:
                            cat_opts = {}
                            for c in categories:
                                label = "%s %s" % (c['icon'], c['name'])
                                cat_opts[c['id']] = label
                            cat_opts[None] = "No Category"
                            cat_keys = list(cat_opts.keys())
                            cur_c_idx = 0
                            if t.get('category_id') in cat_keys:
                                cur_c_idx = cat_keys.index(t['category_id'])
                            ed_category = st.selectbox("Category", options=cat_keys,
                                                        index=cur_c_idx,
                                                        format_func=lambda x: cat_opts[x],
                                                        key=f"ed_cat_{t['id']}")

                        ed_c5, ed_c6 = st.columns(2)
                        with ed_c5:
                            pri_opts = ["low", "medium", "high"]
                            cur_pri = pri_opts.index(t.get('priority', 'medium')) if t.get('priority') in pri_opts else 1
                            ed_priority = st.selectbox("Priority", pri_opts, index=cur_pri, key=f"ed_pri_{t['id']}")
                        with ed_c6:
                            rec_opts = [None, "daily", "weekly", "biweekly", "monthly"]
                            rec_labels = {None: "No repeat", "daily": "Daily", "weekly": "Weekly", "biweekly": "Every 2 weeks", "monthly": "Monthly"}
                            cur_rec = rec_opts.index(t.get('recurrence')) if t.get('recurrence') in rec_opts else 0
                            ed_recurrence = st.selectbox("Repeat", rec_opts, index=cur_rec,
                                                          format_func=lambda x: rec_labels.get(x, str(x)),
                                                          key=f"ed_rec_{t['id']}")

                        ed_desc = st.text_input("Notes", value=t.get('description') or '', key=f"ed_desc_{t['id']}")

                        sc1, sc2, _ = st.columns([1, 1, 2])
                        with sc1:
                            if st.button("Save", key=f"save_{t['id']}", type="primary", use_container_width=True):
                                time_str = ed_time.strftime("%H:%M") if ed_time else None
                                db.update_task(
                                    t['id'],
                                    title=ed_title.strip(),
                                    due_date=ed_date.isoformat(),
                                    due_time=time_str,
                                    assigned_to=ed_assigned,
                                    category_id=ed_category,
                                    priority=ed_priority,
                                    recurrence=ed_recurrence,
                                    description=ed_desc,
                                )
                                st.session_state.editing_task_id = None
                                st.cache_data.clear()
                                st.toast("Task updated!")
                                st.rerun()
                        with sc2:
                            if st.button("Cancel", key=f"cancel_{t['id']}", use_container_width=True):
                                st.session_state.editing_task_id = None
                                st.rerun()

    # ===== DAY VIEW =====
    if st.session_state.calendar_view == "day":
        sd = st.session_state.selected_day
        day_tasks = load_day_tasks(sd)

        if not day_tasks:
            st.markdown("""
            <div style="text-align:center; padding:3rem; color:#94a3b8;">
                <div style="font-size:3rem;">\U0001f31f</div>
                <h3>Nothing planned for this day</h3>
                <p>Click \u2795 Add Task to schedule something</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for t in day_tasks:
                completed_class = "completed" if t['is_completed'] else ""
                priority_class = "priority-%s" % t['priority']
                border_color = t.get('category_color') or t.get('person_color') or '#475569'

                person_html = ""
                if t.get('person_name'):
                    person_html = (
                        "<span class='person-badge' style='background:%s25; "
                        "color:%s !important'>%s %s</span>"
                    ) % (t['person_color'], t['person_color'], t['person_avatar'], t['person_name'])

                cat_html = ""
                if t.get('category_name'):
                    cat_html = (
                        "<span class='cat-tag' style='background:%s25; "
                        "color:%s !important'>%s %s</span>"
                    ) % (t['category_color'], t['category_color'], t['category_icon'], t['category_name'])

                time_html = ""
                if t.get('due_time'):
                    try:
                        t_obj = datetime.strptime(t['due_time'], "%H:%M")
                        time_html = "<span style='color:#94a3b8 !important'>\U0001f550 %s</span>" % t_obj.strftime('%I:%M %p')
                    except ValueError:
                        time_html = "<span style='color:#94a3b8 !important'>\U0001f550 %s</span>" % t['due_time']

                desc_html = ""
                if t.get('description'):
                    desc_html = "<div style='color:#94a3b8; font-size:0.85rem; margin-top:0.3rem;'>%s</div>" % t['description']

                st.markdown("""
                <div class="task-card %s %s" style="border-left-color: %s;">
                    <div class="task-title">%s</div>
                    <div class="task-meta">%s %s</div>
                    <div class="task-meta" style="margin-top:0.2rem;">%s</div>
                    %s
                </div>
                """ % (completed_class, priority_class, border_color, t['title'],
                       person_html, cat_html, time_html, desc_html), unsafe_allow_html=True)

                btn_label = "\u2705" if not t['is_completed'] else "\u21a9\ufe0f"
                btn_help = "Mark complete" if not t['is_completed'] else "Mark incomplete"
                dc1, dc2, dc3 = st.columns(3)
                with dc1:
                    if st.button(btn_label, key="dtoggle_%s" % t['id'], help=btn_help):
                        db.toggle_task_complete(t['id'])
                        st.cache_data.clear()
                        st.toast("Task updated!")
                        st.rerun()
                with dc2:
                    if st.button("\u270f\ufe0f", key="dedit_%s" % t['id'], help="Edit task"):
                        st.session_state.editing_task_id = t['id']
                        st.rerun()
                with dc3:
                    if st.button("\U0001f5d1\ufe0f", key="ddel_%s" % t['id'], help="Delete task"):
                        db.delete_task(t['id'])
                        st.cache_data.clear()
                        st.toast("Task deleted")
                        st.rerun()

    # ===== MONTH VIEW =====
    if st.session_state.calendar_view == "month":
        import calendar as cal_mod
        cm = st.session_state.current_month
        month_tasks = load_month_tasks(cm.year, cm.month)

        # Group tasks by date
        tasks_by_day = {}
        for t in month_tasks:
            d = date.fromisoformat(t['due_date'])
            if d not in tasks_by_day:
                tasks_by_day[d] = []
            tasks_by_day[d].append(t)

        # Calendar grid header
        st.markdown("""
        <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:4px; margin-bottom:4px;">
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Mon</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Tue</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Wed</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Thu</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Fri</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Sat</div>
            <div style="text-align:center; font-weight:600; color:#94a3b8; padding:0.3rem;">Sun</div>
        </div>
        """, unsafe_allow_html=True)

        # Build weeks
        month_cal = cal_mod.monthcalendar(cm.year, cm.month)
        for week_row in month_cal:
            cols = st.columns(7)
            for i, day_num in enumerate(week_row):
                with cols[i]:
                    if day_num == 0:
                        st.markdown("<div style='min-height:80px;'></div>", unsafe_allow_html=True)
                    else:
                        d = date(cm.year, cm.month, day_num)
                        day_tasks_list = tasks_by_day.get(d, [])
                        total = len(day_tasks_list)
                        done = sum(1 for t in day_tasks_list if t.get('is_completed'))

                        is_today = d == today
                        bg = "#1e3a5f" if is_today else "#222640"
                        border = "2px solid #4A90D9" if is_today else "1px solid #334155"

                        task_dots = ""
                        for t in day_tasks_list[:4]:
                            color = t.get('person_color') or t.get('category_color') or '#94a3b8'
                            opacity = "0.4" if t.get('is_completed') else "1"
                            task_dots += "<div style='width:8px;height:8px;border-radius:50%%;background:%s;opacity:%s;display:inline-block;margin:1px;'></div>" % (color, opacity)
                        if total > 4:
                            task_dots += "<span style='color:#94a3b8;font-size:0.7rem;'>+%d</span>" % (total - 4)

                        count_html = ""
                        if total > 0:
                            count_html = "<div style='font-size:0.7rem;color:#94a3b8;'>%d/%d</div>" % (done, total)

                        st.markdown("""
                        <div style="background:%s; border:%s; border-radius:8px; padding:0.4rem; min-height:80px; cursor:pointer;">
                            <div style="font-weight:600; font-size:0.9rem; color:%s;">%d</div>
                            <div style="margin-top:0.2rem;">%s</div>
                            %s
                        </div>
                        """ % (bg, border, "#4A90D9" if is_today else "#cbd5e1", day_num, task_dots, count_html), unsafe_allow_html=True)

                        if st.button("View", key="month_day_%d" % day_num, use_container_width=True):
                            st.session_state.selected_day = d
                            st.session_state.calendar_view = "day"
                            st.rerun()


# ===========================================================================
# TAB 2: GROCERY LIST
# ===========================================================================
with tab_grocery:
    st.markdown('''
    <div style="background: linear-gradient(135deg, #222640, #1a3a2a); border-radius: 12px;
                padding: 1rem 1.5rem; margin-bottom: 1rem; border: 1px solid #334155;">
        <h2 style="margin:0; color:#e0e0e0 !important;">\U0001f6d2 Grocery List</h2>
        <p style="margin:0.3rem 0 0; color:#94a3b8 !important;">Shared family shopping list</p>
    </div>
    ''', unsafe_allow_html=True)

    # Add item form
    people = load_people()
    gc1, gc2, gc3, gc4 = st.columns([3, 2, 2, 1])
    with gc1:
        grocery_name = st.text_input("Item", placeholder="e.g. Milk, Eggs, Bread...", key="grocery_name", label_visibility="collapsed")
    with gc2:
        grocery_categories = ["Produce", "Dairy", "Meat", "Bakery", "Frozen", "Pantry", "Beverages", "Snacks", "Household", "Other"]
        grocery_cat = st.selectbox("Category", grocery_categories, key="grocery_cat", label_visibility="collapsed")
    with gc3:
        person_opts = {None: "Anyone"}
        for p in people:
            person_opts[p['id']] = "%s %s" % (p['avatar'], p['name'])
        grocery_person = st.selectbox("Added by", options=list(person_opts.keys()),
                                       format_func=lambda x: person_opts[x],
                                       key="grocery_person", label_visibility="collapsed")
    with gc4:
        if st.button("\u2795 Add", use_container_width=True, type="primary", key="add_grocery"):
            if grocery_name:
                db.add_grocery_item(grocery_name.strip(), grocery_cat, grocery_person)
                st.cache_data.clear()
                st.toast("Added to list!")
                st.rerun()

    st.markdown("---")

    # Display grocery items
    items = load_grocery_items()

    if not items:
        st.markdown('''
        <div style="text-align:center; padding:3rem; color:#94a3b8;">
            <div style="font-size:3rem;">\U0001f6d2</div>
            <h3>Your grocery list is empty</h3>
            <p>Add items above to get started</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Group by category
        from collections import OrderedDict
        grouped = OrderedDict()
        for item in items:
            cat = item.get('category', 'General')
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(item)

        checked_count = sum(1 for item in items if item.get('is_checked'))
        total_count = len(items)

        if checked_count > 0:
            clear_col1, clear_col2 = st.columns([3, 1])
            with clear_col1:
                st.markdown(
                    "<span style='color:#94a3b8;'>%d of %d items checked</span>" % (checked_count, total_count),
                    unsafe_allow_html=True
                )
            with clear_col2:
                if st.button("\U0001f5d1 Clear checked", use_container_width=True, key="clear_grocery"):
                    db.clear_checked_grocery()
                    st.cache_data.clear()
                    st.toast("Cleared checked items")
                    st.rerun()

        for cat_name, cat_items in grouped.items():
            st.markdown("**%s**" % cat_name)
            for item in cat_items:
                ic1, ic2, ic3 = st.columns([1, 5, 1])
                with ic1:
                    checked = item.get('is_checked', False)
                    if st.checkbox("", value=checked, key="gcheck_%s" % item['id'], label_visibility="collapsed"):
                        if not checked:
                            db.toggle_grocery_item(item['id'])
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        if checked:
                            db.toggle_grocery_item(item['id'])
                            st.cache_data.clear()
                            st.rerun()
                with ic2:
                    style = "text-decoration: line-through; color: #64748b;" if item.get('is_checked') else "color: #e0e0e0;"
                    person_tag = ""
                    if item.get('person_avatar'):
                        person_tag = " <span style='color:#94a3b8;font-size:0.8rem;'>%s</span>" % item['person_avatar']
                    st.markdown(
                        "<span style='%s'>%s</span>%s" % (style, item['name'], person_tag),
                        unsafe_allow_html=True
                    )
                with ic3:
                    if st.button("\u2716", key="gdel_%s" % item['id'], help="Remove"):
                        db.delete_grocery_item(item['id'])
                        st.cache_data.clear()
                        st.rerun()

# ===========================================================================
# TAB 3: BALANCE BOARD
# ===========================================================================
with tab_balance:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #222640, #0f3460); border-radius: 12px;
                padding: 1rem 1.5rem; margin-bottom: 1rem; border: 1px solid #334155;">
        <h3 style="margin:0; color:#38bdf8 !important;">⚖️ Balance Board</h3>
        <p style="margin:0.3rem 0 0 0; color:#94a3b8 !important; font-size:0.9rem;">
            A blameless look at how household work is distributed.
            Not about who's slacking — it's about making sure things feel fair for everyone.
        </p>
    </div>
    """, unsafe_allow_html=True)

    time_range = st.selectbox("Time range", [2, 4, 8, 12], index=1,
                               format_func=lambda w: f"Past {w} weeks", key="equity_range")
    equity = db.get_equity_stats(weeks_back=time_range)

    if not equity['assigned']:
        st.info("No tasks assigned yet! Start adding tasks and the Balance Board will show how the workload is distributed.")
    else:
        # --- Overall workload split ---
        st.markdown("### 🎯 Workload Split")
        total_assigned = sum(p['assigned_count'] for p in equity['assigned'])

        eq_cols = st.columns(len(equity['assigned']))
        for idx, person in enumerate(equity['assigned']):
            pct = int(person['assigned_count'] / total_assigned * 100) if total_assigned > 0 else 0
            comp_pct = int(person['completed_count'] / person['assigned_count'] * 100) if person['assigned_count'] > 0 else 0
            with eq_cols[idx]:
                st.markdown(f"""
                <div class="stat-card" style="border-top: 4px solid {person['color']};">
                    <div style="font-size:2rem;">{person['avatar']}</div>
                    <div style="font-weight:700; font-size:1.1rem; color:#f1f5f9 !important;">{person['name']}</div>
                    <div class="stat-number">{pct}%</div>
                    <div class="stat-label">of tasks ({person['assigned_count']} total)</div>
                    <div class="progress-container" style="margin-top:0.5rem;">
                        <div class="progress-fill" style="width:{comp_pct}%; background:{person['color']};"></div>
                    </div>
                    <div class="stat-label">{comp_pct}% completion rate</div>
                </div>
                """, unsafe_allow_html=True)

        # Fairness indicator
        if len(equity['assigned']) >= 2:
            pcts = [p['assigned_count'] / total_assigned * 100 for p in equity['assigned']]
            max_diff = max(pcts) - min(pcts)
            if max_diff <= 10:
                fairness_emoji = "🟢"
                fairness_msg = "Looking really balanced! Great teamwork."
            elif max_diff <= 25:
                fairness_emoji = "🟡"
                fairness_msg = "Slightly uneven — might be worth a quick check-in to see if anyone wants to swap some tasks."
            else:
                fairness_emoji = "🟠"
                fairness_msg = "One person has quite a bit more on their plate. A good chance to redistribute!"

            st.markdown(f"""
            <div style="background:#222640; border-radius:10px; padding:0.8rem 1.2rem;
                        margin:1rem 0; border: 1px solid #334155;
                        display:flex; align-items:center; gap:0.8rem;">
                <span style="font-size:1.5rem;">{fairness_emoji}</span>
                <div>
                    <strong style="color:#f1f5f9 !important;">Fairness Check:</strong>
                    <span style="color:#cbd5e1 !important;"> {fairness_msg}</span>
                    <br><span style="color:#64748b !important; font-size:0.8rem;">
                    Spread: {max_diff:.0f}% difference · An even split would be {100/len(equity['assigned']):.0f}% each
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- Category breakdown ---
        st.markdown("### 🏷️ Who Does What?")
        st.caption("See which types of chores each person tends to handle — useful for mixing things up!")

        people_names = list(dict.fromkeys(r['person_name'] for r in equity['by_category']))
        if people_names:
            cat_cols = st.columns(len(people_names))
            for idx, person_name in enumerate(people_names):
                person_cats = [r for r in equity['by_category'] if r['person_name'] == person_name]
                with cat_cols[idx]:
                    p_color = person_cats[0]['person_color'] if person_cats else '#94a3b8'
                    st.markdown(f"<div style='font-weight:700; color:{p_color} !important; font-size:1.1rem; margin-bottom:0.5rem;'>{person_name}</div>",
                               unsafe_allow_html=True)
                    for pc in person_cats:
                        cat_name = pc['category_name'] or 'Uncategorized'
                        cat_icon = pc['category_icon'] or '📋'
                        st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center;
                                    padding:0.4rem 0; border-bottom: 1px solid #334155;">
                            <span style="color:#cbd5e1 !important;">{cat_icon} {cat_name}</span>
                            <span style="font-weight:600; color:#f1f5f9 !important;">{pc['count']}</span>
                        </div>
                        """, unsafe_allow_html=True)

        # --- Unassigned tasks callout ---
        if equity['unassigned'] > 0:
            st.markdown(f"""
            <div style="background:#222640; border-radius:10px; padding:0.8rem 1.2rem;
                        margin:1rem 0; border-left: 4px solid #f59e0b; border: 1px solid #334155;">
                <strong style="color:#fbbf24 !important;">📋 {equity['unassigned']} unassigned task{'s' if equity['unassigned'] != 1 else ''}</strong>
                <span style="color:#94a3b8 !important;"> in this period — grab some to help balance the load!</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; color:#64748b !important; font-size:0.8rem; margin-top:1rem;">
            Showing data from {equity['period_start'].strftime('%b %d')} to {equity['period_end'].strftime('%b %d, %Y')}
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center; color:#64748b !important; font-size:0.8rem; padding:0.5rem;'>"
    "🏠 Home Command Center — Built with ❤️ for your household"
    "</div>",
    unsafe_allow_html=True
)

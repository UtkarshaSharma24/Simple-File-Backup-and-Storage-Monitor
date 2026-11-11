"""app.py - Simple File Backup & Storage Monitor (Streamlit dashboard)."""

import html
import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import backup_utils
import database

st.set_page_config(page_title="File Backup & Storage Monitor", layout="wide")
database.create_table()

# ---------- Styling (plain CSS) ----------
CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2.2rem; max-width: 1200px;}
[data-testid="stSidebar"] {border-right: 1px solid #262a36;}
[data-testid="stSidebar"] [role="radiogroup"] {gap: 4px;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding: 9px 14px; border-radius: 10px; width: 100%;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background: #1f2330;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background: #2b2f55;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 14px;}
.top {display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.4rem;}
.top h1 {font-size: 1.9rem; font-weight: 700; margin: 0; padding: 0; color: #f3f4f6;}
.top p {margin: 2px 0 0 0; color: #9ca3af; font-size: 0.92rem;}
.pill {padding: 5px 14px; border-radius: 999px; font-size: 0.78rem; font-weight: 600;}
.pill-ok {background: rgba(34,197,94,.15); color: #4ade80; border: 1px solid rgba(34,197,94,.35);}
.pill-warn {background: rgba(245,158,11,.15); color: #fbbf24; border: 1px solid rgba(245,158,11,.35);}
.pill-bad {background: rgba(239,68,68,.15); color: #f87171; border: 1px solid rgba(239,68,68,.35);}
.card {background: #171a23; border: 1px solid #262a36; border-radius: 14px; padding: 18px 20px;}
.card-title {font-weight: 600; color: #f3f4f6; margin-bottom: 14px; font-size: 1rem;}
.stat {display: flex; align-items: center; gap: 14px; padding: 16px 18px;}
.icon {width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; flex-shrink: 0;}
.i-purple {background: rgba(124,108,240,.18); color: #a99cff;}
.i-green {background: rgba(34,197,94,.16); color: #4ade80;}
.i-blue {background: rgba(59,130,246,.16); color: #60a5fa;}
.i-red {background: rgba(239,68,68,.16); color: #f87171;}
.i-amber {background: rgba(245,158,11,.16); color: #fbbf24;}
.stat-value {font-size: 1.6rem; font-weight: 700; color: #f9fafb; line-height: 1.1;}
.stat-label {font-size: 0.78rem; color: #9ca3af; margin-top: 3px;}
.donut {width: 170px; height: 170px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 4px auto 18px auto;}
.donut-inner {width: 124px; height: 124px; border-radius: 50%; background: #171a23; display: flex; flex-direction: column; align-items: center; justify-content: center;}
.donut-percent {font-size: 1.7rem; font-weight: 700; color: #f9fafb;}
.donut-text {font-size: 0.72rem; color: #9ca3af;}
.legend-row {display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-top: 1px solid #262a36; font-size: 0.9rem; color: #cbd5e1;}
.legend-row b {color: #f9fafb;}
.dot {display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 8px;}
.activity {display: flex; align-items: center; gap: 14px; padding: 11px 0; border-top: 1px solid #262a36;}
.activity:first-of-type {border-top: none;}
.tag {width: 40px; height: 40px; border-radius: 10px; background: #1f2330; color: #9ca3af; display: flex; align-items: center; justify-content: center; font-size: 0.62rem; font-weight: 700; letter-spacing: .04em; flex-shrink: 0;}
.activity-main {flex: 1; min-width: 0;}
.activity-name {font-weight: 600; color: #f3f4f6; font-size: 0.93rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.activity-meta {font-size: 0.78rem; color: #9ca3af;}
.activity-size {font-size: 0.82rem; color: #9ca3af; min-width: 70px; text-align: right;}
.badge {padding: 3px 12px; border-radius: 999px; font-size: 0.72rem; font-weight: 600;}
.ok {background: rgba(34,197,94,.15); color: #4ade80;}
.fail {background: rgba(239,68,68,.15); color: #f87171;}
.empty {color: #6b7280; font-size: 0.9rem; padding: 8px 0;}
.note {color: #9ca3af; font-size: 0.82rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Small helper functions (build HTML pieces) ----------

def page_header(title, subtitle, pill_text="", pill_class="pill-ok"):
    pill = f'<span class="pill {pill_class}">{pill_text}</span>' if pill_text else ""
    st.markdown(
        f'<div class="top"><div><h1>{title}</h1><p>{subtitle}</p></div>{pill}</div>',
        unsafe_allow_html=True,
    )


def stat_card(icon, icon_class, value, label):
    return (
        '<div class="card stat">'
        f'<div class="icon {icon_class}">{icon}</div>'
        f'<div><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>'
        "</div>"
    )


def disk_color(percent):
    if percent < 70:
        return "#22c55e"
    if percent < 90:
        return "#f59e0b"
    return "#ef4444"


def disk_card(total, used, free):
    percent = used / total * 100
    color = disk_color(percent)
    return (
        '<div class="card"><div class="card-title">Disk Space</div>'
        f'<div class="donut" style="background: conic-gradient({color} {percent}%, #2a2f3d 0);">'
        f'<div class="donut-inner"><div class="donut-percent">{percent:.0f}%</div>'
        '<div class="donut-text">used</div></div></div>'
        f'<div class="legend-row"><span>Total</span><b>{backup_utils.format_size(total)}</b></div>'
        f'<div class="legend-row"><span><span class="dot" style="background:{color}"></span>Used</span>'
        f'<b>{backup_utils.format_size(used)}</b></div>'
        f'<div class="legend-row"><span><span class="dot" style="background:#2a2f3d"></span>Free</span>'
        f'<b>{backup_utils.format_size(free)}</b></div>'
        "</div>"
    )


def activity_card(history, count=6):
    rows = ""
    for row in history[:count]:
        badge = "ok" if row["status"] == "Success" else "fail"
        tag = {"File": "FILE", "Folder": "DIR"}.get(row["item_type"], "-")
        size = backup_utils.format_size(row["size_bytes"]) if row["size_bytes"] else ""
        rows += (
            '<div class="activity">'
            f'<div class="tag">{tag}</div>'
            '<div class="activity-main">'
            f'<div class="activity-name">{html.escape(row["file_name"])}</div>'
            f'<div class="activity-meta">{row["action"]} &middot; {row["backup_date"]} {row["backup_time"]}</div>'
            "</div>"
            f'<div class="activity-size">{size}</div>'
            f'<span class="badge {badge}">{row["status"]}</span>'
            "</div>"
        )
    if not rows:
        rows = '<div class="empty">No activity yet. Create your first backup.</div>'
    return f'<div class="card"><div class="card-title">Recent Activity</div>{rows}</div>'


def storage_chart_data(history, days=7):
    """Total backup size (in MB) at the end of each of the last 7 days."""
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    good = [r for r in history if r["action"] == "Backup" and r["status"] == "Success"]
    values = []
    for day in dates:
        total = sum(r["size_bytes"] or 0 for r in good if r["backup_date"] <= str(day))
        values.append(round(total / (1024 * 1024), 3))
    labels = [d.strftime("%d %b") for d in dates]
    return pd.DataFrame({"Backup storage (MB)": values}, index=labels)


# ---------- Sidebar ----------
st.sidebar.markdown("### Backup Monitor")
st.sidebar.caption("Simple File Backup & Storage Monitor")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Create Backup", "Restore Backup", "Backup History"],
    label_visibility="collapsed",
)
_, _, side_free = backup_utils.get_disk_space()
st.sidebar.divider()
st.sidebar.caption(f"Free disk space: {backup_utils.format_size(side_free)}")


# ---------- Page 1: Dashboard ----------
if page == "Dashboard":
    total, used, free = backup_utils.get_disk_space()
    percent = used / total * 100
    if percent < 70:
        pill_text, pill_class = "System healthy", "pill-ok"
    elif percent < 90:
        pill_text, pill_class = "Disk filling up", "pill-warn"
    else:
        pill_text, pill_class = "Disk almost full", "pill-bad"
    page_header("Dashboard", "Overview of your backups and disk space", pill_text, pill_class)

    history = database.get_history()
    ok_backups = [r for r in history if r["action"] == "Backup" and r["status"] == "Success"]
    ok_restores = [r for r in history if r["action"] == "Restore" and r["status"] == "Success"]
    failed = [r for r in history if r["status"] == "Failed"]
    backup_size = sum(r["size_bytes"] or 0 for r in ok_backups)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(stat_card("&#8801;", "i-purple", len(history), "Total actions"), unsafe_allow_html=True)
    c2.markdown(stat_card("&#10003;", "i-green", len(ok_backups), "Backups done"), unsafe_allow_html=True)
    c3.markdown(stat_card("&#8635;", "i-blue", len(ok_restores), "Restores done"), unsafe_allow_html=True)
    c4.markdown(stat_card("&#10005;", "i-red", len(failed), "Failed"), unsafe_allow_html=True)
    c5.markdown(stat_card("&#9632;", "i-amber", backup_utils.format_size(backup_size), "Backup storage"), unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([3, 2])
    with left:
        with st.container(border=True):
            st.markdown('<div class="card-title">Backup Storage Growth (last 7 days)</div>',
                        unsafe_allow_html=True)
            st.area_chart(storage_chart_data(history), color="#7c6cf0", height=285)
    right.markdown(disk_card(total, used, free), unsafe_allow_html=True)

    st.write("")
    st.markdown(activity_card(history), unsafe_allow_html=True)


# ---------- Page 2: Create Backup ----------
elif page == "Create Backup":
    page_header("Create Backup", "Copy a file or folder into the backups folder")

    with st.container(border=True):
        with st.form("backup_form", border=False):
            path = st.text_input(
                "File or folder path",
                placeholder=r"C:\Users\YourName\Documents\notes.txt",
                help="Tip: in File Explorer, Shift + right-click the item and choose 'Copy as path'.",
            )
            submitted = st.form_submit_button("Create Backup", type="primary")

    if submitted:
        success, message = backup_utils.create_backup(path)
        if success:
            st.success(message)
        else:
            st.error(message)

    st.markdown('<div class="note">Old backups are never replaced. Each backup name '
                "includes the date and time.</div>", unsafe_allow_html=True)


# ---------- Page 3: Restore Backup ----------
elif page == "Restore Backup":
    page_header("Restore Backup", "Bring back a file or folder from an earlier backup")

    backups = database.get_successful_backups()
    if not backups:
        st.info("No backups available yet. Create a backup first.")
    else:
        options = {
            f"{b['file_name']}  -  {b['backup_date']} {b['backup_time']}": b
            for b in backups
        }
        choice = st.selectbox("Select a backup", list(options.keys()))
        selected = options[choice]

        size = backup_utils.format_size(selected["size_bytes"] or 0)
        st.markdown(
            '<div class="card"><div class="activity" style="border-top:none; padding:0;">'
            f'<div class="tag">{"DIR" if selected["item_type"] == "Folder" else "FILE"}</div>'
            '<div class="activity-main">'
            f'<div class="activity-name">{html.escape(selected["file_name"])}</div>'
            f'<div class="activity-meta">Original location: {html.escape(selected["source_path"])}</div>'
            "</div>"
            f'<div class="activity-size">{size}</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")

        with st.container(border=True):
            with st.form("restore_form", border=False):
                restore_folder = st.text_input(
                    "Restore to folder",
                    value=os.path.dirname(selected["source_path"]),
                )
                restore_clicked = st.form_submit_button("Restore", type="primary")

        if restore_clicked:
            success, message = backup_utils.restore_backup(
                selected["backup_path"], selected["file_name"], restore_folder
            )
            if success:
                st.success(message)
            else:
                st.error(message)

        st.markdown('<div class="note">Existing files are never overwritten. If the name is '
                    "already used, the restored item gets '_restored' in its name.</div>",
                    unsafe_allow_html=True)


# ---------- Page 4: Backup History ----------
elif page == "Backup History":
    page_header("Backup History", "Every backup and restore action is saved here")

    history = database.get_history()
    if not history:
        st.info("No history yet.")
    else:
        f1, f2, f3 = st.columns([1, 1, 2])
        action_filter = f1.selectbox("Action", ["All", "Backup", "Restore"])
        status_filter = f2.selectbox("Status", ["All", "Success", "Failed"])
        search = f3.text_input("Search by name")

        rows = history
        if action_filter != "All":
            rows = [r for r in rows if r["action"] == action_filter]
        if status_filter != "All":
            rows = [r for r in rows if r["status"] == status_filter]
        if search:
            rows = [r for r in rows if search.lower() in r["file_name"].lower()]

        table_data = [
            {
                "ID": r["id"],
                "Action": r["action"],
                "Name": r["file_name"],
                "Type": r["item_type"],
                "Size": backup_utils.format_size(r["size_bytes"] or 0),
                "Date": r["backup_date"],
                "Time": r["backup_time"],
                "Status": r["status"],
                "Details": r["message"],
            }
            for r in rows
        ]
        st.caption(f"Showing {len(rows)} of {len(history)} records")
        st.dataframe(table_data, hide_index=True)

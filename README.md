# 📁 Simple File Backup & Storage Monitor

A beginner-friendly Python project built using **Python, Streamlit, and SQLite** to manage local file and folder backups.

The application allows users to create backups, restore previously saved files, monitor disk storage, and maintain a history of backup and restore operations through an interactive dashboard.

## 🚀 Features

- **File & Folder Backup:** Create backups of individual files or complete folders.
- **Restore Backup:** Restore previously created backups to a selected destination.
- **Backup History:** Store backup and restore records using SQLite.
- **Storage Monitoring:** Display available, used, and total disk space.
- **Interactive Dashboard:** View backup statistics, recent activities, and storage charts.
- **Data Visualization:** Includes a 7-day backup storage chart and disk space visualization.
- **File Validation:** Handle missing paths, empty files, permission issues, and invalid inputs.
- **Duplicate Protection:** Prevent accidental overwriting of existing files during backup and restore.
- **Navigation:** Separate sections for Dashboard, Create Backup, Restore Backup, and Backup History.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web dashboard |
| SQLite | Backup history and record management |
| Pandas | Data handling and table management |
| Plotly | Charts and data visualization |
| OS & Shutil | File operations and storage management |

## 📂 Project Structure

```text
file_backup_monitor/
│
├── app.py                  # Streamlit application and dashboard
├── backup_utils.py         # Backup, restore and validation logic
├── database.py             # SQLite database operations
├── test_backup.py         # Basic application tests
│
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
│
├── backups/                # Automatically created backup folder
├── backup_history.db       # Automatically created database
│
├── requirements.txt        # Project dependencies
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/file-backup-monitor.git
```

### 2. Navigate to the Project Directory

```bash
cd file-backup-monitor
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run Tests

```bash
python test_backup.py
```

### 7. Start the Application

```bash
streamlit run app.py
```

Open the following URL in your browser:

```text
http://localhost:8501
```

## 💻 Application Modules

### 1. Dashboard
- Displays total backups and recent activities.
- Shows disk storage information.
- Provides a 7-day backup storage chart.
- Displays disk usage through a donut chart.

### 2. Create Backup
- Accepts file or folder paths.
- Validates the selected source.
- Creates a backup inside the local `backups/` directory.
- Records the operation in SQLite.

### 3. Restore Backup
- Displays previously created backups.
- Allows users to select a backup.
- Restores the selected backup to a destination folder.
- Prevents overwriting existing files.

### 4. Backup History
- Displays previous backup and restore operations.
- Shows file names, dates, times, operation status, and other details.
- Maintains records of successful and failed operations.

## 🗄️ Database Design

The application uses SQLite to maintain a table named `backups`.

| Column | Description |
|---|---|
| id | Unique record ID |
| action | Backup or Restore operation |
| file_name | Name of the file or folder |
| item_type | File or Folder |
| source_path | Original file location |
| backup_path | Backup file location |
| backup_date | Operation date |
| backup_time | Operation time |
| status | Success or Failed |
| message | Operation details or error message |
| size_bytes | Size of the backup |

## 🔒 Data Protection

- Backup files are saved with unique timestamp-based names.
- Existing files are not intentionally overwritten during restore.
- Duplicate restored files receive a different filename.
- Invalid paths and file operation errors are handled.
- Backup and restore activities are recorded in the database.

## 🎯 Learning Outcomes

Through this project, I explored:

- Python file handling and directory management.
- Working with SQLite databases.
- Building interactive applications using Streamlit.
- Implementing file backup and restore operations.
- Handling exceptions and validating user inputs.
- Creating dashboards and visualizing storage information.
- Organizing Python applications into separate modules.
- Writing basic tests for application functionality.

## 🔮 Future Improvements

- Automated scheduled backups.
- File compression to reduce storage usage.
- Cloud-based backup integration.
- Backup encryption for improved data security.
- Email notifications for backup operations.

## ⚠️ Limitations

This is a beginner-level learning project designed for local file management.

- Backups are stored locally.
- The application does not currently support cloud storage.
- Automatic scheduling and compression are not implemented.
- The application must be running locally to access files on the computer.

## 👨‍💻 Author

**Utkarsh Sharma**

B.Tech – Computer Science & Engineering (Data Science)

- GitHub: [UtkarshaSharma24](https://github.com/UtkarshaSharma24)
- LinkedIn: [Utkarsh Sharma](https://www.linkedin.com/in/erutkarshsharma/)

---

⭐ If you find this project useful, consider giving it a star!

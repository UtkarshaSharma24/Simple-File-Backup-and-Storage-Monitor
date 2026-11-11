"""backup_utils.py - backup, restore and disk space functions.

No Streamlit code here, so these functions are easy to test.
"""

import os
import shutil
from datetime import datetime

import database

BACKUP_FOLDER = "backups"


# ---------- Helpers ----------

def format_size(num_bytes):
    """Convert bytes into a readable text like '1.50 GB'."""
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def get_disk_space(path="."):
    """Return total, used and free disk space (in bytes)."""
    total, used, free = shutil.disk_usage(path)
    return total, used, free


def get_size(path):
    """Size of a file or a whole folder in bytes."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for folder, _, files in os.walk(path):
        for file in files:
            total += os.path.getsize(os.path.join(folder, file))
    return total


def unique_path(path):
    """If 'path' already exists, add _1, _2 ... so nothing is overwritten."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    return f"{base}_{counter}{ext}"


def validate_source(path, backup_folder=BACKUP_FOLDER):
    """Check the path. Returns (True, '') or (False, 'error message')."""
    if not path or not path.strip():
        return False, "Please enter a file or folder path."
    if not os.path.exists(path):
        return False, "This path does not exist."
    if not os.access(path, os.R_OK):
        return False, "You do not have permission to read this path."
    if os.path.isfile(path) and os.path.getsize(path) == 0:
        return False, "The file is empty (0 bytes)."
    if os.path.isdir(path) and not os.listdir(path):
        return False, "The folder is empty."

    # Do not back up the backup folder itself (it would copy itself forever)
    source = os.path.abspath(path)
    backup_root = os.path.abspath(backup_folder)
    if source == backup_root or source.startswith(backup_root + os.sep):
        return False, "You cannot back up the backup folder itself."
    if backup_root.startswith(source + os.sep):
        return False, "This folder contains the backup folder. Choose another one."
    return True, ""


# ---------- Backup ----------

def create_backup(path, backup_folder=BACKUP_FOLDER, db_path=database.DB_NAME):
    """Back up a file or folder. Returns (success, message)."""
    path = path.strip().strip('"')
    name = os.path.basename(os.path.normpath(path)) or "backup"

    ok, error = validate_source(path, backup_folder)
    if not ok:
        database.add_record("Backup", name, "-", path, "", "Failed", error, db_path)
        return False, error

    item_type = "Folder" if os.path.isdir(path) else "File"
    try:
        os.makedirs(backup_folder, exist_ok=True)

        # Name looks like: report_20261112_153045.txt
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(name) if item_type == "File" else (name, "")
        destination = unique_path(os.path.join(backup_folder, f"{base}_{stamp}{ext}"))

        if item_type == "File":
            shutil.copy2(path, destination)
        else:
            shutil.copytree(path, destination)

        message = f"Backup created: {destination}"
        database.add_record("Backup", name, item_type, path, destination,
                            "Success", message, db_path,
                            size_bytes=get_size(destination))
        return True, message

    except Exception as error:  # keep it simple for beginners
        message = f"Backup failed: {error}"
        database.add_record("Backup", name, item_type, path, "", "Failed",
                            message, db_path)
        return False, message


# ---------- Restore ----------

def restore_backup(backup_path, original_name, restore_folder,
                   db_path=database.DB_NAME):
    """Restore a backup into restore_folder without overwriting anything.

    If a file/folder with the same name already exists, a new name like
    'report_restored_1.txt' is used. Returns (success, message).
    """
    restore_folder = restore_folder.strip().strip('"')
    item_type = "-"

    if not backup_path or not os.path.exists(backup_path):
        message = "The backup file was not found. It may have been deleted."
        database.add_record("Restore", original_name, item_type, backup_path,
                            restore_folder, "Failed", message, db_path)
        return False, message

    item_type = "Folder" if os.path.isdir(backup_path) else "File"

    if not restore_folder:
        message = "Please enter a restore folder."
        database.add_record("Restore", original_name, item_type, backup_path,
                            restore_folder, "Failed", message, db_path)
        return False, message

    try:
        os.makedirs(restore_folder, exist_ok=True)

        target = os.path.join(restore_folder, original_name)
        if os.path.exists(target):
            base, ext = os.path.splitext(target) if item_type == "File" else (target, "")
            target = unique_path(f"{base}_restored{ext}")

        if item_type == "File":
            shutil.copy2(backup_path, target)
        else:
            shutil.copytree(backup_path, target)

        message = f"Restored to: {target}"
        database.add_record("Restore", original_name, item_type, backup_path,
                            target, "Success", message, db_path)
        return True, message

    except Exception as error:
        message = f"Restore failed: {error}"
        database.add_record("Restore", original_name, item_type, backup_path,
                            restore_folder, "Failed", message, db_path)
        return False, message

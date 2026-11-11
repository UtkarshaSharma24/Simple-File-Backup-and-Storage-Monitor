"""test_backup.py - simple tests for backup and restore (no Streamlit needed).

Run with:  python test_backup.py
"""

import os
import tempfile

import backup_utils
import database


def check(condition, text):
    print(("PASS  " if condition else "FAIL  ") + text)
    if not condition:
        raise SystemExit(1)


with tempfile.TemporaryDirectory() as temp:
    db = os.path.join(temp, "test.db")
    backups = os.path.join(temp, "backups")
    database.create_table(db)

    # Sample file and folder
    sample_file = os.path.join(temp, "notes.txt")
    with open(sample_file, "w") as f:
        f.write("hello backup")
    sample_folder = os.path.join(temp, "project")
    os.makedirs(os.path.join(sample_folder, "sub"))
    with open(os.path.join(sample_folder, "a.txt"), "w") as f:
        f.write("file A")
    with open(os.path.join(sample_folder, "sub", "b.txt"), "w") as f:
        f.write("file B")

    # 1. File backup
    ok, msg = backup_utils.create_backup(sample_file, backups, db)
    check(ok and len(os.listdir(backups)) == 1, "File backup created")

    # 2. Folder backup
    ok, msg = backup_utils.create_backup(sample_folder, backups, db)
    check(ok and len(os.listdir(backups)) == 2, "Folder backup created")

    # 3. Same file backed up twice in the same second -> no overwrite
    backup_utils.create_backup(sample_file, backups, db)
    check(len(os.listdir(backups)) == 3, "Second backup did not overwrite first")

    # 4. Validation errors
    ok, msg = backup_utils.create_backup("", backups, db)
    check(not ok, "Empty path rejected")
    ok, msg = backup_utils.create_backup(os.path.join(temp, "nope.txt"), backups, db)
    check(not ok, "Missing file rejected")
    empty = os.path.join(temp, "empty.txt")
    open(empty, "w").close()
    ok, msg = backup_utils.create_backup(empty, backups, db)
    check(not ok, "Empty file rejected")
    ok, msg = backup_utils.create_backup(backups, backups, db)
    check(not ok, "Backing up the backup folder rejected")
    ok, msg = backup_utils.create_backup(temp, backups, db)
    check(not ok, "Folder containing the backup folder rejected")

    # 5. Database records
    history = database.get_history(db)
    good = database.get_successful_backups(db)
    check(len(good) == 3, "3 successful backups stored in SQLite")
    check(sum(r["status"] == "Failed" for r in history) == 5, "5 failed attempts logged")
    check(all(r["backup_date"] and r["backup_time"] for r in history), "Date and time stored")
    sizes = {r["item_type"]: r["size_bytes"] for r in good}
    check(sizes["File"] == 12 and sizes["Folder"] == 12, "Backup size stored (file 12 B, folder 12 B)")

    # 6. Restore file into a new folder
    file_backup = [b for b in good if b["item_type"] == "File"][0]
    out = os.path.join(temp, "restored")
    ok, msg = backup_utils.restore_backup(file_backup["backup_path"],
                                          file_backup["file_name"], out, db)
    restored_file = os.path.join(out, "notes.txt")
    check(ok and open(restored_file).read() == "hello backup", "File restored with correct content")

    # 7. Restore again -> existing file must NOT be overwritten
    with open(restored_file, "w") as f:
        f.write("MY NEW EDITS")
    ok, msg = backup_utils.restore_backup(file_backup["backup_path"],
                                          file_backup["file_name"], out, db)
    check(ok and open(restored_file).read() == "MY NEW EDITS", "Existing file not overwritten")
    check(os.path.exists(os.path.join(out, "notes_restored.txt")), "Restored copy got a new name")

    # 8. Restore folder (twice, to test no overwrite for folders)
    folder_backup = [b for b in good if b["item_type"] == "Folder"][0]
    ok, msg = backup_utils.restore_backup(folder_backup["backup_path"],
                                          folder_backup["file_name"], out, db)
    check(ok and open(os.path.join(out, "project", "sub", "b.txt")).read() == "file B",
          "Folder restored with sub-folder content")
    ok, msg = backup_utils.restore_backup(folder_backup["backup_path"],
                                          folder_backup["file_name"], out, db)
    check(ok and os.path.isdir(os.path.join(out, "project_restored")),
          "Second folder restore used a new name")

    # 9. Restore errors
    ok, msg = backup_utils.restore_backup(os.path.join(temp, "gone"), "x", out, db)
    check(not ok, "Missing backup file handled")
    ok, msg = backup_utils.restore_backup(file_backup["backup_path"], "notes.txt", "", db)
    check(not ok, "Empty restore folder handled")

    # 10. Disk space
    total, used, free = backup_utils.get_disk_space(temp)
    check(total > 0 and used >= 0 and free >= 0, "Disk space values read")
    check(backup_utils.format_size(1536) == "1.50 KB", "format_size works")

    check(len(database.get_history(db)) == 14, "Restore actions also logged in history")

print("\nAll tests passed.")

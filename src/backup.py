import sqlite3
import os
from datetime import datetime, timedelta


def backup_database(DB_PATH, BACKUP_DIR):
    """Backs up the SQLite database."""

    # Create filepath for upcoming backup
    datestamp = datetime.now().strftime("%Y-%m-%d")
    backup_db_path = os.path.join(BACKUP_DIR, f"funtimes_{datestamp}.db")

    # Remove backups older than 7 days old
    one_week_ago = datetime.now() - timedelta(7)

    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith("funtimes_"):

            try:
                # Extract date from filename
                backup_date_str = filename[:-3].split("_")[1]
                backup_date = datetime.strptime(backup_date_str, "%Y-%m-%d")

                if backup_date < one_week_ago:
                    backup_path = os.path.join(BACKUP_DIR, filename)
                    os.remove(backup_path)
                    print(f"Removed old backup: {backup_path}")

            except ValueError:
                print(f"Skipping file with invalid date format: {filename}")

    # Backup DB
    try:
        db = sqlite3.connect(DB_PATH)

        # Use the backup API to create a consistent copy
        backup_conn = sqlite3.connect(backup_db_path)
        with backup_conn:
            db.backup(backup_conn)

        db.close()
        backup_conn.close()

        print(f"Database backed up successfully to: {backup_db_path}")

    except sqlite3.Error as e:
        print(f"Error backing up database: {e}")


if __name__ == "__main__":
    DB_PATH = os.path.join("..", "storage", "funtimes.db")
    BACKUP_DIR = os.path.join("..", "storage", "backups")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    backup_database(DB_PATH, BACKUP_DIR)

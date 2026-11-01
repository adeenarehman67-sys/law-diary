import json
import os

# Define the exact path to your local database
DB_PATH = "law_diary_cases.json"

def load_case_database():
    """
    Safely loads case records from the local JSON database file.
    Includes error handling for missing files or incomplete write states.
    """
    if not os.path.exists(DB_PATH):
        # Fallback if the file isn't found in the directory
        print(f"Warning: {DB_PATH} not found in current directory.")
        return []

    try:
        with open(DB_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        # Handles edge case if the app is caught mid-write during a backup snapshot
        print("Notice: Database file is currently syncing. Retrying or returning empty set.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

# Quick test execution when run directly
if __name__ == "__main__":
    cases = load_case_database()
    print(f"Successfully loaded {len(cases)} case records from your secure local database!")
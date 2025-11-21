import sqlite3
import os

db_path = 'cache/cache.db'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables in {db_path}:\n")
    
    for table_name in tables:
        table = table_name[0]
        print(f"--- Table: {table} ---")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table});")
        columns_info = cursor.fetchall()
        columns = [info[1] for info in columns_info]
        print(f"Columns: {', '.join(columns)}")
        
        # Get data
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        if not rows:
            print("Table is empty.")
        else:
            # Calculate column widths
            col_widths = [len(c) for c in columns]
            for row in rows:
                for i, val in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(val)))
            
            # Print header
            header = " | ".join(f"{col:<{w}}" for col, w in zip(columns, col_widths))
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                print(" | ".join(f"{str(val):<{w}}" for val, w in zip(row, col_widths)))
                
        print("\n")
        
    conn.close()

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

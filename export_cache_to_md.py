import sqlite3
import os

db_path = 'cache/cache.db'
output_file = 'cache_contents.md'

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value, store_time, access_count FROM Cache")
    rows = cursor.fetchall()
    
    with open(output_file, 'w') as f:
        f.write("# Cache Contents\n\n")
        f.write(f"Total entries: {len(rows)}\n\n")
        f.write("| Key | Value (Truncated) | Store Time | Access Count |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        for row in rows:
            key, value, store_time, access_count = row
            # Truncate value for better readability in table, but maybe keep it long enough
            # The user wants to view the db file, so maybe full content is better?
            # Let's put full content in a details block if it's long, or just the table.
            # The previous output showed full text. Let's try to keep it clean.
            
            # Clean up value for markdown table (replace newlines)
            clean_value = str(value).replace('\n', '<br>')
            if len(clean_value) > 100:
                 display_value = clean_value[:100] + "..."
            else:
                 display_value = clean_value
            
            f.write(f"| {key} | {display_value} | {store_time} | {access_count} |\n")
        
        f.write("\n\n## Full Entries\n\n")
        for row in rows:
            key, value, store_time, access_count = row
            f.write(f"### Key: {key}\n")
            f.write(f"- **Store Time**: {store_time}\n")
            f.write(f"- **Access Count**: {access_count}\n")
            f.write(f"\n**Value**:\n\n")
            f.write(f"{value}\n\n")
            f.write("---\n\n")

    print(f"Successfully exported cache to {output_file}")
    conn.close()

except Exception as e:
    print(f"An error occurred: {e}")

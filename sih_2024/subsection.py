import sqlite3
import re

# Connect to the SQLite database (or create it if it doesn't exist)
db_path = 'chapters.db'  # Path to your database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a new table for subsections
cursor.execute('''
    CREATE TABLE IF NOT EXISTS subsections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_name TEXT NOT NULL,
        subsection_header TEXT NOT NULL,
        content TEXT NOT NULL
    )
''')
conn.commit()

# Define the regex pattern for subsection headers
# Match numbers like 2.0, 2.1, 2.1.1, etc.
subsection_pattern = re.compile(r'(\d+\.\d+(\.\d+)?(?:\.\d+)?)\s*(.*)')

# Fetch the chapter content
cursor.execute("SELECT chapter_title, content FROM chapters")
chapters = cursor.fetchall()

# Process each chapter and divide it into subsections
for chapter_name, content in chapters:
    current_header = None
    current_subsection = []
    
    for line in content.splitlines():
        match = subsection_pattern.match(line.strip())
        
        if match:
            # Store the previous subsection if we have one
            if current_header and current_subsection:
                cursor.execute('''
                    INSERT INTO subsections (chapter_name, subsection_header, content)
                    VALUES (?, ?, ?)
                ''', (chapter_name, current_header, '\n'.join(current_subsection)))
            
            # Start a new subsection
            current_header = match.group(1) + " " + match.group(3)  # Header number + title
            current_subsection = []
        else:
            # Keep collecting lines for the current subsection
            current_subsection.append(line.strip())
    
    # Store the last subsection of the chapter
    if current_header and current_subsection:
        cursor.execute('''
            INSERT INTO subsections (chapter_name, subsection_header, content)
            VALUES (?, ?, ?)
        ''', (chapter_name, current_header, '\n'.join(current_subsection)))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Subsections successfully stored in the database.")
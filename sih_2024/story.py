import sqlite3
from pdf2image import convert_from_path
import pytesseract
import re

# Function to extract text from each page and group pages by starting text
def extract_and_group_pages(pdf_path, start_page, end_page):
    pages = convert_from_path(pdf_path, first_page=start_page + 1, last_page=end_page)
    chapters = []
    current_chapter_text = ""
    current_starting_text = None

    for page_num, page in enumerate(pages, start=start_page + 1):
        text = pytesseract.image_to_string(page)
        # Get the starting text of the page (first line)
        starting_text = text.strip().split('\n')[0].strip().lower()
        starting_text = re.sub(r'\s+', ' ', starting_text)  # Normalize spaces
        starting_text = starting_text[:50]  # Limit to first 50 characters for consistency

        # Debugging output (optional)
        print(f"Processing Page {page_num}: Starting Text -> '{starting_text}'")

        if current_starting_text is None:
            # First page initialization
            current_starting_text = starting_text
            current_chapter_text = text
        elif starting_text == current_starting_text:
            # Same chapter, append text
            current_chapter_text += text
        else:
            # New chapter detected, save the current chapter and start a new one
            chapters.append(current_chapter_text)
            current_starting_text = starting_text
            current_chapter_text = text

    # Append the last chapter if any text remains
    if current_chapter_text:
        chapters.append(current_chapter_text)

    return chapters

# Function to store extracted chapters into SQLite database
def store_in_database(db_name, chapters):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    for idx, chapter in enumerate(chapters):
        chapter_title = f"Chapter {idx + 1}"
        cursor.execute('INSERT INTO chapters (chapter_title, content) VALUES (?, ?)', (chapter_title, chapter))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Define PDF path and page range
    pdf_path = 'resource/Carpentry and Woodwork-output.pdf'
    start_page = 8  # Specify the starting page (page number starts from 0)
    end_page = 20   # Specify the end page

    print("Extracting text from the PDF and grouping pages into chapters...")
    
    # Step 1: Extract text and group pages into chapters
    chapters = extract_and_group_pages(pdf_path, start_page, end_page)

    print(f"Extracted {len(chapters)} chapters.")

    # Step 2: Store extracted chapters into SQLite database
    store_in_database('chapters.db', chapters)

    print("Text extracted and stored in SQLite database successfully.")

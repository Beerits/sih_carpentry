from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import re
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure the Gemini API
api_key = "AIzaSyCJRS1Wdp-ggwC4X7hzrAgMx3nzD0ioPp4"
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to generate story options using Gemini API
def generate_story_options(section_text, selected_path):
    prompt = (
        "The reader has chosen the following path: {path}\n\n"
        "New section of text to teach : \n\n'{text}'\n\n"
        
        "First, create 'Choose Your Own Adventure' story based on the text and the chosen path."
         "Then, using newly generated story provide three distinct story paths  labeled as Path 1, Path 2, and Path 3, that the reader can choose from, each path following the main story."
    )
    
    response = model.generate_content(prompt.format(text=section_text, path=selected_path))
    
    # Parse the response to separate the main story and paths
    if response and response.text:
        # Split the response into story and paths
        parts = re.split(r'\n?Path \d+', response.text)
        story = parts[0].strip()
        paths = [part.strip() for part in parts[1:] if part.strip()]
        
        # Ensure we have exactly three paths
        while len(paths) < 3:
            paths.append(f"Path {len(paths) + 1}: No content generated")
        
        return story, [f"Path {i + 1}: {path}" for i, path in enumerate(paths[:3])]

    return "No story generated.", ["Path 1: No content generated", "Path 2: No content generated", "Path 3: No content generated"]

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('chapters.db')
    conn.row_factory = sqlite3.Row
    return conn

# API to get all chapters
@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT chapter_name FROM subsections')
    chapters = cursor.fetchall()
    conn.close()
    return jsonify([chapter['chapter_name'] for chapter in chapters])

# API to get subsections by chapter name
@app.route('/api/chapters/<chapter_name>', methods=['GET'])
def get_chapter_content(chapter_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subsection_header, content FROM subsections WHERE chapter_name = ?', (chapter_name,))
    subsections = cursor.fetchall()
    conn.close()
    
    chapter_content = [{'header': row['subsection_header'], 'content': row['content']} for row in subsections]
    return jsonify(chapter_content)

# API to generate story options
@app.route('/api/generate_story_options', methods=['POST'])
def generate_story():
    data = request.get_json()
    subsection_text = data.get('subsection_text', '')
    selected_path = data.get('selected_path', '')
    
    # Generate story and paths using the Gemini API
    story, paths = generate_story_options(subsection_text, selected_path)
    
    return jsonify({'story': story, 'paths': paths})

if __name__ == '__main__':
    app.run(debug=True)

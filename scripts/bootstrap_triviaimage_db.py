import sqlite3
import os
import random
import re

DB_PATH = '../database/triviaimage.db'
POSTERS_DIR = '../posters_blurred_east'

# Helper to extract movie title from filename
# Example: '01_The_Godfather_blurred.jpg' -> 'The Godfather'
def extract_title(filename):
    match = re.match(r'\d+_(.+?)_blurred\.jpg', filename)
    if match:
        return match.group(1).replace('_', ' ')
    return None

# Get all poster files
poster_files = [f for f in os.listdir(POSTERS_DIR) if f.endswith('_blurred.jpg')]
movie_titles = [extract_title(f) for f in poster_files if extract_title(f)]

# Generate confusing options
# For each movie, pick 3 other random titles
questions = []
for f in poster_files:
    correct = extract_title(f)
    if not correct:
        continue
    others = [t for t in movie_titles if t != correct]
    distractors = random.sample(others, 3) if len(others) >= 3 else others
    options = distractors + [correct]
    random.shuffle(options)
    answer_idx = options.index(correct) + 1  # 1-based index
    questions.append({
        'image': f,
        'opt1': options[0],
        'opt2': options[1],
        'opt3': options[2],
        'opt4': options[3],
        'answer': answer_idx
    })

# Bootstrap DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
# Create tables if not exist
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, image TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT, answer INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime TEXT, user_id INTEGER, rounds INTEGER, score INTEGER, total_time INTEGER)')
# Clear questions table
c.execute('DELETE FROM questions')
for q in questions:
    c.execute('INSERT INTO questions (image, opt1, opt2, opt3, opt4, answer) VALUES (?, ?, ?, ?, ?, ?)',
              (q['image'], q['opt1'], q['opt2'], q['opt3'], q['opt4'], q['answer']))
conn.commit()
conn.close()
print(f"Inserted {len(questions)} questions into the database.")

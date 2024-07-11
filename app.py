import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            feedback TEXT NOT NULL,
            avatar TEXT
        )
    ''')
    conn.commit()
    conn.close()

# One-time script to add avatar column to existing table
def add_avatar_column():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE feedback ADD COLUMN avatar TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

# Ensure to call this only once to update the existing schema
add_avatar_column()

# Function to get gender based on name
def get_gender(name):
    try:
        response = requests.get(f"https://api.genderize.io?name={name}")
        gender_data = response.json()
        print(f"Genderize response: {gender_data}")  # Debugging log
        return gender_data.get('gender', 'unknown')
    except Exception as e:
        print(f"Error: {e}")
        return 'unknown'

# Function to get a random avatar based on gender
def get_avatar(gender):
    male_avatars = ["male_avatar1.jpg", "male_avatar2.jpg"]
    female_avatars = ["female_avatar1.jpg", "female_avatar2.jpg"]
    default_avatars = ["face_avatar.png", "another_avatar.png"]  # Add your second default image here
    
    if gender == 'male':
        return random.choice(male_avatars)
    elif gender == 'female':
        return random.choice(female_avatars)
    else:
        return random.choice(default_avatars)

@app.route('/')
def index():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, feedback, avatar FROM feedback')
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('index.html', feedback=feedbacks)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    feedback = request.form['feedback']
    
    gender = get_gender(name)
    avatar = get_avatar(gender)
    
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (name, feedback, avatar) VALUES (?, ?, ?)', (name, feedback, avatar))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/edit_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    if request.method == 'POST':
        new_feedback = request.form['feedback']
        
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE feedback SET feedback = ? WHERE id = ?', (new_feedback, feedback_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, feedback FROM feedback WHERE id = ?', (feedback_id,))
    feedback_item = cursor.fetchone()
    conn.close()
    
    if feedback_item is None:
        return "Feedback not found", 404
    
    print(f"Fetched feedback item: {feedback_item}")  # Debugging log
    return render_template('edit_feedback.html', feedback=feedback_item)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
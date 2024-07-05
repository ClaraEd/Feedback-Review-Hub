from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            feedback TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, feedback FROM feedback')
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('index.html', feedback=feedbacks)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    feedback = request.form['feedback']
    
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (name, feedback) VALUES (?, ?)', (name, feedback))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ababab"

DATABASE = os.path.join(os.path.dirname(__file__), 'mydatabase.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)  # wait up to 10 seconds
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username  = request.form['username']
    password  = request.form['password']
    firstname = request.form['firstname']
    lastname  = request.form['lastname']
    email     = request.form['email']
    address   = request.form['address']

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO users (username, password, firstname, lastname, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password, firstname, lastname, email, address))
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            return redirect(url_for('profile', username=username))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run()


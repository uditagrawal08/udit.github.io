from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secret key for session security
app.config['DATABASE'] = os.path.join(app.root_path, 'users.db')

# Function to connect to the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

# Function to initialize the database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Close the database connection at the end of each request
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, '_database'):
        g._database.close()

# Route for the home page with login and register buttons
@app.route('/')
def home():
    return render_template('home.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        db.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

# Route for the logout page
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name= request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        db = get_db()
        db.execute('INSERT INTO users (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        db.commit()

        return redirect(url_for('login'))
    return render_template('contact.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

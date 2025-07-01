
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/chat_app?unix_socket=/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Message Table
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', backref='messages')

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/chat')
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            return "All fields are required!"

        # Check if user exists
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            return "Username or email already exists"

        # Hash password
        hashed = generate_password_hash(password)

        # Create user
        new_user = User(username=username, email=email, password=hashed)
        try:
            db.session.add(new_user)
            db.session.commit()
            print("✅ User saved:", username)
        except Exception as e:
            db.session.rollback()
            print("❌ Error inserting user:", str(e))
            return "Failed to save user"

        return redirect('/login')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password_input):
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect('/chat')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        content = request.form['message']
        if content:
            msg = Message(sender_id=session['user_id'], message=content)
            db.session.add(msg)
            db.session.commit()

    messages = Message.query.order_by(Message.timestamp).all()
    return render_template('chat.html', username=session['username'], messages=messages)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist

        # Insert test user if not exists
        if not User.query.filter_by(username="testuser").first():
            test_user = User(
                username="testuser",
                email="test@example.com",
                password=generate_password_hash("1234")
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created.")
        else:
            print("⚠️ Test user already exists.")

    app.run(debug=True)

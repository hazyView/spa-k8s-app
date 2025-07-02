import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
import logging

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Set up logging
if os.environ.get('FLASK_ENV') == 'development':
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_current = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_current': self.is_current
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

# Routes
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/auth')
def auth():
    """Auth page route for compatibility"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/dashboard')
@login_required
def dashboard_route():
    """Dashboard route for compatibility"""
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

# API routes for compatibility
@app.route('/api/login', methods=['POST'])
def api_login():
    """API login endpoint for compatibility"""
    data = request.get_json()
    
    # Handle both email and username fields for compatibility
    email = data.get('email') or data.get('username', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    """API register endpoint for compatibility"""
    data = request.get_json()
    
    # Handle both email and username fields for compatibility
    email = data.get('email') or data.get('username', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/notes')
@login_required
def get_notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@app.route('/api/notes/current')
@login_required
def get_current_note():
    current_note = Note.query.filter_by(user_id=current_user.id, is_current=True).first()
    if current_note:
        return jsonify(current_note.to_dict())
    return jsonify(None)

@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    try:
        app.logger.debug(f'Creating note for user {current_user.id}')
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        title = data.get('title', '').strip()
        content = data.get('content', '')
        
        app.logger.debug(f'Create data - Title: "{title}", Content length: {len(content)}')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Clear current note flag from other notes
        Note.query.filter_by(user_id=current_user.id, is_current=True).update({'is_current': False})
        
        note = Note(
            title=title,
            content=content,
            user_id=current_user.id,
            is_current=True
        )
        
        db.session.add(note)
        db.session.commit()
        
        app.logger.info(f'Successfully created note {note.id}: "{title}" for user {current_user.id}')
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error creating note for user {current_user.id}: {str(e)}', exc_info=True)
        return jsonify({'error': f'Failed to create note: {str(e)}'}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    try:
        app.logger.debug(f'Updating note {note_id} for user {current_user.id}')
        
        # Check if note exists and belongs to current user
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            app.logger.warning(f'Note {note_id} not found for user {current_user.id}')
            return jsonify({'error': 'Note not found'}), 404
        
        # Get and validate request data
        data = request.get_json()
        if not data:
            app.logger.warning('No JSON data provided in request')
            return jsonify({'error': 'No data provided'}), 400
            
        title = data.get('title', '').strip()
        content = data.get('content', '')
        
        app.logger.debug(f'Update data - Title: "{title}", Content length: {len(content)}')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Update note fields
        old_title = note.title
        note.title = title
        note.content = content
        note.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        app.logger.info(f'Successfully updated note {note_id}: "{old_title}" -> "{title}"')
        
        return jsonify(note.to_dict())
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating note {note_id}: {str(e)}', exc_info=True)
        return jsonify({'error': f'Failed to update note: {str(e)}'}), 500

@app.route('/api/notes/<int:note_id>/set-current', methods=['POST'])
@login_required
def set_current_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    # Clear current note flag from other notes
    Note.query.filter_by(user_id=current_user.id, is_current=True).update({'is_current': False})
    
    note.is_current = True
    
    try:
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to set current note'}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    try:
        app.logger.debug(f'Deleting note {note_id} for user {current_user.id}')
        
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            app.logger.warning(f'Note {note_id} not found for user {current_user.id}')
            return jsonify({'error': 'Note not found'}), 404
        
        note_title = note.title  # Store for logging
        
        db.session.delete(note)
        db.session.commit()
        
        app.logger.info(f'Successfully deleted note {note_id}: "{note_title}" for user {current_user.id}')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting note {note_id} for user {current_user.id}: {str(e)}', exc_info=True)
        return jsonify({'error': f'Failed to delete note: {str(e)}'}), 500

# Health check endpoint for containerization
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Initialize database
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_ENV') == 'development')
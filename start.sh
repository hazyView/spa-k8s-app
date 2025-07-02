#!/bin/bash

echo "🚀 Starting NoteTaker Application"
echo "================================="

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-change-in-production
export DATABASE_URL=sqlite:///notes.db

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
fi

# Check if all dependencies are installed
echo "📦 Checking dependencies..."
.venv/bin/python -c "
try:
    import flask, flask_sqlalchemy, flask_login, werkzeug
    print('✅ All dependencies installed')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Installing missing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi

echo ""
echo "🏗️  Setting up database..."
.venv/bin/python -c "
import os
os.environ['SECRET_KEY'] = 'dev-secret'
os.environ['DATABASE_URL'] = 'sqlite:///notes.db'
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"

echo ""
echo "🌟 Starting the application..."
echo "   📍 URL: http://localhost:5000"
echo "   🔧 Environment: Development"
echo "   💾 Database: SQLite (notes.db)"
echo ""
echo "📋 How to use:"
echo "   1. Open http://localhost:5000 in your browser"
echo "   2. Create an account or login"
echo "   3. Start creating notes!"
echo ""
echo "🛠️  Troubleshooting:"
echo "   • If you get 'Failed to save note', try creating a new note first"
echo "   • Check browser console (F12) for detailed error messages"
echo "   • Make sure you're logged in and have a current note selected"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="

.venv/bin/python app.py

# NoteTaker - Single Page Application

A sleek, minimalistic note-taking application built with Flask. Features user authentication, real-time auto-save, and a beautiful responsive interface. Designed for easy containerization and Kubernetes deployment.

## Features

### 🔐 Security & Authentication
- Secure user registration and login
- Password hashing with Werkzeug
- Session-based authentication with Flask-Login
- Email validation and secure password requirements

### 📝 Note Management
- Create, edit, and delete notes
- Real-time auto-save (saves automatically after 2 seconds of inactivity)
- Current note system - resume work where you left off
- Word count tracking
- Beautiful, responsive interface

### 🎨 User Interface
- Single Page Application (SPA) design
- Glassmorphism UI with gradient backgrounds
- Responsive design works on all devices
- Smooth animations and transitions
- Modern icons with Font Awesome


## Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Kubernetes cluster (optional)

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd spa-k8s-app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

4. **Access the app**:
Open http://localhost:5000 in your browser

### Docker Development

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

2. **Access the app**:
Open http://localhost:5000 in your browser

### Production Deployment

#### Docker

1. **Build the image**:
```bash
docker build -t notetaker:latest .
```

2. **Run with environment variables**:
```bash
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY="your-production-secret-key" \
  -e DATABASE_URL="sqlite:///notes.db" \
  notetaker:latest
```

#### Kubernetes

1. **Update the secret in k8s-deployment.yaml**:
```bash
echo -n 'your-production-secret-key' | base64
```

2. **Deploy to Kubernetes**:
```bash
kubectl apply -f k8s-deployment.yaml
```

3. **Check the deployment**:
```bash
kubectl get pods
kubectl get services
```

## Architecture

### Backend (Flask)
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Werkzeug**: Password hashing and security

### Frontend (Vanilla JS)
- **Vanilla JavaScript**: No framework dependencies
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Icon library

### Database Schema
```sql
Users:
- id (Primary Key)
- email (Unique)
- password_hash
- created_at

Notes:
- id (Primary Key)
- title
- content
- created_at
- updated_at
- user_id (Foreign Key)
- is_current (Boolean)
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Notes Management
- `GET /api/notes` - Get all user notes
- `GET /api/notes/current` - Get current active note
- `POST /api/notes` - Create new note
- `PUT /api/notes/<id>` - Update note
- `DELETE /api/notes/<id>` - Delete note
- `POST /api/notes/<id>/set-current` - Set note as current

### System
- `GET /health` - Health check endpoint

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (required in production)
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)
- `PORT`: Port to run the application (default: 5000)

### Security Features
- CSRF protection through session management
- Password hashing with salt
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM
- XSS prevention through proper templating

## Monitoring & Health

The application includes:
- Health check endpoint at `/health`
- Kubernetes liveness and readiness probes
- Resource limits and requests configured
- Graceful error handling

## Customization

### Styling
- Modify `templates/base.html` for global styles
- Update CSS classes in templates for UI changes
- Customize color scheme in the gradient background

### Features
- Add note categories or tags
- Implement note sharing
- Add export functionality
- Integrate with cloud storage

## Troubleshooting

### Common Issues

1. **Database not found**:
   - Ensure the database is created: The app creates it automatically on first run

2. **Permission denied in Docker**:
   - Check file permissions and Docker user configuration

3. **Health check failing**:
   - Verify the `/health` endpoint is accessible
   - Check application logs for errors

### Logs
```bash
# Docker logs
docker logs <container-id>

# Kubernetes logs
kubectl logs <pod-name>
```

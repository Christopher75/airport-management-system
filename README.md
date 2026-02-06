# NAIA Airport Management System

A comprehensive airport management system for Nnamdi Azikiwe International Airport (NAIA), Abuja, Nigeria. This system provides flight booking, real-time flight tracking, passenger management, and analytics for airport operations.

**Developer:** Christopher Ishaku Danladi (ID: 121-012)
**Institution:** Cavendish University Uganda
**Supervisor:** Mr. Kumakech Michael

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## Overview

The NAIA Airport Management System is a full-featured web application designed to modernize airport operations and enhance the passenger experience. Built with Django and modern web technologies, it provides:

- Online flight booking and ticketing
- Real-time flight status tracking
- User account management with role-based access
- Payment processing via Paystack
- Administrative analytics dashboard
- RESTful API for mobile/third-party integration

---

## Features

### For Passengers
- **Flight Search & Booking**: Search flights by route, date, and class
- **Multi-step Booking Flow**: Intuitive process (search → select → passengers → review → payment)
- **E-Tickets**: Downloadable PDF tickets with barcodes
- **User Dashboard**: View bookings, manage profile, track flights
- **Real-time Updates**: Flight status notifications via email and in-app

### For Airlines
- **Flight Management**: Schedule and manage flights
- **Aircraft Management**: Track fleet and assignments
- **Passenger Manifests**: View booking details

### For Airport Staff
- **Analytics Dashboard**: Revenue, bookings, and operations metrics
- **Flight Status Board**: Real-time departures and arrivals
- **User Management**: Admin controls for user accounts

### Technical Features
- **RESTful API**: Full API with JWT authentication
- **Swagger/ReDoc Documentation**: Interactive API docs
- **Payment Integration**: Secure payments via Paystack
- **Responsive Design**: Mobile-friendly with Tailwind CSS
- **Security**: CSRF protection, rate limiting, secure headers

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Django 5.x |
| Language | Python 3.11+ |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Cache/Queue | Redis, Celery |
| API | Django REST Framework |
| Authentication | JWT (SimpleJWT), django-allauth |
| Frontend | Tailwind CSS, JavaScript, Chart.js |
| PDF Generation | ReportLab |
| Payment Gateway | Paystack |
| API Documentation | drf-spectacular (OpenAPI 3.0) |

---

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (for production)
- Redis (for caching and Celery)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/airport-management.git
   cd airport-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load seed data (optional)**
   ```bash
   python manage.py seed_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API docs: http://localhost:8000/api/docs

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DB_NAME=airport_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Paystack Payment Gateway
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=NAIA <noreply@naia.ng>
```

---

## Usage

### Running the Application

```bash
# Development server
python manage.py runserver

# With specific settings
python manage.py runserver --settings=airport_system.settings.development

# Production (with Gunicorn)
gunicorn airport_system.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Background Tasks (Celery)

```bash
# Start Celery worker
celery -A airport_system worker --loglevel=info

# Start Celery beat (scheduled tasks)
celery -A airport_system beat --loglevel=info
```

### Management Commands

```bash
# Seed database with test data
python manage.py seed_data

# Clear expired sessions
python manage.py clearsessions

# Collect static files (production)
python manage.py collectstatic
```

---

## API Documentation

### Authentication

The API uses JWT (JSON Web Tokens) for authentication.

**Obtain Token:**
```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1Q...",
    "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

**Use Token:**
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/v1/flights/
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token/` | POST | Obtain JWT tokens |
| `/api/v1/auth/token/refresh/` | POST | Refresh access token |
| `/api/v1/auth/register/` | POST | Register new user |
| `/api/v1/airports/` | GET | List all airports |
| `/api/v1/airlines/` | GET | List all airlines |
| `/api/v1/flights/` | GET | List/search flights |
| `/api/v1/bookings/` | GET, POST | User bookings |
| `/api/v1/payments/` | GET | Payment records |
| `/api/v1/notifications/` | GET | User notifications |
| `/api/v1/profile/` | GET, PATCH | User profile |
| `/api/v1/dashboard/stats/` | GET | Dashboard statistics |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestBookingModel

# Run with markers
pytest -m "api"          # API tests only
pytest -m "integration"  # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

### Test Structure

```
tests/
├── __init__.py
├── test_models.py      # Model unit tests
├── test_views.py       # View tests
├── test_api.py         # API endpoint tests
└── test_integration.py # Integration tests
```

### Coverage Report

After running tests with coverage, view the report:
```bash
# Open in browser
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

---

## Deployment

### Production Checklist

1. **Set Environment Variables**
   ```bash
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate --settings=airport_system.settings.production
   ```

4. **Configure Gunicorn**
   ```bash
   gunicorn airport_system.wsgi:application \
       --bind 0.0.0.0:8000 \
       --workers 4 \
       --threads 2 \
       --timeout 60
   ```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Project Structure

```
airport-management/
├── airport_system/          # Main Django project
│   ├── settings/
│   │   ├── base.py         # Base settings
│   │   ├── development.py  # Development settings
│   │   └── production.py   # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── accounts/               # User authentication & profiles
├── airlines/               # Airline & fleet management
├── flights/                # Flight scheduling & airports
├── bookings/               # Booking & reservation system
├── payments/               # Payment processing (Paystack)
├── notifications/          # Notification system
├── analytics/              # Analytics & reporting dashboard
├── api/                    # REST API endpoints
├── core/                   # Shared utilities & middleware
├── templates/              # HTML templates
│   ├── base.html
│   ├── account/           # Authentication templates
│   ├── core/              # Public pages
│   ├── flights/           # Flight templates
│   ├── bookings/          # Booking flow templates
│   ├── accounts/          # Dashboard templates
│   └── analytics/         # Admin analytics
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── tests/                  # Test suite
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_api.py
│   └── test_integration.py
├── manage.py
├── requirements.txt
├── pytest.ini
├── conftest.py
└── README.md
```

---

## User Roles

| Role | Permissions |
|------|-------------|
| **PASSENGER** | Book flights, manage profile, view bookings, earn loyalty points |
| **AIRLINE_STAFF** | Manage airline flights, view bookings, update flight status |
| **AIRPORT_STAFF** | View all flights, manage gates, access operations dashboard |
| **ADMIN** | Full system access, user management, analytics |

---

## Database Models

### Core Models (15+)

- **accounts**: CustomUser, UserProfile
- **airlines**: Airline, Aircraft
- **flights**: Airport, Gate, Flight
- **bookings**: Booking, Passenger, Seat
- **payments**: Payment
- **notifications**: Notification, NotificationPreference

---

## Development Phases Completed

- **Phase 1**: Foundation - Project setup, models, authentication, admin ✅
- **Phase 2**: Core Features - Public pages, flight search, booking flow, dashboard ✅
- **Phase 3**: Advanced Features - Payment integration, notifications, real-time tracking, analytics ✅
- **Phase 4**: Enhancement - REST API, documentation, caching, security hardening ✅
- **Phase 5**: Testing & Documentation - Unit tests, integration tests, documentation ✅

---

## License

This project is developed for academic purposes as a final year project at Cavendish University Uganda.

---

## Support

For support, contact:
- **Email**: support@naia.ng
- **Phone**: +234 9 123 4567

---

**Built with Django for Nnamdi Azikiwe International Airport, Nigeria**

# SmartBank - Complete Project Structure

## Project Overview

This is a comprehensive banking application built with Flask, MongoDB, and modern web technologies. It features user authentication, transaction management, bill payments, admin dashboard, and an AI-powered chatbot.

## Directory Structure

```
smartbank/
├── app.py                          # Main Flask application
├── database.py                     # MongoDB connection and setup
├── db_config.py                    # Alternative database configuration
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (see .env.example)
├── .env.example                   # Template for environment variables
├── README.md                      # Project documentation
├── run.py                         # Application runner script
├── config.py                      # Application configuration
├── services/                      # Business logic services
│   ├── __init__.py
│   ├── account_service.py         # Account management
│   ├── auth_service.py            # Authentication and 2FA
│   ├── biller_service.py          # Bill payment providers
│   ├── chatbot_service.py         # AI chatbot integration
│   ├── email_service.py           # Email notifications
│   ├── report_service.py          # Reports and analytics
│   ├── transaction_service.py     # Transaction processing
│   └── user_service.py            # User management
├── templates/                     # HTML templates
│   └── index.html                 # Main application template
├── static/                        # Static assets
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── images/
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_services.py
│   └── test_api.py
└── docs/                          # Documentation
    ├── API.md
    ├── DEPLOYMENT.md
    └── DEVELOPMENT.md
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Gmail account for email notifications
- Google Gemini API key for chatbot

### 1. Clone and Setup Virtual Environment

```bash
git clone <your-repo-url>
cd smartbank
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

### 3. Database Setup

- For local MongoDB: Ensure MongoDB is running on localhost:27017
- For MongoDB Atlas: Update MONGO_URI in .env with your connection string

### 4. Run the Application

```bash
python app.py
```

or

```bash
python run.py
```

The application will be available at http://localhost:5000

## Key Features

### User Features

- **Registration & Login**: Secure user registration with email verification
- **Two-Factor Authentication**: Email-based 2FA for enhanced security
- **Dashboard**: Account overview with balance, recent transactions, and insights
- **Money Transfer**: Send money to other accounts with real-time balance updates
- **Bill Payment**: Pay bills to various service providers
- **Transaction History**: View and filter transaction history
- **AI Chatbot**: Get help with banking queries using Google Gemini AI
- **Profile Management**: Update personal information and security settings

### Admin Features

- **Admin Dashboard**: System overview with key metrics
- **User Management**: View, create, suspend, and delete user accounts
- **Transaction Monitoring**: View and manage all system transactions
- **Reports**: Generate and download transaction reports in CSV format
- **Security Center**: Monitor system security and access logs

### Technical Features

- **Modern UI**: Responsive design with glassmorphism effects and animations
- **Real-time Updates**: Dynamic content updates without page refresh
- **Secure Authentication**: JWT tokens with proper expiration handling
- **Database Transactions**: ACID compliance for financial operations
- **Error Handling**: Comprehensive error handling and user feedback
- **Email Integration**: Automated email notifications for 2FA codes
- **API Architecture**: RESTful API design with proper HTTP status codes

## API Endpoints

### Authentication

- `POST /api/register` - User registration
- `POST /api/login` - User login (sends 2FA code)
- `POST /api/login/verify` - Verify 2FA code
- `POST /api/admin/login` - Admin login

### User Operations

- `GET /api/account` - Get user account details
- `GET /api/transactions` - Get user transactions
- `POST /api/transactions` - Create money transfer
- `GET /api/billers` - Get available billers
- `POST /api/bill-payment` - Pay a bill
- `GET /api/insights` - Get spending insights
- `POST /api/chatbot` - Chat with AI assistant

### Admin Operations

- `GET /api/admin/users` - Get all users
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/<id>` - Update user status
- `DELETE /api/admin/users/<id>` - Delete user
- `GET /api/admin/transactions` - Get all transactions
- `PUT /api/admin/transactions/<id>` - Update transaction
- `DELETE /api/admin/transactions/<id>` - Delete transaction
- `GET /api/admin/stats` - Get dashboard statistics
- `GET /api/admin/reports/transactions.csv` - Download transaction report

## Default Credentials

- **Admin**: username: `admin`, password: `admin123`
- **Regular users**: Create through registration or admin panel

## Security Features

- Password hashing using PBKDF2-SHA256
- JWT token-based authentication
- Two-factor authentication via email
- Input validation and sanitization
- SQL injection protection (using MongoDB)
- Session management with token expiration
- Admin-only routes protection

## Environment Variables

Required environment variables in `.env`:

```
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```

## Development Notes

- The application uses MongoDB for data persistence
- All financial operations use database transactions for consistency
- The frontend is a single-page application with dynamic content loading
- The AI chatbot requires a valid Google Gemini API key
- Email functionality requires Gmail app passwords for security

## Deployment Considerations

- Set strong SECRET_KEY for production
- Use environment variables for all sensitive configuration
- Enable MongoDB authentication in production
- Configure proper email server settings
- Set up proper logging and monitoring
- Use HTTPS in production
- Configure rate limiting for API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with financial regulations if used in production.

#!/usr/bin/env python3
"""
SmartBank Application Runner

This script provides a convenient way to run the SmartBank application
with proper initialization and error handling.
"""

import os
import sys
from app import app
from services import user_service, biller_service

def check_environment():
"""Check if all required environment variables are set."""
required_vars = ['SECRET_KEY', 'MONGO_URI']
optional_vars = ['GEMINI_API_KEY', 'EMAIL_USER', 'EMAIL_PASS']

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_required.append(var)

    for var in optional_vars:
        if not os.environ.get(var):
            missing_optional.append(var)

    if missing_required:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_required)}")
        print("Please create a .env file based on .env.example")
        return False

    if missing_optional:
        print(f"WARNING: Missing optional environment variables: {', '.join(missing_optional)}")
        print("Some features may not work properly.")

    return True

def initialize_app():
"""Initialize the application with default data."""
print("Initializing SmartBank...")

    try:
        with app.app_context():
            # Create admin user if it doesn't exist
            user_service.create_admin_user_if_not_exists()

            # Initialize billers
            biller_service.initialize_billers()

        print("✅ Application initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return False

def main():
"""Main entry point for the application."""
print("🏦 Starting SmartBank Application...")

    # Check environment variables
    if not check_environment():
        sys.exit(1)

    # Initialize the application
    if not initialize_app():
        sys.exit(1)

    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"🚀 Starting server on http://{host}:{port}")
    print("📝 Default admin credentials: admin / admin123")
    print("⏹️  Press Ctrl+C to stop the server")

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 SmartBank application stopped.")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if **name** == '**main**':
"""
Configuration module for SmartBank application.

This module contains configuration classes for different environments.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

class Config:
"""Base configuration class."""

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database Configuration
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    DATABASE_NAME = 'smart_ebanking'

    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Email Configuration
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')
    EMAIL_USE_SSL = True

    # JWT Configuration
    JWT_EXPIRATION_DELTA = 24 * 60 * 60  # 24 hours in seconds
    JWT_ADMIN_EXPIRATION_DELTA = 8 * 60 * 60  # 8 hours for admin

    # 2FA Configuration
    TFA_CODE_EXPIRATION_MINUTES = 10

    # Security Settings
    BCRYPT_LOG_ROUNDS = 12

    # Application Settings
    DEFAULT_ACCOUNT_BALANCE = 5000.00
    MAX_TRANSACTION_AMOUNT = 50000.00
    MIN_TRANSACTION_AMOUNT = 0.01

class DevelopmentConfig(Config):
"""Development environment configuration."""

    DEBUG = True
    TESTING = False

    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'

    # Relaxed security for development
    BCRYPT_LOG_ROUNDS = 4

class ProductionConfig(Config):
"""Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Enhanced security for production
    BCRYPT_LOG_ROUNDS = 15

    # Production logging
    LOG_LEVEL = 'INFO'

    # Validate required environment variables
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            'SECRET_KEY',
            'MONGO_URI',
            'EMAIL_USER',
            'EMAIL_PASS',
        ]

        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

class TestingConfig(Config):
"""Testing environment configuration."""

    DEBUG = True
    TESTING = True

    # Use separate test database
    DATABASE_NAME = 'smart_ebanking_test'

    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 1

    # Disable external services in tests
    EMAIL_ENABLED = False
    GEMINI_API_ENABLED = False

# Configuration mapping

config = {
'development': DevelopmentConfig,
'production': ProductionConfig,
'testing': TestingConfig,
'default': DevelopmentConfig
}

def get_config():
"""Get the appropriate configuration based on environment."""
env = os.environ.get('FLASK_ENV', 'development')
return config.get(env, config['default'])
main() # SmartBank - Modern Banking Application

A comprehensive banking application built with Flask, MongoDB, and modern web technologies. Features user authentication, transaction management, bill payments, admin dashboard, and an AI-powered chatbot.

## Features

### 🔐 Security Features

- **Two-Factor Authentication** - Email-based 2FA for enhanced security
- **JWT Token Authentication** - Secure token-based authentication
- **Password Hashing** - PBKDF2-SHA256 encryption
- **Admin Access Control** - Separate admin interface with enhanced permissions

### 💳 Banking Features

- **Account Management** - View balance and account details
- **Money Transfers** - Send money between accounts with real-time updates
- **Bill Payments** - Pay bills to various service providers
- **Transaction History** - Complete transaction tracking with filtering
- **Spending Insights** - Visual analytics of spending patterns

### 🤖 AI Features

- **Smart Chatbot** - Google Gemini-powered banking assistant
- **Contextual Help** - AI assistant with access to user account information
- **Natural Language Processing** - Handle banking queries in natural language

### 👑 Admin Features

- **User Management** - Create, suspend, and manage user accounts
- **Transaction Monitoring** - View and manage all system transactions
- **Analytics Dashboard** - System statistics and insights
- **Report Generation** - Export transaction data as CSV
- **Security Monitoring** - Access logs and security alerts

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB with PyMongo
- **Frontend**: HTML5, CSS3, JavaScript, TailwindCSS
- **AI**: Google Gemini API
- **Authentication**: JWT tokens, bcrypt password hashing
- **Email**: SMTP integration for 2FA codes
- **Charts**: Chart.js for data visualization

## Quick Start

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Gmail account (for email notifications)
- Google Gemini API key

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd smartbank

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:

```env
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secure-secret-key
GEMINI_API_KEY=your-gemini-api-key
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
```

### 3. Run the Application

```bash
# Using the runner script (recommended)
python run.py

# Or directly
python app.py
```

The application will be available at `http://localhost:5000`

### 4. Default Credentials

- **Admin**: `admin` / `admin123`
- **Users**: Register new accounts through the interface

## API Documentation

### Authentication Endpoints

```
POST /api/register          # User registration
POST /api/login             # User login (sends 2FA)
POST /api/login/verify      # Verify 2FA code
POST /api/admin/login       # Admin login
```

### User Endpoints

```
GET  /api/account           # Get account details
GET  /api/transactions      # Get user transactions
POST /api/transactions      # Create transfer
GET  /api/billers          # Get available billers
POST /api/bill-payment     # Pay bill
GET  /api/insights         # Get spending insights
POST /api/chatbot          # AI chatbot interaction
```

### Admin Endpoints

```
GET    /api/admin/users               # Get all users
POST   /api/admin/users               # Create user
PUT    /api/admin/users/<id>          # Update user
DELETE /api/admin/users/<id>          # Delete user
GET    /api/admin/transactions        # All transactions
PUT    /api/admin/transactions/<id>   # Update transaction
DELETE /api/admin/transactions/<id>   # Delete transaction
GET    /api/admin/stats               # Dashboard stats
GET    /api/admin/reports/transactions.csv  # Download report
```

## Project Structure

```
smartbank/
├── app.py                     # Main Flask application
├── database.py                # MongoDB connection
├── config.py                  # Configuration management
├── run.py                     # Application runner
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── services/                 # Business logic
│   ├── __init__.py
│   ├── account_service.py
│   ├── auth_service.py
│   ├── biller_service.py
│   ├── chatbot_service.py
│   ├── email_service.py
│   ├── report_service.py
│   ├── transaction_service.py
│   └── user_service.py
├── templates/                # HTML templates
│   └── index.html
└── static/                   # Static assets
    ├── css/
    ├── js/
    └── images/
```

## Database Schema

### Users Collection

```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "is_admin": "boolean",
  "status": "active|suspended",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### Accounts Collection

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "account_number": "string",
  "balance": "decimal",
  "type": "checking"
}
```

### Transactions Collection

```json
{
  "_id": "ObjectId",
  "from_account": "string",
  "to_account": "string",
  "amount": "decimal",
  "type": "string",
  "description": "string",
  "timestamp": "datetime"
}
```

## Security Considerations

- All passwords are hashed using PBKDF2-SHA256
- JWT tokens expire after 24 hours (8 hours for admin)
- 2FA codes expire after 10 minutes
- Input validation on all API endpoints
- MongoDB injection protection through PyMongo
- Session management with secure tokens

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=True

# Run with auto-reload
python run.py
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=services
```

## Deployment

### Environment Variables for Production

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<strong-secret-key>
MONGO_URI=<production-mongodb-uri>
GEMINI_API_KEY=<your-gemini-key>
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=<production-email>
EMAIL_PASS=<app-password>
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes. Please ensure compliance with financial regulations if used in production environments.

## Support

For support, please open an issue on GitHub or contact the development team.

---

**Note**: This is a demonstration application. For production use, additional security measures, compliance requirements, and testing would be necessary.

# tests/**init**.py

"""Test package for SmartBank application."""

# tests/test_services.py

"""Unit tests for service modules."""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
import datetime

# Import services to test

from services import user_service, auth_service, transaction_service, account_service

class TestUserService(unittest.TestCase):
"""Test cases for user service."""

    @patch('services.user_service._get_users_collection')
    def test_create_user_success(self, mock_get_collection):
        """Test successful user creation."""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None  # User doesn't exist
        mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_collection.find_one.return_value = {
            '_id': ObjectId(),
            'username': 'testuser',
            'email': 'test@example.com',
            'created_at': datetime.datetime.utcnow(),
            'is_admin': False,
            'status': 'active'
        }

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

        result, status_code = user_service.create_user(data)

        self.assertEqual(status_code, 201)
        self.assertIn('User registered successfully', result['message'])

    @patch('services.user_service._get_users_collection')
    def test_create_user_duplicate_username(self, mock_get_collection):
        """Test user creation with duplicate username."""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = {'username': 'existing_user'}

        data = {
            'username': 'existing_user',
            'email': 'new@example.com',
            'password': 'password123'
        }

        result, status_code = user_service.create_user(data)

        self.assertEqual(status_code, 409)
        self.assertIn('Username already exists', result['message'])

class TestAuthService(unittest.TestCase):
"""Test cases for authentication service."""

    @patch('services.auth_service._get_users_collection')
    @patch('services.auth_service.email_service.send_2fa_code')
    def test_login_success(self, mock_send_email, mock_get_collection):
        """Test successful login with 2FA."""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_send_email.return_value = True

        # Mock user data
        mock_user = {
            '_id': ObjectId(),
            'username': 'testuser',
            'password': 'hashed_password',
            'email': 'test@example.com',
            'is_admin': False,
            'status': 'active'
        }
        mock_collection.find_one.return_value = mock_user

        with patch('werkzeug.security.check_password_hash', return_value=True):
            result, status_code = auth_service.login('testuser', 'password123')

        self.assertEqual(status_code, 200)
        self.assertIn('2FA code sent', result['message'])
        self.assertIn('user_id', result)

    @patch('services.auth_service._get_users_collection')
    def test_login_invalid_credentials(self, mock_get_collection):
        """Test login with invalid credentials."""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None

        result, status_code = auth_service.login('nonexistent', 'wrong_password')

        self.assertEqual(status_code, 401)
        self.assertIn('Invalid username or password', result['message'])

class TestTransactionService(unittest.TestCase):
"""Test cases for transaction service."""

    @patch('services.transaction_service._get_collections')
    def test_create_transfer_success(self, mock_get_collections):
        """Test successful money transfer."""
        mock_transactions = MagicMock()
        mock_accounts = MagicMock()
        mock_get_collections.return_value = (mock_transactions, mock_accounts, None)

        # Mock account data
        from_account = {
            '_id': ObjectId(),
            'user_id': ObjectId(),
            'account_number': 'ACC123456789',
            'balance': 1000.0
        }
        to_account = {
            '_id': ObjectId(),
            'account_number': 'ACC987654321',
            'balance': 500.0
        }

        mock_accounts.find_one.side_effect = [from_account, to_account]

        # Mock database session


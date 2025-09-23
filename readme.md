SmartBank - AI-Powered Banking Application
A comprehensive banking application built with Flask, MongoDB, and modern web technologies. This project demonstrates a secure, feature-rich platform with user authentication, transaction management, an admin dashboard, and an integrated AI-powered chatbot.

Project Overview
SmartBank is a full-stack banking solution designed to showcase key features of a modern digital banking platform. It includes:

Secure Authentication: User and admin login with two-factor authentication (2FA) and JSON Web Tokens (JWT).

Financial Operations: Core functionalities like money transfers, bill payments, deposits, and withdrawals.

Data-Driven Insights: A dashboard with user-specific spending insights and a dedicated admin panel for system-wide monitoring.

AI-Powered Assistance: A conversational chatbot integrated using the Google Gemini API to provide instant help and answer banking queries.

Key Features
User Features
Registration & Login: Secure user registration with email-based 2FA.

Dashboard: A personalized overview of account balance and recent transactions.

Money Transfers: Seamlessly send money to other bank accounts.

Bill Payment: Pay bills to a list of pre-configured billers.

AI Chatbot: Get assistance with banking questions 24/7.

Financial Insights: View visual breakdowns of spending habits.

Admin Features
Admin Dashboard: A high-level view of system metrics, including total users and daily transactions.

User Management: Activate, suspend, or delete user accounts.

Transaction Monitoring: View a complete history of all transactions on the platform.

Reports: Generate and download PDF and CSV reports of transactions.

Technical Features
Backend: Robust RESTful API built with Flask.

Database: MongoDB for flexible, scalable data storage.

Authentication: JWT tokens for secure, stateless sessions.

Concurrency: Database transactions for financial operations to ensure data integrity.

Frontend: Responsive, modern single-page application (SPA) using HTML, CSS, and JavaScript.

AI Integration: Direct communication with the Google Gemini API for the chatbot functionality.

Quick Start
Prerequisites
Python 3.8+

MongoDB (local instance or a cloud service like MongoDB Atlas)

Google Gemini API Key

Gmail account (for email-based 2FA)

1. Clone the repository
   git clone <your-repo-url>
   cd smartbank

2. Set up the Python Virtual Environment

# Create a virtual environment

python -m venv venv

# Activate the environment

source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

3. Configure Environment Variables
   Copy the .env.example file to .env and fill in your details.

cp .env.example .env

Open the new .env file and add your credentials:

MONGO_URI="mongodb://localhost:27017/smartbank"
SECRET_KEY="a-very-secure-and-long-secret-key-that-you-should-change"
GEMINI_API_KEY="your-google-gemini-api-key"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=465
EMAIL_USER="your-email@gmail.com"
EMAIL_PASS="your-gmail-app-password"

4. Run the Application
   Start the server using the main application file. This will automatically seed the database with an admin user, sample users, and billers.

python app.py

The application will be available at http://localhost:5000.

Default Credentials
Admin: admin / admin123

Sample User: sampleuser / password123

New Users: Register an account through the application's login page.

Project Structure
smartbank/
├── app.py # Main Flask application
├── database.py # MongoDB connection and setup
├── requirements.txt # Python dependencies
├── .env.example # Template for environment variables
├── .env # Your local environment variables
├── services/ # Backend business logic services
│ ├── account_service.py
│ ├── auth_service.py
│ ├── biller_service.py
│ ├── chatbot_service.py # AI chatbot logic
│ ├── ...
├── static/ # Frontend assets
│ ├── css/
│ │ └── style.css
│ ├── js/
│ │ ├── api.js
│ │ ├── auth.js
│ │ ├── chatbot.js # Chatbot UI and API calls
│ │ ├── dashboard.js
│ │ └── main.js
│ └── ...
└── templates/ # HTML templates
└── index.html # The single-page application file

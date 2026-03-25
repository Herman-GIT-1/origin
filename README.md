# 🏫 University Portal — Flask Web Application

A full-stack web application simulating a university management portal. Built with Python and Flask as a first-year academic project.

---

## ✨ Features

### 👥 Role-Based Access Control
Three distinct account types with separate dashboards and permissions:
- **Student** — enroll in courses, view schedule, manage profile
- **Teacher** — manage assigned courses, view enrolled students, set consultation hours
- **Admin** — full control over users, courses, and platform data

### 📚 Course Management
- Create, update, and delete courses (CRUD)
- Assign teachers to courses
- Students can enroll/unenroll
- Grade tracking via the Enrollment model

### 📅 Schedule System
- Per-course scheduling with date, start time, and end time
- Cascade-delete: removing a course removes its schedule automatically

### 💳 PayPal Integration (Sandbox)
- Payout functionality using PayPal REST API (sandbox mode)
- Payout history stored in the database per user
- Tracks batch ID, amount, currency, recipient email, and timestamp

### 🔐 Authentication
- User registration and login with Flask-Login
- Password hashing
- Session management

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask |
| ORM | SQLAlchemy + Flask-Migrate |
| Database | SQLite |
| Auth | Flask-Login |
| Payments | PayPal REST API (sandbox) |
| Frontend | HTML, CSS (Jinja2 templates) |

---

## 📁 Project Structure

```
origin/
├── app.py              # App factory, routes, and main logic
├── models.py           # Database models (User, Teacher, Admin, Course, Schedule, Enrollment, PayoutHistory)
├── config.py           # Configuration (secret key, DB URI, PayPal credentials)
├── extensions.py       # Flask extensions (db, login_manager)
├── paypal.py           # PayPal API integration
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images
├── migrations/         # Flask-Migrate database migrations
└── instance/           # SQLite database file (gitignored)
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Herman-GIT-1/origin.git
cd origin
```

### 2. Install dependencies
```bash
pip install flask flask-sqlalchemy flask-migrate flask-login
```

### 3. Configure PayPal (optional)
In `config.py`, set your PayPal sandbox credentials:
```python
PAYPAL_CLIENT_ID = "your_sandbox_client_id"
PAYPAL_CLIENT_SECRET = "your_sandbox_secret"
```

### 4. Initialize the database
```bash
flask db upgrade
```

### 5. Run the application
```bash
python app.py
```

Open your browser at `http://127.0.0.1:5000`

---

## 🗄 Database Models

```
BaseUser (abstract)
├── User        — students: major, semester, enrolled courses
├── Teacher     — subjects, office, consultation hours, courses
└── Admin       — platform administration

Course          — code, name, teacher, students (M2M via Enrollment)
Enrollment      — links User ↔ Course, stores grade
Schedule        — course date/time slots (cascade delete)
PayoutHistory   — PayPal payout records per user
```

---

## 📝 Notes

- PayPal integration uses **sandbox mode only** — no real transactions
- Database migrations handled via Flask-Migrate
- Project built as part of first-year coursework at WIT Akademy, Warsaw

---

## 👤 Authors

**Herman Polianskyi**
[LinkedIn](https://www.linkedin.com/in/herman-polianskyi-8843bb386) · [GitHub](https://github.com/Herman-GIT-1)

**Yehor Milkov**
[GitHub](https://github.com/Yehormef)

from extensions import db
import enum
from datetime import datetime
from flask_login import UserMixin

class BaseUser(UserMixin, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    account_type = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=True, unique=True)

class User(BaseUser):
    __tablename__ = 'user'
    major = db.Column(db.String(150), nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    enrolled_courses = db.relationship('Course', secondary='enrollment', back_populates='students')

class Teacher(BaseUser):
    __tablename__ = 'teacher'
    subjects = db.Column(db.String(200), nullable=False)
    office = db.Column(db.String(100), nullable=False)
    consultation_hours = db.Column(db.String(100), nullable=False)
    courses = db.relationship('Course', backref='teacher')

class Admin(BaseUser):
    __tablename__ = 'admin'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)
    grade = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),
    )

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    students = db.relationship('User', secondary='enrollment', back_populates='enrolled_courses')
    course_schedule = db.relationship('Schedule', back_populates='course', cascade="all, delete-orphan") 

class DaysOfWeek(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', name="fk_schedule_course"), nullable=False)
    day_of_week = db.Column(db.Enum(DaysOfWeek), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    course = db.relationship('Course', back_populates='course_schedule')


class PayoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    batch_id = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    sent_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
    user = db.relationship('User', backref='payouts')

    def __repr__(self):
        return f"<Payout {self.batch_id} - {self.amount} {self.currency}>"
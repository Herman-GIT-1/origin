from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required, current_user
from paypal import create_payout, get_payout_status
from datetime import datetime
from config import Config
from extensions import db, mail, login_manager
from flask_migrate import Migrate
from models import BaseUser, User, Teacher, Admin, Enrollment, Course, DaysOfWeek ,Schedule, PayoutHistory
import re

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'GGWPEZKATKA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  
mail.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if not user:
        user = Teacher.query.get(int(user_id))
    if not user:
        user = Admin.query.get(int(user_id))
    return user

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must log in to access this page.", "danger")
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

#Module №1


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['account_type']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first() or Teacher.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        if account_type == 'user':
            new_user = User(
                username=username,
                password=password,
                account_type='user',
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Student registration successful!', 'success')
            return redirect(url_for('login'))
        
        elif account_type == 'teacher':
            new_teacher = Teacher(
                username=username,
                password=password,
                account_type='teacher',
                first_name=first_name,
                last_name=last_name,
                email=email,
                subjects="",
                office="",
                consultation_hours="",
            )
            db.session.add(new_teacher)
            db.session.commit()
            flash('Teacher registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if not user:
            user = Teacher.query.filter_by(username=username).first()
        if not user:
            user = Admin.query.filter_by(username=username).first()
        
        if not user:
            message = 'User not found.'
        elif user.password != password:
            message = 'Incorrect password.'
        else:
            login_user(user)
            if user.account_type == 'admin':
                return redirect(url_for('admin_page'))
            elif user.account_type == 'teacher':
                return redirect(url_for('teacher_page'))
            else:
                return redirect(url_for('user_page'))

    return render_template('login.html', message=message)
            
        
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostanąl wylogowany.', 'success')
    return redirect(url_for('login'))

@app.route('/user_page')
@login_required
def user_page():
    return render_template('user_page.html')

@app.route('/teacher_page')
@login_required
def teacher_page(): 
    return render_template('teacher_page.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    if not current_user.is_authenticated:
        flash("You must be logged in to access this page.", "danger")
        return redirect(url_for('login'))

    teachers = Teacher.query.all()
    users = User.query.all()
    return render_template('admin_page.html', teachers=teachers, users=users)

#Module №2

@app.route('/admin_page/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        account_type = request.form['account_type']
        major = request.form.get('major')  
        semester = request.form.get('semester')  

        if User.query.filter_by(username=username).first():
            flash('A user with this username already exists.', 'danger')
            return redirect(url_for('admin_page'))

        new_user = User(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            account_type=account_type,
            major=major,
            semester=semester
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('admin_page'))

    return render_template('add_user.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.major = request.form.get('major')  
        user.semester = request.form.get('semester')  
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_page'))  
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin_page'))

#Module №3

@app.route('/admin_page/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        subjects = request.form['subjects']
        account_type = request.form['account_type']
        office = request.form.get('office')
        consultation_hours = request.form.get('consultation_hours')

        new_teacher = Teacher(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            subjects=subjects,
            account_type=account_type,
            office=office,
            consultation_hours=consultation_hours,
        )
        db.session.add(new_teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('admin_page'))
    return render_template('add_teacher.html')

@app.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
   
    teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == 'POST':
        teacher.username = request.form['username']
        teacher.first_name = request.form.get('first_name')
        teacher.last_name = request.form.get('last_name')
        teacher.subjects = request.form['subjects']
        teacher.office = request.form['office']
        teacher.consultation_hours = request.form['consultation_hours']

        db.session.commit()
        flash('Teacher data updated successfully!', 'success')
        return redirect(url_for('admin_page'))
    return render_template('edit_teacher.html', teacher=teacher)

@app.route('/delete_teacher/<int:teacher_id>')
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        flash('Teacher not found.', 'danger')
        return redirect(url_for('admin_page'))
    try:
        db.session.delete(teacher)
        db.session.commit()
        flash('Teacher deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {e}', 'danger')
    return redirect(url_for('admin_page'))
#Module №4

@app.route('/admin_page', methods=['GET', 'POST']) 
@login_required
def manage_courses():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        teacher_id = request.form['teacher_id']
        student_ids = request.form.getlist('students')
        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            flash("Course with this code already exists.", "warning")
        else:
            new_course = Course(name=name, code=code, teacher_id=teacher_id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')

        for student_id in student_ids:
            enrollment = Enrollment(user_id=student_id, course_id=new_course.id)
            db.session.add(enrollment)
        db.session.commit()

        return redirect(url_for('manage_courses'))

    teachers = Teacher.query.all()
    courses = Course.query.all()
    students = User.query.filter_by(account_type='user').all()
    return render_template('manage_courses.html', courses=courses, teachers=teachers, students=students)

@app.route('/admin_page/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        flash("Course not found!", "error")
        return redirect(url_for('manage_courses'))

    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        teacher_id = request.form.get('teacher_id')
        selected_students = request.form.getlist('students')

        if not name or not code or not teacher_id:
            flash("All fields are required!", "error")
            return redirect(url_for('edit_course', course_id=course.id))

        course.name = name
        course.code = code
        course.teacher_id = int(teacher_id)

        selected_students_set = set(map(int, selected_students))
        current_students_set = {s.id for s in course.students}  

        students_to_remove = current_students_set - selected_students_set
        for user_id in students_to_remove:
            user = User.query.get(user_id)
            if user:
                course.students.remove(user)

        students_to_add = selected_students_set - current_students_set
        for user_id in students_to_add:
            user = User.query.get(user_id)
            if user:
                course.students.append(user)

        try:
            db.session.commit()
            flash("Course updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "error")

        return redirect(url_for('manage_courses'))

    teachers = Teacher.query.all()
    students = User.query.all()

    return render_template("edit_course.html", course=course, teachers=teachers, students=students)





@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get(course_id)

    if not course:
        flash('Course not found!', 'error')
        return redirect(url_for('manage_courses'))

    Enrollment.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('manage_courses'))



@app.route('/teacher_page/teacher_courses', methods=['GET', 'POST'])
@login_required
def teacher_courses():
    if request.method == 'POST':
        course_id = request.form['course_id']
        user_id = request.form['user_id']
        grade = request.form['grade']

        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if not enrollment:
            enrollment = Enrollment(user_id=user_id, course_id=course_id, grade=grade)
            db.session.add(enrollment)
        else:
            enrollment.grade = grade

        db.session.commit()
        return redirect(url_for('teacher_courses'))
    
    if current_user.account_type == 'teacher':
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
    else:
        courses = []
    
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    students = User.query.filter_by(account_type='user').all()
    return render_template('teacher_courses.html', courses=courses, students=students)

@app.route('/user_page/user_courses')
@login_required
def user_courses():
    courses = current_user.enrolled_courses
    return render_template('user_courses.html', courses=courses)

#Module №5

@app.route('/admin/course/<int:course_id>/schedule', methods=['GET', 'POST'])
@login_required
def edit_course_schedule(course_id):
    course = Course.query.get_or_404(course_id)
    schedule = Schedule.query.filter_by(course_id=course_id).first()

    if request.method == 'POST':
        try:
            new_day = request.form['day_of_week']
            start_time = datetime.strptime(request.form['start_time'], "%H:%M").time()
            end_time = datetime.strptime(request.form['end_time'], "%H:%M").time()

            if start_time >= end_time:
                flash('End time must be later than start time.', 'danger')
                return redirect(url_for('edit_course_schedule', course_id=course_id))

            existing_schedule = Schedule.query.filter_by(course_id=course_id, day_of_week=new_day).first()
            if existing_schedule and existing_schedule.id != schedule.id:
                flash('A schedule for this day already exists.', 'warning')
                return redirect(url_for('edit_course_schedule', course_id=course_id))

            if not schedule:
                schedule = Schedule(course_id=course_id, day_of_week=new_day, start_time=start_time, end_time=end_time)
                db.session.add(schedule)
            else:
                schedule.day_of_week = new_day
                schedule.start_time = start_time
                schedule.end_time = end_time

            db.session.commit()
            flash('Course schedule updated successfully!', 'success')
            return redirect(url_for('manage_courses'))
        
        except ValueError:
            flash('Invalid time format. Please enter a valid time.', 'danger')

    return render_template('edit_course_schedule.html', course=course)


#Module №7
@app.route('/payout', methods=['GET', 'POST'])
@login_required
def payout():
    if request.method == 'POST':
        email = request.form['email'].strip()
        amount = request.form['amount'].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address!", "danger")
            return redirect(url_for('payout'))

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Invalid amount! Please enter a positive number.", "danger")
            return redirect(url_for('payout'))

        try:
            payout_response = create_payout(email, amount)
            batch_id = payout_response.get("batch_header", {}).get("payout_batch_id")

            if not batch_id:
                raise Exception("Failed to get batch ID from PayPal response.")

            new_payout = PayoutHistory(
                user_id=current_user.id,
                batch_id=batch_id,
                amount=amount,
                currency="USD",
                recipient_email=email
            )
            db.session.add(new_payout)
            db.session.commit()
            
            flash(f"Payment successful! Batch ID: {batch_id}", "success")
        except Exception as e:
            flash(f"Payment error: {str(e)}", "danger")

    user_payouts = PayoutHistory.query.filter_by(user_id=current_user.id).all()
    
    return render_template('payout.html', payouts=user_payouts)

@app.route('/admin_payhistory')
@login_required
def admin_payhistory():
    payouts = PayoutHistory.query.order_by(PayoutHistory.sent_date.desc()).all()
    return render_template('admin_payhistory.html', payouts=payouts)
#Module 8

@app.route('/reports')
def reports():
    student_count = db.session.query(User).count()
    average_grades = db.session.query(User.id, User.first_name, db.func.avg(Enrollment.grade)).join(Enrollment).group_by(User.id).all()
    course_enrollment = db.session.query(Course.name, db.func.count(Enrollment.user_id)).join(Enrollment).group_by(Course.id).all()
    
    return render_template('reports.html', student_count=student_count, average_grades=average_grades, course_enrollment=course_enrollment)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
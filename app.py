from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required, current_user

app = Flask(__name__)
app.secret_key = 'GGWPEZKATKA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', secondary='enrollment', backref=db.backref('enrolled_students', lazy=True))
    email = db.Column(db.String(150), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)  
    last_name = db.Column(db.String(100), nullable=True)   
    major = db.Column(db.String(150), nullable=True)       
    semester = db.Column(db.Integer, nullable=True)       

class Teacher(UserMixin, db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    subjects = db.Column(db.String(200), nullable=False)
    office = db.Column(db.String(100), nullable=False)
    consultation_hours = db.Column(db.String(100), nullable=False)

class Admin(UserMixin, db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    account_type = db.Column(db.String(50), nullable=False)


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

#Modul №1


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_type = request.form['account_type']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

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

#Modul №2

@app.route('/add_user', methods=['GET', 'POST'])
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

#Modul №3

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        account_type = request.form['account_type']
        subjects = request.form['subjects']
        office = request.form.get['office']
        consultation_hours = request.form.get['consultation_hours']

        new_teacher = Teacher(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            account_type=account_type,
            subjects=subjects,
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
#Modul №4
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(50), nullable=True) 

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  
    code = db.Column(db.String(50), nullable=False, unique=True)  
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False) 
    students = db.relationship('User', secondary='enrollment')

@app.route('/admin_page', methods=['GET', 'POST'])
@login_required
def manage_courses():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        teacher_id = request.form['teacher_id']

        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            flash("Course with this code already exists.", "warning")
        else:
            new_course = Course(name=name, code=code, teacher_id=teacher_id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')

        return redirect(url_for('manage_courses'))

    teachers = Teacher.query.all()
    courses = Course.query.all()
    return render_template('manage_courses.html', courses=courses, teachers=teachers)

@app.route('/admin_page/<int:course_id>', methods=['POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get(course_id)
    if course:
        course.name = request.form['name']
        course.code = request.form['code']
        course.teacher_id = request.form['teacher_id']
        db.session.commit()
        flash('Course updated successfully!', 'success')
    else:
        flash('Course not found!', 'error')
    return redirect(url_for('manage_courses'))


@app.route('/admin_page/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get(course_id)
    if course:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    else:
        flash('Course not found!', 'error')
    return redirect(url_for('manage_courses'))



@app.route('/teacher_page', methods=['GET', 'POST'])
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
    
    courses = Course.query.filter_by(teacher_id=current_user.teacher.id).all()
    students = User.query.filter_by(account_type='user').all()
    return render_template('teacher_courses.html', courses=courses, students=students)



@app.route('/user_page')
@login_required
def user_courses():
    courses = current_user.courses
    return render_template('user_courses.html', courses=courses)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
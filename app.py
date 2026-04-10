from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

from flask_login import login_required


app = Flask(__name__)
app.config["SECRET_KEY"] = "1e5e9c2c016cd69636df46731d225320"  # SECRET KEY


# ---------------- DATABASE ----------------

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///job_portal.db'
db= SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50))  # employer / job_seeker

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))


# ---------------- ROUTES ----------------

from flask import session, redirect, url_for

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    jobs = Job.query.all()
    return render_template('home.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


from flask import flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid username or password", "danger")  # 👈 message

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'employer':
        return redirect(url_for('home'))

    if request.method == 'POST':
        print(request.form)
        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            salary=request.form['salary'],
            location=request.form['location'],
            company=request.form['company']
        )
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('post_job.html')


@app.route('/apply/<int:job_id>')
def apply(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    application = Application(
        user_id=session['user_id'],
        job_id=job_id
    )
    db.session.add(application)
    db.session.commit()

    return render_template('apply_job.html')  

@app.route('/search')
def search():
    query = request.args.get('q')

    jobs = Job.query.filter(
        (Job.title.ilike(f'%{query}%')) |
        (Job.location.ilike(f'%{query}%'))
    ).all()

    return render_template('home.html', jobs=jobs)


# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
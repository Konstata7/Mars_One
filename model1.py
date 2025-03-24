from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, redirect, render_template, request
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from data.forms import LoginForm, WorksForm, RegisterForm, DepartmentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def save_department(form, department=None):
    db_sess = db_session.create_session()
    flag = False
    if department is None:
        department = Department()
        flag = True
    department.title = form.title.data
    department.chief = form.chief.data
    department.members = form.members.data
    department.email = form.email.data
    if flag:
        db_sess.add(department)
    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def journal_works():
    db_session.global_init('db/db.sqlite')
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return render_template('index.html', jobs=jobs,
                           title='Журнал работ', message=request.args.get('message'),
                           message_type=request.args.get('message_type'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_job', methods=['GET', 'POST'])
def add_work():
    form = WorksForm(data={'team_leader': current_user.id})
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            creator=current_user.id,
            is_finished=form.is_finished.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('add_work.html', title='Добавление работы', form=form)


@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        if current_user.id == 1 or current_user.id == job.creator:
            form = WorksForm(data={'team_leader': job.team_leader, 'job': job.job, 'work_size': job.work_size,
                                   'collaborators': job.collaborators, 'is_finished': job.is_finished})
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                job.job = form.job.data
                job.team_leader = form.team_leader.data
                job.work_size = form.work_size.data
                job.collaborators = form.collaborators.data
                job.is_finished = form.is_finished.data
                db_sess.merge(job)
                db_sess.commit()
                return redirect('/?message=Работа сохранена&message_type=success')
            return render_template('add_work.html', title='Редактирование работы', form=form)
        return redirect("/?message=У вас нет доступа к редакции чужих работ"
                        "jobs!&message_type=danger")
    return redirect(f'/?message=Работа с id "{job_id}" не найдена&message_type=danger')


@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if job:
        if current_user.id == 1 or current_user.id == job.team_leader_id:
            db_sess.delete(job)
            db_sess.commit()
            return redirect('/?message=Работа удалена&message_type=success')
        return redirect('/?message=У вас нет доступа к удалению чужих работ'
                        'jobs!&message_type=danger')
    return redirect(f'/?message=Работа с id "{job_id}" не найдена&message_type=danger')


@app.route('/departments')
def departments():
    db_sess = db_session.create_session()
    return render_template('departments.html', title='Департаменты',
                           departments=db_sess.query(Department).all(),
                           message=request.args.get('message'),
                           message_type=request.args.get('message_type'))


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm(data={'chief': current_user.id})
    if form.validate_on_submit():
        save_department(form)
        return redirect('/departments?message=Департамент добавлен&message_type=success')
    return render_template('add_department.html', title='Добавление департамента', form=form)


@app.route('/edit_department/<int:dep_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dep_id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).get(dep_id)
    if department:
        if current_user.id == 1 or current_user.id == department.chief:
            form = DepartmentForm(data={'chief': department.chief, 'title': department.title,
                                        'members': department.members, 'email': department.email})
            if form.validate_on_submit():
                save_department(form, department)
                return redirect('/departments?message=Департамент сохранён&message_type=success')
            return render_template('add_department.html', title='Редактирование департамента', form=form)
        return redirect('/departments?message=У вас нет доступа к редакции чужих департаментов'
                        'departments!&message_type=danger')
    return redirect(f'/departments?message=Департамент с id "{dep_id}" не найден&message_type'
                    '=danger')


@app.route('/delete-department/<int:dep_id>')
@login_required
def delete_department(dep_id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).get(dep_id)
    if department:
        if current_user.id == 1 or current_user.id == department.chief:
            db_sess.delete(department)
            db_sess.commit()
            return redirect('/departments?message=Департамент сохранён&message_type=success')
        return redirect('/departments?message=У вас нет доступа к удалению чужих департаментов'
                        'departments!&message_type=danger')
    return redirect(f'/departments?message=Департамент с id "{dep_id}" не найден&message_type'
                    '=danger')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

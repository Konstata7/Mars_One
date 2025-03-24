from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class WorksForm(FlaskForm):
    team_leader = StringField('ID лидера', validators=[DataRequired()])
    job = StringField('Описание работы', validators=[DataRequired()])
    work_size = StringField('Размер работы', validators=[DataRequired()])
    collaborators = StringField("ID работников", validators=[DataRequired()])
    is_finished = BooleanField('Завершена?')
    submit = SubmitField('Подтвердить')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    age = IntegerField('Возраст пользователя', validators=[DataRequired()])
    position = StringField('Пост пользователя', validators=[DataRequired()])
    speciality = StringField('Специализация пользователя', validators=[DataRequired()])
    address = StringField('Адрес пользователя', validators=[DataRequired()])
    submit = SubmitField('Войти')


class DepartmentForm(FlaskForm):
    chief = IntegerField('ID главы', validators=[DataRequired()])
    title = StringField('Название департамента', validators=[DataRequired()])
    members = StringField('ID участников',
                          validators=[DataRequired()])
    email = EmailField('E-mail департамента', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

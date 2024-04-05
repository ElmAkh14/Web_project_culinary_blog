from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class UserRegisterForm(FlaskForm):
    email = EmailField('Логин/email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    speciality = StringField('Специальность', validators=[DataRequired()])
    address = StringField('Город проживания', validators=[DataRequired()])
    about = TextAreaField('О себе')
    submit = SubmitField('Submit')

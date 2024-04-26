from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, FieldList, IntegerField
from wtforms.validators import DataRequired


class RecipeForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    dish_image = FileField('Картинка')
    content = TextAreaField('Содержание', validators=[DataRequired()])
    is_private = BooleanField('Личное')
    submit = SubmitField('Применить')

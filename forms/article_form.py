from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FormField, FileField, IntegerField, FieldList
from wtforms.validators import DataRequired
from flask import url_for


class IngredientsForm(FlaskForm):
    ingredient_title = StringField('Название ингредиента')
    weight = IntegerField('Масса в граммах/количество в штуках ингредиента')


class ArticleForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    dish_image = FileField('Картинка')  #, default=url_for('static', filename='img/default_image.jpg')
    ingredients = FormField(IngredientsForm)
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')

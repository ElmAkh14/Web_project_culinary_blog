from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, FormField, Fieldlist, IntegerField
from wtforms.validators import DataRequired


class Ingredients(FlaskForm):
    ingredient_name = StringField('Название ингредиента', validators=[DataRequired()])
    ingredient_value = IntegerField('Количество', validators=[DataRequired()])

class RecipeForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    dish_image = FileField('Картинка')
    ingredients = Fieldlist(Ingredients)
    content = TextAreaField("Содержание", validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')

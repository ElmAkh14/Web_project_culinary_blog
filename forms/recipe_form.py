from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FormField, FileField, IntegerField, FieldList
from wtforms.validators import DataRequired


class IngredientsForm(FlaskForm):
    ingredient_title = StringField('Название ингредиента')
    weight = IntegerField('Масса в граммах/количество в штуках ингредиента')


class RecipeForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    dish_image = FileField('Картинка')
    ingredients = FieldList(FormField(IngredientsForm))
    content = TextAreaField("Содержание", validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')

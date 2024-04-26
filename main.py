import datetime
import sqlalchemy.orm
import os
from flask import Flask, request, render_template, redirect, session, make_response, abort, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user_register_form import UserRegisterForm
from forms.user_login_form import UserLoginForm
from forms.recipe_form import RecipeForm
from data.db_session import global_init, create_session
from data.user_model import User
from data.recipe_model import Recipe
from datetime import timedelta
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365 * 2)

db_file = 'db/culinary blog.sqlite'

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)

login_manager = LoginManager()
login_manager.init_app(app)


def img_to_bytes(img):
    print(img)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = create_session()
    recipes = db_sess.query(Recipe).filter(Recipe.is_private == 0)
    return render_template("index.html", title="Главная", recipes=recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            speciality=form.speciality.data,
            address=form.address.data,
            about=form.about.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile')
@login_required
def profile():
    db_sess = create_session()
    recipes = db_sess.query(Recipe).filter(Recipe.user == current_user)
    return render_template('profile.html', title=f"{current_user.name} {current_user.surname}", recipes=recipes)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        db_sess = create_session()
        recipe = Recipe()
        recipe.title = form.title.data
        if request.files.get('dish_image'):
            with open(f'static/users_img/{len(os.listdir("static/users_img")) + 1}.jpeg', 'wb') as file:
                file.write(request.files.get('dish_image').read())
            recipe.dish_image = f'{len(os.listdir("static/users_img"))}.jpeg'
        recipe.content = form.content.data
        recipe.is_private = form.is_private.data
        recipe.user_id = current_user.id
        db_sess.add(recipe)
        db_sess.commit()
        return redirect('/')
    return render_template('recipe_form.html', title='Добавление статьи',
                           form=form)


@app.route('/edit_recipe/<int:_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(_id: int):
    form = RecipeForm()
    if request.method == "GET":
        db_sess = create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == _id, Recipe.user == current_user).first()
        if recipe:
            form.title.data = recipe.title
            form.dish_image.data = recipe.dish_image
            form.content.data = recipe.content
            form.is_private.data = recipe.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == _id, Recipe.user == current_user).first()
        if recipe:
            recipe.title = form.title.data
            recipe.content = form.content.data
            recipe.created_date = datetime.datetime.now().strftime("%B %d, %Y")
            recipe.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('recipe_form.html',
                           title='Редактирование статьи',
                           form=form
                           )


@app.route('/delete_recipe/<int:_id>', methods=['GET', 'POST'])
@login_required
def delete_recipe(_id: int):
    db_sess = create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == _id, Recipe.user == current_user).first()
    if recipe:
        if recipe.dish_image:
            os.remove(f'static/users_img/{_id}.jpeg')
        db_sess.delete(recipe)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/recipe/<int:_id>')
def recipe(_id: int):
    db_sess = create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == _id).first()
    return render_template('recipe.html', recipe=recipe)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def abort_if_recipe_not_found(recipe_id):
    session_ = create_session()
    recipe_ = session_.query(Recipe).get(recipe_id)
    if not recipe_:
        abort(404, message=f"Recipe {recipe_id} not found")


class RecipeResource(Resource):
    def get(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session_ = create_session()
        recipe_ = session_.query(Recipe).get(recipe_id)
        return jsonify({'recipe': recipe_.to_dict(
            only=('title', 'dish_image', 'content', 'is_private', 'user_id'))})

    def delete(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session_ = create_session()
        recipe_ = session_.query(Recipe).get(recipe_id)
        session.delete(recipe_)
        session.commit()
        return jsonify({'success': 'OK'})


class RecipeListResource(Resource):
    def get(self):
        session = create_session()
        recipes = session.query(Recipe).all()
        return jsonify({'news': [recipe.to_dict(
            only=('title', 'content', 'user_id')) for recipe in recipes]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        recipe = Recipe(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(recipe)
        session.commit()
        return jsonify({'id': recipe.id})


api.add_resource(RecipeResource, '/api/recipe/<int:recipe_id>')

api.add_resource(RecipeListResource, '/api/recipes')

if __name__ == '__main__':
    global_init(db_file)
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
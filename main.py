import sqlalchemy.orm
from flask import Flask, request, render_template, redirect, session, make_response, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user_register_form import UserRegisterForm
from forms.user_login_form import UserLoginForm
from forms.article_form import ArticleForm
from data.db_session import global_init, create_session
from data.user_model import User
from data.article_model import Article
from constants import *
from datetime import timedelta
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365 * 2)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = create_session()
    articles = db_sess.query(Article)
    return render_template("index.html", title="Главная", articles=articles)


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
    return render_template('profile.html', title=f"{current_user.name} {current_user.surname}")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    form = ArticleForm()
    if form.validate_on_submit():
        db_sess = create_session()
        article = Article()
        article.title = form.title.data
        article.content = form.content.data
        article.is_private = form.is_private.data
        db_sess.add(article)
        db_sess.commit()
        print(form.ingredients.data)
        return redirect('/')
    return render_template('article_form.html', title='Добавление статьи',
                           form=form)


@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(_id: int):
    form = ArticleForm()
    if request.method == "GET":
        db_sess = create_session()
        article = db_sess.query(Article).filter((Article.id == _id),
                                                (Article.team_leader_object == current_user) |
                                                (current_user.id == 1)
                                                ).first()
        if article:
            form.title.data = article.title
            form.content.data = article.content
            form.is_private.data = article.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        article = db_sess.query(Article).filter(Article.id == _id,
                                                (Article.team_leader_object == current_user) |
                                                (current_user.id == 1)
                                                ).first()
        if article:
            article.title = form.title.data
            article.content = form.content.data
            article.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('article_form.html',
                           title='Редактирование статьи',
                           form=form
                           )


@app.route('/delete_article/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_article(_id: int):
    db_sess = create_session()
    job = db_sess.query(Article).filter(Article.id == _id,
                                        (Article.team_leader_object == current_user) |
                                        (current_user.id == 1)
                                        ).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/article')
def article():
    return render_template('article.html')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def abort_if_news_not_found(article_id):
    session_ = create_session()
    article_ = session_.query(Article).get(id)
    if not article_:
        abort(404, message=f"News {article_id} not found")


class ArticleResource(Resource):
    def get(self, article_id):
        abort_if_news_not_found(article_id)
        session_ = create_session()
        article_ = session_.query(Article).get(id)
        return jsonify({'article': article_.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, article_id):
        abort_if_news_not_found(article_id)
        session_ = create_session()
        article_ = session_.query(Article).get(article_id)
        session.delete(article_)
        session.commit()
        return jsonify({'success': 'OK'})


api.add_resource(ArticleResource, '/api/article/<int:article_id>')


if __name__ == '__main__':
    global_init(db_file)
    app.debug = True
    app.run(host='192.168.0.103')

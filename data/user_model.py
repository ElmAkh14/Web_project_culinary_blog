import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer,
                            nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String,
                                   nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    about = sqlalchemy.Column(sqlalchemy.Text,
                              nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              unique=True, index=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String,
                                        nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now())
    leader_job = orm.relationship("Article",
                                  back_populates='user')

    def __init__(self, **kwargs):
        super(User, self).__init__()
        self.surname = kwargs.get('surname', None)
        self.name = kwargs.get('name', None)
        self.age = kwargs.get('age', None)
        self.speciality = kwargs.get('speciality', None)
        self.address = kwargs.get('address', None)
        self.about = kwargs.get('about', None)
        self.email = kwargs.get('email', None)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

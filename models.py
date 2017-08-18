import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

db = SqliteDatabase('taco.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = db

    def get_tacos(self):
        return Taco.select().where(Taco.user == self)

    def get_stream(self):
        return Taco.select().where(
            (Taco.user == self)
        )

    @classmethod
    def create_user(cls, email, password):
        try:
            cls.create(
                email=email,
                password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError("User already exists")


class Taco(Model):
    protein = CharField()
    shell = CharField()
    cheese = BooleanField(default=True)
    extras = TextField()
    user = ForeignKeyField(
        rel_model=User,
        related_name='tacos'
    )

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([User, Taco], safe=True)
    db.close()

from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager

class Restaurant(db.Document):
    restaurant_name = db.StringField(required=True, min_length=1, max_length=20)
    price = db.IntField(required=True, min_value=1, max_value=4)
    location = db.StringField(required=True)
    type = db.StringField(required=True)
    restaurant_id = db.StringField(required=True)
    gmap = db.StringField(required=True)

    def get_id(self):
        return self.restaurant_id

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    favorites = db.ListField(db.ReferenceField(Restaurant))

    def get_id(self):
        return self.username

class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    restaurant = db.ReferenceField(Restaurant, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    stars = db.IntField(required=True, min_value=1, max_value=5)
    date = db.StringField(required=True)
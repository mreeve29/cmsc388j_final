from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, SearchForm
from ..models import User, Review

users = Blueprint("users", __name__)



@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: 
        return redirect(url_for("restaurants.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("restaurants.index"))
        else:
            flash("Invalid username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("restaurants.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()

    if username_form.validate_on_submit():
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
    )

@users.route("/account/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    favs = current_user.favorites
    if len(favs) == 0: favs = None
    return render_template(
        "favorites.html",
        restaurants=favs,
    )

@users.route("/users/search", methods=["GET", "POST"])
def user_search():
    search_form = SearchForm()

    if search_form.validate_on_submit():
        return redirect(url_for("users.user_query_results", query=search_form.search_query.data))

    return render_template("search.html", form=search_form, msg="Search For a User: ")


@users.route("/users/search/<query>", methods=["GET"])
def user_query_results(query):
    users = User.objects(username__iregex=query)
    n = len(users)
    reviews = []
    if n == 0:
        return render_template("user_query.html", users=None, query=query, n=n)
    else:
        for u in users:
            reviews.append(len(Review.objects(commenter=u)))
    

    return render_template("user_query.html", users=list(zip(users,reviews)), query=query, n=n)

@users.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    restaurants = user.favorites

    return render_template("user_detail.html", username=username, reviews=reviews, restaurants=restaurants)
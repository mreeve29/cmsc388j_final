from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from ..forms import RestaurantReviewForm, AddToFavoritesForm, RemoveFromFavoritesForm
from ..models import User, Review, Restaurant
from ..utils import current_time

from statistics import mean


restaurants = Blueprint("restaurants", __name__)


@restaurants.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", restaurants=Restaurant.objects())


#TODO: add searching
# @restaurants.route("/search/<query>", methods=["GET"])
# def search(query):


@restaurants.route("/restaurant/<id>", methods=["GET", "POST"])
def restaurant_detail(id):
    try:
        result = Restaurant.objects(restaurant_id=id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = RestaurantReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            stars=form.stars.data,
            date=current_time(),
            restaurant=result
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(restaurant=result)
    star_rating = None
    if len(reviews) > 0:
        star_rating = round(mean([x.stars for x in reviews]),1)


    fav_form = None
    if current_user.is_authenticated:
        favs = list(current_user.favorites)
        if result in favs:
            fav_form = RemoveFromFavoritesForm()
            if fav_form.validate_on_submit():
                favs.remove(result)
                current_user.modify(favorites=favs)
                current_user.save()
                return redirect(request.path)
        else:
            fav_form = AddToFavoritesForm()
            if fav_form.validate_on_submit():
                favs.append(result)
                current_user.modify(favorites=favs)
                current_user.save()
                return redirect(request.path)

    return render_template(
        "restaurant_detail.html", 
        form=form, 
        restaurant=result, 
        reviews=reviews, 
        star_rating=star_rating, 
        fav_form=fav_form
    )

@restaurants.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    restaurants = user.favorites

    return render_template("user_detail.html", username=username, reviews=reviews, restaurants=restaurants)

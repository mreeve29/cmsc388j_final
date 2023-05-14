from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from ..forms import RestaurantReviewForm, AddToFavoritesForm, RemoveFromFavoritesForm, SearchForm
from ..models import User, Review, Restaurant
from ..utils import current_time

import plotly.graph_objects as go
import io

from statistics import mean


restaurants = Blueprint("restaurants", __name__)


@restaurants.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", restaurants=Restaurant.objects())

@restaurants.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")


@restaurants.route("/restaurant/search", methods=["GET", "POST"])
def restaurant_search():
    search_form = SearchForm()

    if search_form.validate_on_submit():
        print("hello")
        return redirect(url_for("restaurants.restaurant_query_results", query=search_form.search_query.data))

    return render_template("search.html", form=search_form, msg="Search For a Restaurant: ")


@restaurants.route("/restaurant/search/<query>", methods=["GET"])
def restaurant_query_results(query):
    result = Restaurant.objects(restaurant_name__iregex=query)
    n = len(result)

    return render_template("restaurant_query.html", restaurants=result, query=query, n=n)

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
        star_rating = round(mean([x.stars for x in reviews]), 1)


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


@restaurants.route("/data")
def plotly():
    rests = Restaurant.objects()
    reviews = Review.objects()
    users = User.objects()

    # charts:
    # 1. ratings by restaurant bar chart - done
    # 2. price per restaurant bar chart - done
    # 3. reviews by restaurant bar chart - done
    # 4. reviews by restaurant pie chart - done
    # 5. reviews by user (top 5) bar chart 
    

    r_names = [r.restaurant_name for r in rests]

    reviews_rest_bar_data = {k:[] for k in r_names}
    for r in reviews:
        r_name = r.restaurant.restaurant_name
        reviews_rest_bar_data[r_name].append(r)


    ## RATINGS BAR CHART
    ratings = [(r,round(mean([x.stars for x in y]), 1)) if len(y) >= 1 else (r,0) for r,y in reviews_rest_bar_data.items()]
    ratings.sort(key=lambda x: x[1], reverse=True)

    ratings_bar_fig = go.Figure(data=[go.Bar(x=list(map(lambda x: x[0],ratings)), y=list(map(lambda x: x[1],ratings)))])
    ratings_bar_fig.update_layout(title="Star Rating Per Restaurant")
    ratings_bar_f = io.StringIO()

    ratings_bar_fig.write_html(ratings_bar_f)

    ## PRICE BAR CHART
    prices_bar_fig = go.Figure(data=[go.Bar(x=list(reviews_rest_bar_data.keys()), y=[x.price for x in rests])])
    prices_bar_fig.update_layout(title="Price Per Restaurant")
    prices_bar_f = io.StringIO()

    prices_bar_fig.write_html(prices_bar_f)

    ## NUM OF REVIEWS BAR CHART
    num_of_reviews = [(r,len(n)) for r,n in reviews_rest_bar_data.items()]
    num_of_reviews_bar_fig = go.Figure(data=[go.Bar(x=list(map(lambda x: x[0], num_of_reviews)), y=list(map(lambda x: x[1], num_of_reviews)))])
    num_of_reviews_bar_fig.update_layout(title="Number of Reviews Per Restaurant - Bar Chart")
    num_of_reviews_bar_f = io.StringIO()

    num_of_reviews_bar_fig.write_html(num_of_reviews_bar_f)


    ## NUM OF REVIEWS PIE CHART
    
    num_of_reviews_pie_fig = go.Figure(data=[go.Pie(labels=list(map(lambda x: x[0], num_of_reviews)), values=list(map(lambda x: x[1], num_of_reviews)))])
    num_of_reviews_pie_fig.update_layout(title="Number of Reviews Per Restaurant - Pie Chart")
    num_of_reviews_pie_f = io.StringIO()

    num_of_reviews_pie_fig.write_html(num_of_reviews_pie_f)

    ## TOP USERS BAR CHART

    top_users = {k.username:0 for k in users}
    for r in reviews:
        uname = r.commenter.username
        top_users[uname] += 1

    top_users_items = list(top_users.items())
    top_users_items.sort(key=lambda x: x[1], reverse=True)
    if len(top_users_items) > 5:
        top_users_items = top_users_items[:4]

    users_num_of_reviews_bar_fig = go.Figure(data=[go.Bar(
        x=list(map(lambda x: x[0], top_users_items)), 
        y=list(map(lambda x: x[1], top_users_items)))])
    users_num_of_reviews_bar_fig.update_layout(title="Top Users by Number of Reviews")
    users_num_of_reviews_bar_f = io.StringIO()

    users_num_of_reviews_bar_fig.write_html(users_num_of_reviews_bar_f)

    return render_template(
        "plots.html", 
        ratings_bar = ratings_bar_f.getvalue(),
        price_bar = prices_bar_f.getvalue(),
        num_of_reviews_bar=num_of_reviews_bar_f.getvalue(),
        num_of_reviews_pie=num_of_reviews_pie_f.getvalue(),
        top_users_bar=users_num_of_reviews_bar_f.getvalue())

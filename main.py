from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

API_KEY = os.getenv("MOVIE_API_KEY")
API_ENDPOINT = os.getenv("MOVIE_API")
API_SEARCH_ENDPOINT = os.getenv("API_SEARCH_ENDPOINT")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie.db"
Bootstrap(app)
db = SQLAlchemy(app)


class Form(FlaskForm):
    rating = SelectField(label='your rating', choices=([(num,num) for num in list(range(0,11))]))
    review = StringField(label='your review', validators=[])
    submit = SubmitField(label='submit')

class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])


class Movie(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.String(250), unique=False, nullable=True)
    img_url = db.Column(db.String(250), unique=False, nullable=False)

# db.create_all()
# movie1 = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(movie1)
# db.session.commit()


@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by("rating").all()
    return render_template("index.html", movies=all_movies)

@app.route("/edit/<id>", methods=["POST", "GET"])
def edit(id):
    movie = Movie.query.get(id)
    form = Form()
    if request.method == "POST":
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("edit.html", id=id, movie=movie, form=form)

@app.route("/delete")
def delete():
    id = request.args.get("id")
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddForm()
    if request.method == "POST":
        add_title = str(form.title.data).replace(" ", "%20")
        # print(add_title)
        api_call = f"https://{API_SEARCH_ENDPOINT}?api_key={API_KEY}&query={add_title}"
        # print(api_call)
        response = requests.get(api_call)
        # print(response.status_code)
        response.raise_for_status()
        list = response.json()
        # print(list)
        if "results" in list.keys():
            list = list["results"]
        print(list)
        # return redirect(url_for("select", list_of_titles=list))
        return render_template("select.html", list_of_titles=list)
    else:
        return render_template("add.html", form=form)

@app.route("/movie/<id>")
def movie(id):
    response = requests.get(f"https://{API_ENDPOINT}{id}?api_key={API_KEY}")
    response.raise_for_status()
    print(response.status_code)
    movie_dict = response.json()
    print(movie_dict)
    movie_chosen = Movie(
        id=movie_dict["id"],
        title=movie_dict["original_title"],
        year=movie_dict["release_date"],
        description=movie_dict["overview"],
        rating=0,
        ranking=0,
        review=" ",
        img_url=f'https://image.tmdb.org/t/p/w500{movie_dict["backdrop_path"]}')
    print(movie_chosen)
    db.session.add(movie_chosen)
    db.session.commit()
    return redirect(url_for("edit", id=movie_dict['id']))


if __name__ == '__main__':
    app.run(debug=True)

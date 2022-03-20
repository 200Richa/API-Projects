from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = ''
API_READ_ACCESS_TOKEN = ''

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
Bootstrap(app)

##CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


# After adding the new_movie the code needs to be commented out/deleted.
# So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


class EditRatingForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g.6.8', validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    done = SubmitField(label="Done")


class AddMovieForm(FlaskForm):
    movie_title = StringField(label="Movie Name", validators=[DataRequired()])
    add_movie = SubmitField(label="Add Movie")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit/rating', methods=["GET", "POST"])
def edit_rating():
    edit_form = EditRatingForm()
    if edit_form.validate_on_submit():
        movie_id = int(request.args.get('id'))
        movie_selected = Movie.query.get(movie_id)
        movie_selected.rating = edit_form.rating.data
        movie_selected.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=edit_form)


@app.route('/delete')
def delete():
    movie_id = int(request.args.get('id'))
    movie_selected = Movie.query.get(movie_id)
    db.session.delete(movie_selected)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add/movie', methods=["GET", "POST"])
def add_movie():
    add_form = AddMovieForm()
    if add_form.validate_on_submit():
        movie_name = str(add_form.movie_title.data)
        response = requests.get(
            f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&page=1&include_adult=false&query={movie_name}')
        response.raise_for_status()
        response1 = response.json()
        response2 = response1['results']
        all_movies = []
        for movie in response2:
            new_movie = {"title": movie["original_title"],
                         "release_date": movie["release_date"],
                         "id": movie["id"]
                         }
            all_movies.append(new_movie)
        return render_template('select.html', movies=all_movies)
    return render_template('add.html', form=add_form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(movie_api_url)
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit_rating", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)

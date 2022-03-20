from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, select
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
# class Cafe(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), unique=True, nullable=False)
#     map_url = db.Column(db.String(500), nullable=False)
#     img_url = db.Column(db.String(500), nullable=False)
#     location = db.Column(db.String(250), nullable=False)
#     seats = db.Column(db.String(250), nullable=False)
#     has_toilet = db.Column(db.Boolean, nullable=False)
#     has_wifi = db.Column(db.Boolean, nullable=False)
#     has_sockets = db.Column(db.Boolean, nullable=False)
#     can_take_calls = db.Column(db.Boolean, nullable=False)
#     coffee_price = db.Column(db.String(250), nullable=True)


# Alternative way to create json

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def find_loc(self, loc):
        column = self.location


def to_bool(word):
    if word.title() == 'False':
        return False
    elif word.title() == 'True':
        return True
    else:
        return None



@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

# @app.route('/random')
# def get_cafe():
#     selected_cafe = Cafe.query.order_by(func.random()).limit(1).all()[0]
#     return jsonify(id=selected_cafe.id,
#                    name=selected_cafe.name,
#                    map_url=selected_cafe.map_url,
#                    img_url=selected_cafe.img_url,
#                    location=selected_cafe.location,
#                    seats=selected_cafe.seats,
#                    has_toilet=selected_cafe.has_toilet,
#                    has_wifi=selected_cafe.has_wifi,
#                    has_sockets=selected_cafe.has_sockets,
#                    can_take_calls=selected_cafe.can_take_calls,
#                    coffee_price=selected_cafe.coffee_price
#                    )


@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = list()
    for cafe in cafes:
        all_cafes.append(cafe.to_dict())
    return jsonify(cafe=all_cafes)


@app.route('/search', methods=["GET", "POST"])
def search():
    loc = request.args['loc']
    # To get first occurrence
    # cafe = Cafe.query.filter_by(location=loc).first()
    # return jsonify(cafe=cafe.to_dict())
    cafes = Cafe.query.filter_by(location=loc).all()
    if not cafes:
        err = {
            'error': {
                "Not Found": "Sorry we don't have cafes at this location"
            }
        }
        return jsonify(err)
    all_cafes = list()
    for cafe in cafes:
        all_cafes.append(cafe.to_dict())
    return jsonify(cafe=all_cafes)


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_new_cafe():
    if request.method == "POST":

        new_cafe = Cafe(
                        name=request.form['name'],
                        seats=request.form['seats'],
                        map_url=request.form['map_url'],
                        location=request.form['location'],
                        img_url=request.form['img_url'],
                        has_wifi=to_bool(request.form['has_wifi']),
                        has_toilet=to_bool(request.form['has_toilet']),
                        has_sockets=to_bool(request.form['has_sockets']),
                        coffee_price=to_bool(request.form['coffee_price']),
                        can_take_calls=to_bool(request.form['can_take_calls']),

        )
        db.session.add(new_cafe)
        db.session.commit()
        return f" Received request for {request.form['name']}"


# HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    if cafe is None:
        err = {
            'error': {
                "Not Found": "Sorry we don't have cafes at this location"
            }
        }
        return jsonify(err), 404

    cafe.coffee_price = float(request.args.get('new_price'))
    db.session.commit()
    success = {
        'Success': "Successfully Updated the price"
    }
    return jsonify(success)


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    api_key = request.args.get('api-key')
    if api_key != "TopSecretAPIKey":
        err = {
            'error': "Sorry, that's not allowed. Make sure you have the correct API Key"
        }
        return jsonify(err), 403
    if cafe is None:
        err = {
            'error': {
                "Not Found": "Sorry we don't have cafes at this location"
            }
        }
        return jsonify(err), 404
    db.session.delete(cafe)
    db.session.commit()
    success = {
        'Success': "Successfully Deleted The Cafe"
    }
    return jsonify(success)



if __name__ == '__main__':
    app.run(debug=True)

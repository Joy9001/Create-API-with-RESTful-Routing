import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    def db_instance_to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=['GET'])
def get_random_cafe():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe_data = random.choice(cafes)
    # random_cafe = {
    #     "name": random_cafe_data.name,
    #     "map_url": random_cafe_data.map_url,
    #     "img_url": random_cafe_data.img_url,
    #     "location": random_cafe_data.location,
    #     "amenities": {
    #         "has_sockets": random_cafe_data.has_sockets,
    #         "has_toilet": random_cafe_data.has_toilet,
    #         "has_wifi": random_cafe_data.has_wifi,
    #         "can_take_calls": random_cafe_data.can_take_calls
    #     },
    #     "seats": random_cafe_data.seats,
    #     "coffee_price": random_cafe_data.coffee_price
    # }

    random_cafe = random_cafe_data.db_instance_to_dict()
    return jsonify(random_cafe)


# HTTP GET - All the Cafes

@app.route("/all", methods=['GET'])
def get_all_cafes():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    all_cafes = {}

    for index, data in enumerate(cafes, start=1):
        all_cafes[f"{index}"] = (data.db_instance_to_dict())

    return jsonify(all_cafes)


# HTTP GET - Find a Cafe

@app.route("/search", methods=['GET'])
def get_cafe_by_location():
    loc = request.args.get("loc")

    cafes_data = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()

    if cafes_data:
        cafes = {}
        for index, data in enumerate(cafes_data, start=1):
            cafes[f"{index}"] = (data.db_instance_to_dict())

        return jsonify(cafes)
    else:
        return jsonify({
            "error": {
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        }), 404


# HTTP POST - A New Cafe ~ Test using POSTMAN

@app.route("/add", methods=['POST'])
def add_a_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route("/update-price", methods=['PATCH'])
def update_price():
    cafe_id = request.args.get("id")
    new_price = request.args.get("new_price")

    # cafe_to_update = db.get_or_404(Cafe, cafe_id)
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": f"Successfully updated the price of Cafe-{cafe_to_update.id}"})

    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record

@app.route("/report-close", methods=['DELETE'])
def close_cafe():
    cafe_id = request.args.get("cafe_id")
    api_key = request.args.get("api_key")

    if api_key == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(res={"Success": f"Successfully deleted the Cafe with ID-{cafe_id}"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(res={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)

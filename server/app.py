#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pizza_restaurants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route("/")
def home():
    return "Pizza Restaurants API"



# Routes


# Get all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    result = [
        {"id": r.id, "name": r.name, "address": r.address}
        for r in restaurants
    ]
    return jsonify(result), 200


# Get one restaurant by ID
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    result = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }
    return jsonify(result), 200


# Delete a restaurant
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)


# Get all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    result = [
        {"id": p.id, "name": p.name, "ingredients": p.ingredients}
        for p in pizzas
    ]
    return jsonify(result), 200


# Create a RestaurantPizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_rp = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(new_rp)
        db.session.commit()

        result = {
            "id": new_rp.id,
            "price": new_rp.price,
            "pizza_id": new_rp.pizza_id,
            "restaurant_id": new_rp.restaurant_id,
            "pizza": {
                "id": new_rp.pizza.id,
                "name": new_rp.pizza.name,
                "ingredients": new_rp.pizza.ingredients
            },
            "restaurant": {
                "id": new_rp.restaurant.id,
                "name": new_rp.restaurant.name,
                "address": new_rp.restaurant.address
            }
        }
        return jsonify(result), 201

    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


# Run app

if __name__ == "__main__":
    app.run(port=5555, debug=True)

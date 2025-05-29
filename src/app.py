"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Child, Parent
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route("/child", methods=["POST"])
def create_child():
    body = request.get_json()
    if not body:
        return jsonify({"error": "Request body is required"}), 400
    if "name" not in body or "parent_id" not in body:
        return jsonify({"error": "Name and parent_id are required"}), 400

    if not isinstance(body["name"], str) or not isinstance(body["parent_id"], int):
        return jsonify({"error": "Invalid data types"}), 400
    if len(body["name"]) < 3:
        return jsonify({"error": "Name must be at least 3 characters long"}), 400
    if body["parent_id"] <= 0:
        return jsonify({"error": "Parent ID must be a positive integer"}), 400
    # Here you would typically save the child to the database

    child = Child(name=body["name"], parent_id=body["parent_id"])
    db.session.add(child)
    try:
        parent = Parent.query.get(body["parent_id"])
        if not parent:
            return jsonify({"error": "Parent not found"}), 404
        child.parent = parent
        db.session.commit()
        return jsonify({
            "msg": "Child created successfully",
            "child": {
                "id": child.id,
                "name": child.name,
                "parent_id": child.parent_id
            }
        }), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error.args)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

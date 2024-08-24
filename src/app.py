
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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
def get_all_users():
    all_users = User.query.all()
    all_users_serialize = [user.serialize() for user in all_users]
    
    return jsonify(all_users_serialize), 200



@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404

    return jsonify(user.serialize()), 200

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()  
    if not body:
        return jsonify({"msg": "Body is required"}), 400

    email = body.get('email')
    password = body.get('password')
    is_active = body.get('is_active', True)

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    new_user = User(email=email, password=password, is_active=is_active)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201


@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404

    body = request.get_json()  
    if not body:
        return jsonify({"msg": "Body is required"}), 400

    if "email" in body:
        user.email = body["email"]
    if "password" in body:
        user.password = body["password"]
    if "is_active" in body:
        user.is_active = body["is_active"]

    db.session.commit()

    return jsonify(user.serialize()), 200


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted successfully"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

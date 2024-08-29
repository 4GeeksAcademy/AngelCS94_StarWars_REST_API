
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, FavoritePlanet, FavoritePeople
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


@app.route('/people', methods=['GET'])
def get_all_people():
    all_people = People.query.all()  
    all_people_serialize = [person.serialize() for person in all_people]  
    
    return jsonify(all_people_serialize), 200


@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = People.query.get(person_id)  
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404  
    return jsonify(person.serialize()), 200  

@app.route('/people', methods=['POST'])
def create_people():
    body = request.get_json()

    if not body:
        return jsonify({'msg': 'Missing request body'}), 400

    required_fields = ['name', 'birth_year', 'gender', 'height', 'hair_color']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing {field}'}), 400

    new_people = People(
        name=body['name'],
        birth_year=body['birth_year'],
        gender=body['gender'],
        height=body['height'],
        hair_color=body['hair_color']
    )

    try:
        db.session.add(new_people)
        db.session.commit()
        return jsonify(new_people.serialize()), 201  # Devuelve el objeto creado con código 201
    except Exception as e:
        return jsonify({'msg': 'Error creating People', 'error': str(e)}), 500
    
@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    person = People.query.get(person_id)
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404

    body = request.get_json()
    if not body:
        return jsonify({"msg": "Body is required"}), 400

    if "name" in body:
        person.name = body["name"]
    if "birth_year" in body:
        person.birth_year = body["birth_year"]
    if "gender" in body:
        person.gender = body["gender"]
    if "height" in body:
        person.height = body["height"]
    if "hair_color" in body:
        person.hair_color = body["hair_color"]

    db.session.commit()

    return jsonify(person.serialize()), 200

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    person = People.query.get(person_id)
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404

    db.session.delete(person)
    db.session.commit()

    return jsonify({"msg": "Person deleted successfully"}), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()  
    all_planets_serialize = [planet.serialize() for planet in all_planets]  
    
    return jsonify(all_planets_serialize), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)  
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404  

    return jsonify(planet.serialize()), 200  

@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()  
    if not body:
        return jsonify({"msg": "Body is required"}), 400  

    
    required_fields = ['name', 'climate', 'terrain', 'population']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing {field}'}), 400

    
    new_planet = Planet(
        name=body['name'],
        climate=body['climate'],
        terrain=body['terrain'],
        population=body['population']
    )

    
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201 

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)  
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404

    body = request.get_json()  
    if not body:
        return jsonify({"msg": "Body is required"}), 400

   
    if "name" in body:
        planet.name = body["name"]
    if "climate" in body:
        planet.climate = body["climate"]
    if "terrain" in body:
        planet.terrain = body["terrain"]
    if "population" in body:
        planet.population = body["population"]

    db.session.commit()  

    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)  
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404

    db.session.delete(planet)  
    db.session.commit()

    return jsonify({"msg": "Planet deleted successfully"}), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Suponiendo que el usuario actual tiene ID 1
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorites = {
        "planets": [favorite_planet.serialize() for favorite_planet in user.favorite_planets],
        "people": [favorite_person.serialize() for favorite_person in user.favorite_people]
    }

    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Suponiendo que el usuario actual tiene ID 1
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    # Verificar si el planeta ya está en favoritos
    if any(fav_planet.planet_id == planet_id for fav_planet in user.favorite_planets):
        return jsonify({"msg": "Planet is already in favorites"}), 400

    favorite_planet = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({"msg": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1  # Assuming the current user has ID 1
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404

    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    # Check if the person is already a favorite
    if any(fav_person.people_id == people_id for fav_person in user.favorite_people):
        return jsonify({"msg": "Person is already in favorites"}), 400

    favorite_person = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(favorite_person)
    db.session.commit()

    return jsonify({"msg": "Person added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = 1  # Assuming the current user has ID 1
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite_planet = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite_planet:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite_planet)
    db.session.commit()

    return jsonify({"msg": "Favorite planet removed successfully"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    user_id = 1  # Assuming the current user has ID 1
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite_person = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()

    if not favorite_person:
        return jsonify({"msg": "Favorite person not found"}), 404

    db.session.delete(favorite_person)
    db.session.commit()

    return jsonify({"msg": "Favorite person removed successfully"}), 200
 
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

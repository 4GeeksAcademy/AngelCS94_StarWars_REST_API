
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet
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
    all_people = People.query.all()  # Consulta todos los registros de la tabla People
    all_people_serialize = [person.serialize() for person in all_people]  # Serializa los datos
    
    return jsonify(all_people_serialize), 200


@app.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = People.query.get(person_id)  # Busca una persona por ID en la base de datos
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404  # Si no se encuentra, devuelve un error 404

    return jsonify(person.serialize()), 200  # Si se encuentra, devuelve la información de la persona en formato JSON con el código de estado 200

# [POST] Crear un nuevo registro de People
@app.route('/people', methods=['POST'])
def create_people():
    body = request.get_json()

    if not body:
        return jsonify({'msg': 'Missing request body'}), 400

    # Validar que los campos requeridos estén presentes
    required_fields = ['name', 'birth_year', 'gender', 'height', 'hair_color']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing {field}'}), 400

    # Crear un nuevo registro de People
    new_people = People(
        name=body['name'],
        birth_year=body['birth_year'],
        gender=body['gender'],
        height=body['height'],
        hair_color=body['hair_color']
    )

    try:
        # Guardar en la base de datos
        db.session.add(new_people)
        db.session.commit()
        return jsonify(new_people.serialize()), 201  # Devuelve el objeto creado con código 201
    except Exception as e:
        return jsonify({'msg': 'Error creating People', 'error': str(e)}), 500
    
@app.route('/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    # Buscar la persona por ID en la base de datos
    person = People.query.get(person_id)
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404

    # Obtener los datos del cuerpo de la solicitud
    body = request.get_json()
    if not body:
        return jsonify({"msg": "Body is required"}), 400

    # Actualizar los campos permitidos si están presentes en el cuerpo de la solicitud
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

    # Guardar los cambios en la base de datos
    db.session.commit()

    # Devolver la respuesta con los datos actualizados
    return jsonify(person.serialize()), 200

@app.route('/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    # Buscar la persona por ID en la base de datos
    person = People.query.get(person_id)
    if person is None:
        return jsonify({'msg': 'Person not found'}), 404

    # Eliminar la persona de la base de datos
    db.session.delete(person)
    db.session.commit()

    # Devolver una respuesta confirmando la eliminación
    return jsonify({"msg": "Person deleted successfully"}), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()  # Consulta todos los registros de la tabla Planet
    all_planets_serialize = [planet.serialize() for planet in all_planets]  # Serializa los datos
    
    return jsonify(all_planets_serialize), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)  # Busca un planeta por ID en la base de datos
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404  # Si no se encuentra, devuelve un error 404

    return jsonify(planet.serialize()), 200  # Devuelve la información del planeta en formato JSON con código 200

@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()  # Obtener los datos del cuerpo de la solicitud
    if not body:
        return jsonify({"msg": "Body is required"}), 400  # Verifica si el cuerpo de la solicitud está vacío

    # Validar que los campos requeridos estén presentes
    required_fields = ['name', 'climate', 'terrain', 'population']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing {field}'}), 400

    # Crear un nuevo registro de Planet
    new_planet = Planet(
        name=body['name'],
        climate=body['climate'],
        terrain=body['terrain'],
        population=body['population']
    )

    # Guardar en la base de datos
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201  # Devuelve el objeto creado con código 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)  # Busca un planeta por ID en la base de datos
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404

    body = request.get_json()  # Obtener los datos del cuerpo de la solicitud
    if not body:
        return jsonify({"msg": "Body is required"}), 400

    # Actualizar los campos permitidos si están presentes en el cuerpo de la solicitud
    if "name" in body:
        planet.name = body["name"]
    if "climate" in body:
        planet.climate = body["climate"]
    if "terrain" in body:
        planet.terrain = body["terrain"]
    if "population" in body:
        planet.population = body["population"]

    db.session.commit()  # Guardar los cambios en la base de datos

    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)  # Busca un planeta por ID en la base de datos
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404

    db.session.delete(planet)  # Eliminar el planeta de la base de datos
    db.session.commit()

    return jsonify({"msg": "Planet deleted successfully"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.errorhandler(500)
def handle_server_error(error):
    print(f"Error {error}")
    return jsonify("Something unespected ocurred, try again later.")

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def handle_hello():

    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = {
        "hello": "world",
        "family": members
    }
    return jsonify(response_body), 200

@app.route('/members/<int:id>', methods=['GET'])
def get_one_member(id):
    members = jackson_family.get_all_members()
    for index, member in enumerate(members):
        if id == member["id"]:
            return jsonify(jackson_family.get_member(index)), 200
    return jsonify("member not found"), 404


@app.route('/members', methods=['POST'])
def add_new_member():
    new_member = request.json
    new_member = {k.lower(): v for k, v in new_member.items()}
    required_keys = ("age", "first_name", "last_name", "lucky_numbers")
    allowed_last_name = ("jackson_family", "jackson family")
    for key in required_keys:
        if key not in new_member:
            return jsonify(f"The key {key} is obligatory"), 400
    if new_member["last_name"].lower() not in allowed_last_name:
        return jsonify("Only family accepted is Jackson family"), 400
    if not new_member["age"].isnumeric():
        return jsonify("age value should only contain numbers"), 400
    if int(new_member["age"]) <= 0:
        return jsonify("age value should be greater than 0"), 400
    lucky_numbers_list = new_member["lucky_numbers"].replace(" ", "").split(",")
    for number in lucky_numbers_list:
        if not str(number).isnumeric():
            return jsonify(f"lucky numbers shall only contain numbers separated by commas.")
    response_body = jackson_family.add_member(new_member)
    print("Incoming request with the following body", response_body)
    return jsonify(jackson_family.get_all_members()), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_specific_member(id):
    members = jackson_family.get_all_members()
    for index, member in enumerate(members):
        if id == member["id"]:
            jackson_family.delete_member(index)
            return jsonify(f"family: {jackson_family.get_all_members()}"), 200
    return jsonify("member not found"), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)

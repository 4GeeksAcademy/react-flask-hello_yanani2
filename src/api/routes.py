"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


# -------------------------------------------------------------------#


@api.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()

    if not body or not body.get("email") or not body.get("password"):
        return jsonify({"error": "Debes proporcionar email y password"}), 400

    if User.query.filter_by(email=body["email"]).first():
        return jsonify({"error": "El usuario ya existe"}), 400

    try:

        new_user = User(
            email=body["email"],
            password=body["password"]
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Usuario creado exitosamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@api.route('/token', methods=['POST'])
def create_token():

    body = request.get_json()

    if not body or not body.get("email") or not body.get("password"):
        return jsonify({"error": "Debes proporcionar email y password"}), 400

    user = User.query.filter_by(email=body["email"]).first()

    if not user or not user.check_password(body["password"]):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "user": user.serialize()
    }), 200


@api.route('/notes', methods=['GET'])
@jwt_required()
def get_user_notes():

    current_user_id = get_jwt_identity()

    notes = Note.query.filter_by(user_id=current_user_id).all()

    notes_serialized = [note.serialize() for note in notes]

    return jsonify(notes_serialized), 200


@api.route('/notes', methods=['POST'])
@jwt_required()
def create_note():

    current_user_id = get_jwt_identity()

    body = request.get_json()

    if not body or not body.get("title") or not body.get("content"):
        return jsonify({"error": "Debes proporcionar título y contenido"}), 400

    try:

        new_note = Note(
            title=body["title"],
            content=body["content"],
            user_id=current_user_id
        )

        if body.get("tags"):
            for tag_name in body["tags"]:

                tag = Tag.query.filter_by(name=tag_name).first()

                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)

                new_note.tags.append(tag)

        db.session.add(new_note)
        db.session.commit()

        return jsonify(new_note.serialize()), 201

    except Exception as e:

        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api.route('/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    current_user_id = get_jwt_identity()

    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

    if not note:
        return jsonify({"error": "Nota no encontrada"}), 404

    return jsonify(note.serialize()), 200


@api.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    current_user_id = get_jwt_identity()
    body = request.get_json()

    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

    if not note:
        return jsonify({"error": "Nota no encontrada"}), 404

    try:

        if body.get("title"):
            note.title = body["title"]
        if body.get("content"):
            note.content = body["content"]

        if body.get("tags") is not None:

            note.tags.clear()

            for tag_name in body["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                note.tags.append(tag)

        db.session.commit()

        return jsonify(note.serialize()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    current_user_id = get_jwt_identity()

    note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

    if not note:
        return jsonify({"error": "Nota no encontrada"}), 404

    try:

        db.session.delete(note)
        db.session.commit()

        return jsonify({"message": "Nota eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api.route('/tags', methods=['GET'])
@jwt_required()
def get_all_tags():

    tags = Tag.query.all()
    tags_serialized = [tag.serialize() for tag in tags]

    return jsonify(tags_serialized), 200


@api.route('/tags/<string:tag_name>/notes', methods=['GET'])
@jwt_required()
def get_notes_by_tag(tag_name):
    current_user_id = get_jwt_identity()

    tag = Tag.query.filter_by(name=tag_name).first()

    if not tag:
        return jsonify({"error": "Etiqueta no encontrada"}), 404

    user_notes_with_tag = [note.serialize()
                           for note in tag.notes if note.user_id == current_user_id]

    return jsonify(user_notes_with_tag), 200

import os
import requests

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta
from model import User, Music
from controller.MusicController import generate_image, describe_image


from musicxml_parser.scoreToPianoroll import scoreToPianoroll

from music21 import *
from music21 import *
from music21 import converter, repeat


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

if __debug__:
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
    print("30 days")
    
else:
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
    print("30 minutes")

app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')

    if not email or not name or not password:
        return jsonify({'message': 'Email and name, password are required'}), 400

    try:
        User.create_user(email=email, name=name, password=password)

    except:
        return jsonify({'message': 'Email already exists'}), 400

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.read_user(email=email)
    
    if not user:
        return jsonify({'message': 'Invalid username'}), 401
    
    if not user.check_password(password):
        return jsonify({'message': 'Invalid password'}), 401

    access_token = create_access_token(identity=user.name)
    refresh_token = create_refresh_token(identity=user.name)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    return jsonify(access_token=access_token)

@app.route('/describe-music', methods=['GET'])
@jwt_required()
def describe_music():
    current_user = get_jwt_identity()

    music_name = request.args.get('music_name')
    composer = request.args.get('composer')

    if not music_name or not composer:
        return jsonify({'message': 'music_name and composer is required'}), 400
    
    images = []

    result = generate_image(music_name=music_name + ' by ' + composer)

    for image in result.data:
        images.append(image.url)

    description = describe_image(music_name, images)

    return jsonify({'image': images}, {'description': description}), 200


@app.route('/get-music', methods=['GET'])
@jwt_required()
def get_music():
    current_user = get_jwt_identity()

    music_name = request.args.get('music_name')
    composer = request.args.get('composer')

    if not music_name and not composer:
        return jsonify({'message': 'music_name and composer is required'}), 400

    result = get_music(music_name=music_name, composer=composer)

    return jsonify({'image': result.data[0].url}), 200

@app.route('/link-file', methods=['PRIVATE'])
def link_file():
    music_name = request.args.get('music_name')
    composer = request.args.get('composer')
    file_name = request.args.get('file_name')

    if not music_name or not composer or not file_name:
        return jsonify({'message': 'music_name, composer, file_name is required'}), 400
    
    try:
        Music.create_music(music_name=music_name, composer=composer, file_name=file_name)

    except:
        return jsonify({'message': 'Music file is already linked'}), 400

    return jsonify({'message': 'Music file linked successfully'}), 200

@app.route('/read-music', methods=['GET'])
@jwt_required()
def read_music():
    current_user = get_jwt_identity()

    music_name = request.args.get('music_name')
    composer = request.args.get('composer')

    if not music_name or not composer:
        return jsonify({'message': 'music_name and composer is required'}), 400

    score_path = Music.read_music(music_name=music_name, composer=composer)

    print(score_path)

    score = converter.parse(score_path)

    for note in score.recurse().notes:
        if(type(note) is harmony.ChordSymbol):
            score.remove(note, recurse=True)

    mf = midi.translate.music21ObjectToMidiFile(score)
    stream = midi.translate.midiFileToStream(mf)   

    notes = stream.flat.notes

    result = []

    for note in notes:
        result.append([note.nameWithOctave, note.quarterLength])

    return jsonify({'result': result}), 200

if __name__ == '__main__':
    app.run()
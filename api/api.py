# flask imports
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy import false  # for public id
from werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps

# creates Flask object
app = Flask(__name__)
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = '123456789'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

# Database ORMs


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    text = db.Column(db.String(100))

# decorator for verifying the JWT


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query\
                .filter_by(public_id=data['public_id'])\
                .first()
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated

# User Database Route
# this route sends back list of users


@app.route('/', methods=['GET'])
def up():
    return jsonify({'ok': 'true'}), 200


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'username': user.username
        })

    return jsonify({'users': output})

# route for logging user in


@app.route('/login', methods=['POST'])
def login():
    # creates dictionary of form data
    auth = request.form

    if not auth or not auth.get('username') or not auth.get('password'):
        # returns 401 if any username or / and password is missing
        return jsonify({'ok': 'false', "error": "no username or password provided"}), 400

    user = User.query\
        .filter_by(username=auth.get('username'))\
        .first()

    if not user:
        # returns 401 if user does not exist
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 400

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return jsonify({'ok': 'true', 'token': token.decode('UTF-8')}), 200
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )

# signup route


@app.route('/signup', methods=['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.form

    # gets username and password
    username = data.get('username')
    password = data.get('password')

    # checking for existing user
    user = User.query\
        .filter_by(username=username)\
        .first()

    if user:
        return jsonify({'ok': 'false', "error": "user already exists"}), 400
    if not username or not password:
        return jsonify({'ok': 'false', "error": "no username or password provided"}), 400

        # database ORM object
    user = User(
        public_id=str(uuid.uuid4()),
        username=username,
        password=generate_password_hash(password)
    )
    # insert user
    db.session.add(user)
    db.session.commit()

    token = jwt.encode({
        'public_id': user.public_id,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, app.config['SECRET_KEY'])

    return jsonify({'ok': 'true', 'token': token.decode('UTF-8')})


@app.route('/suggestions', methods=['POST'])
@token_required
def suggestions(self):

    if 'text' not in request.form:
        return jsonify({'ok': 'false', "error": "no text provided"}), 400
    if request.form['text'] == '':
        return jsonify({'ok': 'false', "error": "no text provided"}), 400

    # database ORM object
    data = Data(
        username=self.username,
        text=request.form.get('text')
    )
    # insert user
    db.session.add(data)
    db.session.commit()

    return jsonify({'ok': 'true'}), 201


@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    # querying the database
    # for all the entries in it
    data = Data.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for d in data:
        # appending the user data json
        # to the response list
        output.append({
            'user': d.username,
            'text': d.text
        })

    return jsonify({'data': output})


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debugger shell
    # if you hit an error while running the server
    app.run(debug=True)

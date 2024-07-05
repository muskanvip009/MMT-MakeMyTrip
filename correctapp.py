from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import Config
from flask_oauthlib.client import OAuth,OAuthException
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_CLIENT_ID'],
    consumer_secret=app.config['GOOGLE_CLIENT_SECRET'],
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homepage')
def homepage():
    return render_template('abc.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if password != confirm_password:
        return "The passwords do not match"

    password_hash = generate_password_hash(password)
    connection = get_db_connection()
    
    with connection.cursor() as cursor:
        if cursor.execute('SELECT email FROM users WHERE email = %s', email) > 0:
            return redirect(url_for('index'))
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s)', (email, password_hash))
        connection.commit()
    connection.close()
    
    return redirect(url_for('homepage'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    connection = get_db_connection()
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
    
    connection.close()
    
    if user and check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity={'email': email})
        return jsonify(access_token=access_token)
    
    return jsonify({'msg': 'Invalid credentials'}), 401

@app.route('/login/google/authorized')
def google_authorized():
    response = google.authorized_response()
    
    if response is None or response.get('access_token') is None:
        # return redirect(url_for('index'))
        return "error found in login google"
    
    session['google_token'] = (response['access_token'], '')
    userinfo = google.get('userinfo')
    email = userinfo.data['email']
    connection = get_db_connection()
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if not user:
            cursor.execute('INSERT INTO users (email) VALUES (%s)', (email,))
            connection.commit()
    
    connection.close()
    access_token = create_access_token(identity={'email': email})
    return jsonify(access_token=access_token)

@app.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('google_authorized', _external=True))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except:
            pass

        # Check for Google token
        google_token = session.get('google_token')
        if google_token:
            try:
                userinfo = google.get('userinfo')
                if userinfo.data:
                    return f(*args, **kwargs)
            except OAuthException as e:
                return jsonify({'msg': 'Google token is invalid or expired'}), 401

        return jsonify({'msg': 'Token is missing or invalid'}), 401

    return decorated_function


@app.route('/protected', methods=['GET'])
@token_required
def protected():
    # current_user = get_jwt_identity()
    if get_jwt_identity():
        return jsonify(logged_in_as=get_jwt_identity()), 200
    else:
        userinfo = google.get('userinfo').data
        return jsonify(logged_in_as=userinfo['email']), 200
    




if __name__ == '__main__':
    app.run(debug=True)

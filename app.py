from flask import Flask, render_template, request, redirect, url_for, jsonify, session,flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_oauthlib.client import OAuth,OAuthException
from config.config import Config
from models.user_model import UserModel
import controllers.user_controller as user_controller
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homepage')
def homepage():
    return render_template('abc.html')

@app.route('/register', methods=['POST'])
def register():
    return user_controller.register()

@app.route('/login', methods=['POST'])
def login():
    return user_controller.login()

@app.route('/login/google/authorized')
def google_authorized():
    response = google.authorized_response()
    
    if response is None or response.get('access_token') is None:
        return "Error found in login google"
    
    session['google_token'] = (response['access_token'], '')
    userinfo = google.get('userinfo')
    email = userinfo.data['email']
    
    user = UserModel().get_user_by_email(email)
    if not user:
        UserModel().add_user(email, None)
    
    session['user_email'] = email
    session['user_id'] = UserModel().get_userid_by_email(email)
    
    user = UserModel().get_user_by_email(email)
    if not user:
        UserModel().add_user(email, None)
    
    # access_token = create_access_token(identity={'email': email})
    # return jsonify(access_token=access_token)
    return redirect(url_for ('flightpage'))

@app.route('/flightpage')
def flightpage():
    userinfo = google.get('userinfo') 
    email = userinfo.data['email']
    user = UserModel().get_user_by_email(email)

    return render_template('flights.html',user=user)


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
    
@app.route('/getFlights',methods=['POST','GET'])
def getFlights():
    flights=user_controller.getflights()[0]
    returnflights=user_controller.getflights()[1]
    trip_type = request.form['trip_type']
    return render_template('flight_results.html',departure_flights=flights,returnflights=returnflights, trip_type=trip_type)


@app.route('/user')
@token_required  
def user():
    email = session.get('user_email')
    user_id = session.get('user_id')
    
    if not email or not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    user = UserModel().get_user_by_email(email)       
    return render_template('user_details.html', user=user)


@app.route('/update_details',methods=['POST','GET'])
@token_required  
def update_details():
    user_id = session.get('user_id')    
    print(user_id)
    return user_controller.update_details(user_id['userid'])

@app.route('/update_page',methods=['POST','GET'])
def update_page():
    email = session.get('user_email') 
    user = UserModel().get_user_by_email(email)    
    
    return render_template('update.html',user=user)    
    
@app.route('/change_password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not authenticated'}), 401

    old_password = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    confirmpassword=request.form.get('confirmpassword')
    if(new_password!=confirmpassword):
        flash('Confirm and new password do not match', 'danger')
        
    email = session.get('user_email') 

    user = UserModel().get_user_by_email(email)   
    print(user) 

    
    if not user or not check_password_hash(user['password_hash'], old_password):
        flash('Old password is incorrect', 'danger')
        return "old password is incorrect"

    new_password_hash = generate_password_hash(new_password)
    user['password_hash'] = new_password_hash
    UserModel().updatepassword(new_password_hash,email)

    flash('Password updated successfully', 'success')
    return redirect(url_for('user')) 




if __name__ == '__main__':
    app.run(debug=True)    
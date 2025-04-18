from flask import request, redirect, url_for, jsonify, render_template,flash
from models.user_model import UserModel
from flask_jwt_extended import create_access_token

user_model = UserModel()

def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "The passwords do not match"

    if user_model.add_user(email, password):
        return redirect(url_for('homepage'))
    return redirect(url_for('index'))

def login():
    email = request.form['email']
    password = request.form['password']
    user = user_model.get_user_by_email(email)

    if user and (user['password_hash'], password):
        # access_token = create_access_token(identity={'email': email})
        # return jsonify(access_token=access_token)
        return redirect(url_for ('getFlights'))

    return jsonify({'msg': 'Invalid credentials'}), 401

def getflights():
    trip_type = request.form['trip_type']
    src = request.form['source']
    dest = request.form['destination']
    departure_date = request.form['departure_date']
    return_date = request.form.get('return_date')

    return user_model.getflight(trip_type,src,dest,departure_date,return_date)

def update_details(id):
    fn=request.form.get('firstname')
    ln=request.form.get('lastname')
    user_model.updatenames(fn,ln,id)
    return redirect(url_for('user'))

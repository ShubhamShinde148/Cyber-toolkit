from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from core.extensions import db, User
from firebase_admin import auth as firebase_auth
import uuid

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ui_bp.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password')
        
        # Check by email or username
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        
        if user and user.check_password(password):
            # Using Remember Me by default for V2
            login_user(user, remember=True)
            flash('Login successful! Welcome to the V2 Platform.', 'success')
            return redirect(url_for('ui_bp.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    # Reusing the existing template
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('ui_bp.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check existing
        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'error')
            return redirect(url_for('auth_bp.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth_bp.register'))

        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    """Authenticate a user via Google OAuth using Firebase ID token."""
    data = request.get_json(silent=True)
    if not data or not data.get('idToken'):
        return jsonify({'status': 'error', 'message': 'Missing ID token.'}), 400

    try:
        decoded_token = firebase_auth.verify_id_token(data['idToken'])
    except Exception as e:
        print(f"Firebase verification error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid or expired token.'}), 401

    email = decoded_token.get('email', '').strip().lower()
    name = decoded_token.get('name', email.split('@')[0])

    if not email:
        return jsonify({'status': 'error', 'message': 'No email in token.'}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user for first-time Google sign-in
        username = name.replace(' ', '_')[:32]
        
        # Ensure unique username
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"[:32]
            counter += 1

        user = User(username=username, email=email)
        # Give them a random unguessable password since they use OAuth
        user.set_password(str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()

    # Log the user in
    login_user(user, remember=True)
    return jsonify({'status': 'success'})

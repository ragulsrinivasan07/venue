from flask import Flask, render_template, request, redirect, url_for, session
import requests
from cryptography.fernet import Fernet

app = Flask(__name__)

# Generate a Fernet key and keep it secret
FERNET_KEY = Fernet.generate_key() # Do this once and store securely (e.g., in environment variables)
cipher = Fernet(FERNET_KEY)

# Set the Flask secret key (ensure it's kept secret)
app.config['SECRET_KEY'] = 'mysecretkey'  # Replace this with a strong, unique key


# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Call FastAPI Login API
        response = requests.post(f"{FASTAPI_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            try:
                response_data = response.json()  # Try to parse JSON
                token = response_data.get("access_token")
                # Encrypt the token
                encrypted_token = cipher.encrypt(token.encode())
                # Store token in Flask session (secure cookie)
                session['token'] = encrypted_token
                return redirect(url_for('dashboard'))  # Redirect to dashboard
            except ValueError:
                error_message = "Unexpected response format."
                return render_template('login.html', error=error_message)
        else:
            try:
                error_message = response.json().get('detail', 'Invalid credentials')
            except ValueError:
                error_message = "Error: Unable to decode the response."
            return render_template('login.html', error=error_message)
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    encrypted_token = session.get('token')
    if not encrypted_token:
        error_message = "Error: Unable to retain session."
        return redirect(url_for('login', error=error_message))

    try:
        token = cipher.decrypt(encrypted_token).decode()
    except Exception as e:
        error_message = "Token decryption failed. Please log in again."
        return redirect(url_for('login', error=error_message))

    if token:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{FASTAPI_URL}/venues", headers=headers)
        if response.status_code == 200:
            venues = response.json()
            return render_template('dashboard.html', venues=venues)
        else:
            return f"Error: Unable to fetch venues. Status code: {response.status_code}", 500
    else:
        return redirect(url_for('index'))

@app.route('/venue/<int:venue_id>')
def venue_details(venue_id):
    encrypted_token = session.get('token')
    
    if not encrypted_token:
        error_message = "Error: Unable to retain session."
        return redirect(url_for('login'), error=error_message)

    try:
        token = cipher.decrypt(encrypted_token).decode()  # Decrypt the token
    except Exception as e:
        return redirect(url_for('login'))  # Redirect if decryption fails
    
    if token:
        headers = {'Authorization': f'Bearer {token}'}  # Include token in Authorization header
        # Fetch venue details from FastAPI backend
        response = requests.get(f"{FASTAPI_URL}/venue/{venue_id}", headers=headers)
        if response.status_code == 200:
            venue = response.json()
            return render_template('venue_details.html', venue=venue)
        else:
            return "Venue not found", 404
    else:
        return redirect(url_for('index'))  # Redirect if token is not found (user not logged in)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Call FastAPI Signup API
        response = requests.post(f"{FASTAPI_URL}/signup", json={"username": username, "password": password})
        
        if response.status_code == 200:
            return redirect(url_for('login'))
        else:
            error_message = response.json().get('detail', 'Signup failed')
            return render_template('signup.html', error=error_message)
    
    return render_template('signup.html')

@app.route('/profile')
def profile():
    # Simulating user data from the database (this should be dynamically fetched)
    user_data = {
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'joined': '2023-05-01',
        'profile_picture': 'profile.jpg'
    }
    return render_template('profile.html', user=user_data)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, redirect, send_from_directory, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from data.database_postgres import get_id
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Important for sessions

# Serve static files from web_files directory
@app.route('/web_files/<path:filename>')
def serve_static(filename):
    return send_from_directory('web_files', filename)
@app.route('/')
def index():
    return redirect('/web_files/login.html')
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    
    if not name or not password:
        return jsonify({'success': False, 'message': 'Name and password are required'}), 400
    
    user_id = get_id(name, password)
    
    if user_id:
        session['user_id'] = user_id  # Store user ID in session
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': user_id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid name or password'
        }), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/web_files/login.html')

if __name__ == "__main__":
    # Create web_files directory if it doesn't exist
    app.run(host="0.0.0.0", port=5000, debug=True)
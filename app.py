# library includes #################################################################################################################################
from flask import Flask, request, redirect, send_from_directory, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from tempfile import NamedTemporaryFile
# header includes  #################################################################################################################################
from data.database_postgres import get_id, user_registration
from temp.audio import transcribe_audio as transcript
from chatbots.diet import get_image_description
from chatbots.reasoning import respond


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
        return jsonify({ 'success': False, 'message': 'Invalid name or password' }), 401
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        # Validate required fields
        required_fields = {
            'name': 'Full name is required',
            'password': 'Password is required',
            'age': 'Age is required',
            'gender': 'Gender is required',
            'height': 'Height is required',
            'weight': 'Weight is required',
            'time_availability': 'At least one workout time is required'
        }
        missing_fields = []
        for field, message in required_fields.items():
            if not data.get(field):
                missing_fields.append(message)
        if missing_fields:
            return jsonify({
                'success': False,
                'message': 'Missing required fields',
                'errors': missing_fields
            }), 400
        # Additional validation for numeric fields
        try:
            age = float(data['age'])
            height = float(data['height'])
            weight = float(data['weight'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Age, height, and weight must be numbers'
            }), 400
        # Validate at least one workout time is selected
        if not data['time_availability'] or len(data['time_availability']) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one workout time is required'
            }), 400
        # Convert time availability to the format expected by user_registration
        time_available = []
        for slot in data['time_availability']:
            time_available.append(slot['start'])  # Just use the start time
        # Call the registration function
        user_id = user_registration(
            name=data['name'],
            Age=age,
            gender=data['gender'],
            height_m=height,
            Weight_kg=weight,
            fitness_goal=data.get('fitness_goal', "Get into better shape"),
            dietary_pref=data.get('diet_pref', "any"),
            time_available=time_available,
            mental_health_notes=data.get('mental_health'),
            medical_conditions=data.get('medical_conditions'),
            time_deadline=int(data.get('goal_deadline', 90)),
            password=data['password']
        )
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': user_id
        })
    except Exception as e:
        print("Registration error:", str(e))
        # Registration error: {str(e)}
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}',
            'error': str(e)
        }), 500
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/web_files/login.html')
@app.route('/api/transcribe', methods=['POST'])
def handle_transcription():
    """
    Accepts multipart/form-data with field 'audio' (16kHz mono WAV preferred).
    Saves to temp/, does a quick RIFF check, calls your transcriber, returns JSON.
    """
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, 'temp_audio1.wav')
    try:
        audio_file.save(temp_path)
        # Minimal WAV sanity check (RIFF header)
        with open(temp_path, 'rb') as f:
            if f.read(4) != b'RIFF':
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                return jsonify({'success': False, 'error': 'Invalid WAV file format'}), 400
        # Call your transcription function if available
        result_text = transcript()
        try:
            os.remove('temp_audio1.wav')
        except Exception:
            pass
        return jsonify({'success': True, 'transcription': result_text})
    except Exception as e:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
        return jsonify({'success': False, 'error': f'Transcription failed: {str(e)}'}), 500
# ---------- New: upload mp3 (save as temp_audio.mp3 + transcribe; return text) ----------
@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    ext = (f.filename.rsplit('.', 1)[-1] if '.' in f.filename else '').lower()
    if ext != 'mp3':
        return jsonify({'success': False, 'error': 'Only .mp3 files are allowed'}), 400
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    save_path = os.path.join(temp_dir, 'temp_audio.mp3')
    try:
        f.save(save_path)

        result_text = transcript(mp3_or_not=False)
        return jsonify({'success': True, 'saved_path': 'temp/temp_audio.mp3', 'transcription': result_text})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Audio save failed: {str(e)}'}), 500
# ---------- Upload image (save as download.<ext> + call get_image_description) ----------
@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """
    Expects multipart/form-data with:
      - file: image (.png/.jpg/.jpeg/.ico)
      - prompt: optional text prompt
    Uses session['user_id'] (or form user_id) to call get_image_description(image_path, prompt, user_id).
    Returns:
      {success: True, description: <markup>, ext: <ext>} OR {success: False, error: <msg>}
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 402
    f = request.files['file']
    if f.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    prompt = request.form.get('prompt', ' ')
    # Prefer session; fall back to optional form field
    user_id = session.get('user_id')
    if user_id is None:
        user_id = request.form.get('user_id', type=int)
    if user_id is None:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401

    ext = (f.filename.rsplit('.', 1)[-1] if '.' in f.filename else '').lower()
    if ext not in ('png', 'jpg', 'jpeg', 'ico'):
        return jsonify({'success': False, 'error': 'Unsupported image type'}), 403

    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    save_path_abs = os.path.join(temp_dir, f'download.{ext}')
    save_path_rel = f'temp/download.{ext}'

    try:
        f.save(save_path_abs)

        if get_image_description is None:
            return jsonify({'success': False, 'error': 'get_image_description not configured'}), 404

        try:
            result = get_image_description(save_path_rel, prompt, int(user_id))
        except TypeError:
            result = get_image_description(save_path_rel, prompt, int(user_id))

        if not isinstance(result, dict):
            return jsonify({'success': False, 'error': 'Invalid response from get_image_description'}), 405

        if result.get('status') == 'success':
            return jsonify({'success': True, 'description': result.get('description', ''), 'ext': ext})
        else:
            return jsonify({'success': False, 'error': result.get('message', 'Unknown error')}), 406

    except Exception as e:
        return jsonify({'success': False, 'error': f'Image processing failed: {str(e)}'}), 407
# ---------- NEW: text-only respond(prompt) returning markdown ----------
@app.route('/api/respond', methods=['POST'])
def api_respond():
    """
    Expects JSON: { "prompt": "<text>" }
    Calls respond(prompt) which returns markdown string.
    Returns { success: True, markdown: "<md>" } or { success: False, error: "<msg>" }.
    """
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON body required'}), 400
    data = request.get_json(silent=True) or {}
    prompt = (data.get('prompt') or '').strip()
    if respond is None:
        return jsonify({'success': False, 'error': 'respond function not configured'}), 500
    try:
        markdown = respond(prompt)
    except TypeError:
        # If the function signature is different, try positional
        markdown = respond(prompt)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    if not isinstance(markdown, str):
        return jsonify({'success': False, 'error': 'respond() did not return a string'}), 500
    return jsonify({'success': True, 'markdown': markdown})

from multiprocessing import Process
def return_and_call(result1):
    # # Start a new process
    # p = Process(target=function_name , args=(your_args,))
    # p.start()
    # Return immediately
    return result1
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
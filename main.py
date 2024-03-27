import os
import logging
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import argparse
from flask_socketio import SocketIO  # Import SocketIO
from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.core.audiobook_generator import AudiobookGenerator
from audiobook_generator.tts_providers.base_tts_provider import get_supported_tts_providers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)  # Initialize SocketIO with the Flask app

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'upload')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'epub'}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', tts_options=get_supported_tts_providers())

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

        args_dict = {
            "input_file": file_path,
            "output_folder": app.config['OUTPUT_FOLDER'],
            "tts": request.form.get('tts', 'openai'),
            "voice_name": request.form.get('voice_name', 'default_voice_name'),
            "log": request.form.get('log', 'INFO'),
            "preview": 'preview' in request.form,
            "no_prompt": 'no_prompt' in request.form,
            "language": request.form.get('language', 'en-US'),
            "newline_mode": request.form.get('newline_mode', 'double'),
            "chapter_start": int(request.form.get('chapter_start', 1)),
            "chapter_end": int(request.form.get('chapter_end', -1)),
            "output_text": 'output_text' in request.form,
            "remove_endnotes": 'remove_endnotes' in request.form,
            "output_format": request.form.get('output_format', ''),
            "model_name": request.form.get('model_name', ''),
            "voice_rate": request.form.get('voice_rate', ''),
            "voice_volume": request.form.get('voice_volume', ''),
            "voice_pitch": request.form.get('voice_pitch', ''),
            "proxy": request.form.get('proxy', ''),
            "break_duration": request.form.get('break_duration', '1250'),
        }

        args_namespace = argparse.Namespace(**args_dict)
        config = GeneralConfig(args_namespace)

        # Instead of directly running the generator, emit WebSocket events
        socketio.emit('log_message', {'data': 'Starting conversion...'})
        # Run the AudiobookGenerator in a background thread if needed

        AudiobookGenerator(config).run()

        socketio.emit('log_message', {'data': 'Conversion completed!'})

        return redirect(url_for('index'))

    return 'Invalid file type', 400

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
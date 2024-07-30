from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64
import os
from server.decision_agent import decide
from server.text_to_speech import text_to_speech, get_transcript

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        if not audio_base64:
            return jsonify({'status': 'error', 'message': 'No audio data provided'}), 400
        
        audio_data = base64.b64decode(audio_base64)
        save_dir = 'uploads'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        audio_path = os.path.join(save_dir, 'recorded_audio.wav')
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        return jsonify({'status': 'success', 'path': audio_path})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error uploading audio: {str(e)}'}), 500

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        audio_path = os.path.join('uploads', 'recorded_audio.wav')
        if not os.path.exists(audio_path):
            return jsonify({'status': 'error', 'message': 'Audio file not found'}), 404

        transcript_result = get_transcript(audio_path)
        if not transcript_result:
            return jsonify({'status': 'error', 'message': 'Failed to get transcript'}), 500

        try:
            alternatives = transcript_result['results']['channels'][0]['alternatives']
            if not alternatives:
                return jsonify({'status': 'error', 'message': 'No alternatives found in transcript result'}), 400
            
            transcript = alternatives[0]['transcript']
        except KeyError as e:
            return jsonify({'status': 'error', 'message': f'Missing key in transcript result: {e}'}), 400

        response_text = decide(transcript)
        response_audio_path = os.path.join('uploads', 'response_audio.wav')
        text_to_speech(response_text, response_audio_path)

        return jsonify({
            'status': 'success',
            'response': response_text,
            'audio': 'uploads/response_audio.wav'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing audio: {str(e)}'}), 500

@app.route('/uploads/response_audio.wav', methods=['GET'])
def get_response_audio():
    return send_from_directory('uploads', 'response_audio.wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64
import os
from server.decision_agent import decide
from server.text_to_speech import text_to_speech, get_transcript

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        data = request.get_json()
        audio_base64 = data['audio']
        audio_data = base64.b64decode(audio_base64)

        # Create directory if it does not exist
        save_dir = 'uploads'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        audio_path = os.path.join(save_dir, 'recorded_audio.wav')

        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        return jsonify({'status': 'success', 'path': audio_path})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        # Use the fixed file path directly
        audio_path = os.path.join('uploads', 'recorded_audio.wav')
        print(f"Audio path: {audio_path}")  # Debugging log

        # Check if audio path exists
        if not os.path.exists(audio_path):
            return jsonify({'status': 'error', 'message': 'Audio file not found'}), 400

        # Get transcript
        transcript_result = get_transcript(audio_path)
        print(f"Transcript result: {transcript_result}")  # Debugging log

        if transcript_result is None:
            return jsonify({'status': 'error', 'message': 'Failed to get transcript'}), 400

        # Validate transcript result structure
        try:
            alternatives = transcript_result['results']['channels'][0]['alternatives']
            if not alternatives:
                return jsonify({'status': 'error', 'message': 'No alternatives found in transcript result'}), 400
            
            transcript = alternatives[0]['transcript']
        except KeyError as e:
            return jsonify({'status': 'error', 'message': f'Missing key in transcript result: {e}'}), 400

        print(f"Transcript: {transcript}")  # Debugging log

        # Get response from decision agent
        response_text = decide(transcript)
        print(f"Response text: {response_text}")  # Debugging log

        # Generate TTS audio
        response_audio_path = os.path.join('uploads', 'response_audio.wav')
        text_to_speech(response_text, response_audio_path)

        return jsonify({
            'status': 'success',
            'response': response_text,
            'audio': response_audio_path
        })
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging log
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/uploads/response_audio.wav', methods=['GET'])
def get_response_audio():
    return send_from_directory('uploads', 'response_audio.wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

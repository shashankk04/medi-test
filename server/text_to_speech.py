from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
    SpeakOptions
)
import os
import asyncio
import time
import logging
from dotenv import load_dotenv
load_dotenv()

from server.play_audio import play_audio

DEEPGRAM_API_KEY=os.getenv("DEEPGRAM_API_KEY")
deepgram_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

def text_to_speech(text, output_file_path):
    try:
        options = SpeakOptions(
            model="aura-luna-en",  # Change voice if needed
            encoding="linear16",
            container="wav"
        )
        SPEAK_OPTIONS = {"text": text}
        start_time = time.time()
        deepgram_client.speak.v("1").save(output_file_path, SPEAK_OPTIONS, options)
        end_time = time.time()
        elapsed_time = int((end_time - start_time) * 1000)
        print(f"Latency to produce output.wav: ({elapsed_time}ms)")
        play_audio(output_file_path)
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")

def get_transcript(audio_file_path):
    try:
        # Read audio file
        with open(audio_file_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # Call the transcribe_file method with the text payload and options
        response = deepgram_client.listen.prerecorded.v("1").transcribe_file(payload, options)

        # Print the response (for debugging purposes)
        print(response.to_json(indent=4))

        # Return the response as a dictionary
        return response.to_dict()

    except Exception as e:
        print(f"Exception: {e}")
        return None
import os
import sys
import mimetypes
import requests
import base64
from datetime import datetime,timedelta

# Adjust this if your API is mounted under a prefix, e.g., /api/v1/transcribe
BASE_URL = "http://localhost:8000/"

def test_transcribe_endpoint(wav_file_path: str):
    """
    Test the /transcribe endpoint by sending raw audio bytes as hex string in JSON.
    """
    if not os.path.exists(wav_file_path):
        print(f"Error: File not found at {wav_file_path}")
        return

    # Read file bytes
    with open(wav_file_path, 'rb') as f:
        audio_bytes = f.read()

        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(wav_file_path)
    if not mime_type or not mime_type.startswith("audio/"):
        print(f"Warning: Could not detect audio MIME type for {wav_file_path}, using application/octet-stream")
        mime_type = "application/octet-stream"

    url = f"{BASE_URL}api/v1/transcribe/transcribe"
    print(f"Testing POST {url}")

    # The endpoint expects audio_content as bytes, but since it's JSON,
    # send it as a hex string (or base64) and decode in the API if needed.
    # Your code expects bytes, so sending hex string and converting back is necessary.
    # Adjust if you modify API to accept base64 or raw bytes differently.
    payload = {
        "audio_content": audio_b64,  # hex string representation of bytes
        
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Transcription success:")
            print(f"Transcript: {data['transcript']}")
            print(f"Confidence: {data['confidence']}")
        else:
            print(f"Failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception during test_transcribe_endpoint: {e}")

def test_upload_endpoint(wav_file_path: str):
    """
    Test the /test-upload endpoint by uploading the audio file as multipart/form-data.
    """
    if not os.path.exists(wav_file_path):
        print(f"Error: File not found at {wav_file_path}")
        return

    url = f"{BASE_URL}api/v1/transcribe/test-upload"
    print(f"Testing POST {url}")

    try:
        with open(wav_file_path, 'rb') as f:
            files = {"file": (os.path.basename(wav_file_path), f, "audio/wav")}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            data = response.json()
            print("Upload & transcription success:")
            print(f"Transcript: {data['transcript']}")
            print(f"Confidence: {data['confidence']}")
        else:
            print(f"Failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception during test_upload_endpoint: {e}")

def check_server():
    """
    Check if server is up by hitting /docs or root.
    """
    try:
        resp = requests.get(f"{BASE_URL}docs")
        if resp.status_code == 200:
            print("Server is running!")
            return True
        else:
            print(f"Server returned status {resp.status_code}")
            return False
    except requests.ConnectionError:
        print("Could not connect to server. Is it running at localhost:8000?")
        return False

if __name__ == "__main__":
    if not check_server():
        sys.exit(1)

    wav_file = "audio_files/output.wav"  # Adjust your test WAV path here
    start_time = datetime.now()
    print("\n--- Testing /transcribe endpoint ---")
    test_transcribe_endpoint(wav_file)
    end_time = datetime.now()
    print('Time Taken', (end_time-start_time).total_seconds())
    print("\n--- Testing /test-upload endpoint ---")
    test_upload_endpoint(wav_file)
    print('Time Taken', (datetime.now() - end_time).total_seconds())
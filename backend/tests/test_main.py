import sys
import os
from fastapi.testclient import TestClient
# Add the backend directory to the Python path, before make importations
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

client = TestClient(app)


def test_speech_to_text():
    """
    Test the /speech-to-text/ endpoint with a sample audio file.
    """
    audio_path = os.path.abspath("backend/audio/sample.wav")  # Ensure absolute path

    assert os.path.exists(audio_path), f"❌ ERROR: File not found at {audio_path}"

    with open(audio_path, "rb") as audio:
        files = {"audio_file": audio}
        response = client.post("/speech-to-text/", files=files)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "transcript" in response.json()


def test_text_to_speech():
    """
    Test the /text-to-speech/ endpoint with a valid JSON payload.
    """
    payload = {"text": "Hola, ¿cómo estás?", "lang": "es"}
    response = client.post("/text-to-speech/", json=payload)  # Use json=payload
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["content-type"] == "audio/mpeg"

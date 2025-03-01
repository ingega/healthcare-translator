from fastapi import FastAPI, UploadFile, File, HTTPException
import openai
import speech_recognition as sr
from gtts import gTTS
import os
import uuid
from fastapi.responses import FileResponse
from pydub import AudioSegment
from googletrans import Translator
# load sensitive info by a secure way
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
app = FastAPI()

# Set your Open AI by env
openai.api_key = os.getenv("OPENAI_API_KEY")  # Get the API key securely

# Create a folder to store temporary audio files
TEMP_AUDIO_FOLDER = "audio/"
os.makedirs(TEMP_AUDIO_FOLDER, exist_ok=True)


@app.post("/speech-to-text/")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        file_ext = audio_file.filename.split(".")[-1].lower()
        temp_audio_path = os.path.join(TEMP_AUDIO_FOLDER, f"{uuid.uuid4()}.{file_ext}")

        with open(temp_audio_path, "wb") as buffer:
            buffer.write(audio_file.file.read())

        if file_ext == "mp3":
            wav_path = temp_audio_path.replace(".mp3", ".wav")
            audio = AudioSegment.from_mp3(temp_audio_path)
            audio.export(wav_path, format="wav")
            os.remove(temp_audio_path)
            temp_audio_path = wav_path

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        os.remove(temp_audio_path)

        return {"transcript": text}

    except Exception as e:
        print(f"❌ ERROR: {e}")  # Print the exact error in logs
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate/")
async def translate_text(text: str, target_lang: str = "es"):
    """ Translates a given text into the target language using Google Translate. """
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_lang)
        return {"translated_text": translated.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/text-to-speech/")
async def text_to_speech(text: str, lang: str = "es"):
    """
    Converts translated text into speech using Google Text-to-Speech (gTTS).
    """
    try:
        # Generate a unique filename for the speech output
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(TEMP_AUDIO_FOLDER, audio_filename)

        # Generate speech
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_path)

        return FileResponse(audio_path, media_type="audio/mp3", filename=audio_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


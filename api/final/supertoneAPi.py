import requests
import os
from dotenv import load_dotenv

load_dotenv()
SUPERTONE_API_KEY = os.getenv("SUPERTONE_API_KEY")

def generate_tts(text, output_path="output.wav", style = "Neutral", voice_id="c3c0898fd41489a8e8919c", model="sona_speech_1"):
    API_URL = f"https://supertoneapi.com/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "x-sup-api-key": SUPERTONE_API_KEY
    }

    payload = {
        "text": text,
        "language": "ko",
        "model": model,
        "style":style,
        "voice_settings": {
            "pitch_shift": 0,
            "pitch_variance": 1,
            "speed": 1
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print("음성 파일 저장 완료:", output_path)
        return output_path
    else:
        print("TTS 오류 발생:")
        print(response.status_code)
        print(response.text)
        return None
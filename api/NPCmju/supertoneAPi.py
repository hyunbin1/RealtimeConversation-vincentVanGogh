"""import requests
import time

# API 엔드포인트와 인증 키
#voice_id = "54CyP2zU9HCeLVCpzDRFPi"  # Yoonho의 예시 voice_id
#voice_id = "hpHAJFDjgSgJrMmgs95a93" #알퐁스
#voice_id = "eqmbPSKJ9x7x9P6tKWMP8c" #Dond
voice_id = "h4uJLnsdb32h2FUvYKB7qC" #cedric
API_URL = f"https://supertoneapi.com/v1/text-to-speech/{voice_id}"
API_KEY = "80c7d01d9cc84f9038eb033f5bd2d6a8"

# 요청 헤더
headers = {
    "Content-Type": "application/json",
    "x-sup-api-key": API_KEY
}

# 요청 데이터
payload = {
    "text": "안녕하세요. 수퍼톤 API 테스트입니다.",
    "language": "ko",
    "model": "turbo",
    "voice_settings": {
        "pitch_shift": 0,
        "pitch_variance": 1,
        "speed": 1
    }
}

start_time = time.time()

response = requests.post(API_URL, headers=headers, json=payload)

end_time = time.time()
elapsed_time = end_time - start_time

if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print(" 음성 파일 저장 완료: output.wav")
else:
    print(" 오류 발생:")
    print(response.status_code)
    print(response.text)

print(f"응답 시간: {elapsed_time:.2f}초")

"""

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
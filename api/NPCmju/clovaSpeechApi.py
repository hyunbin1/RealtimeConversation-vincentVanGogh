"""import requests

def clova_short_stt(file_path, secret_key):
    url = 'https://clovaspeech-gw.ncloud.com/recog/v1/stt?lang=Kor'

    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/json',
        'X-CLOVASPEECH-API-KEY': secret_key
    }

    with open(file_path, 'rb') as f:
        audio_data = f.read()

    response = requests.post(url, headers=headers, data=audio_data)

    try:
        result = response.json()
    except ValueError:
        print(" JSON 파싱 실패")
        print(response.text)
        return None
    
    print(result)
    print("")

    if response.status_code == 200 and 'text' in result:
        print("인식 결과:")
        print(result['text'])
        return result['text']
    else:
        print(" 오류 응답:")
        print(result)
        return None


if __name__ == '__main__':
    SECRET_KEY = '62e4c5ff21f34be1831c3b3fe35b4f17'
    #FILE_PATH = "C:/Users/sink0/Downloads/용오리님과 통화_1.wav"
    FILE_PATH = "C:/Users/sink0/Downloads/output6.wav" 

    clova_short_stt(FILE_PATH, SECRET_KEY)
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

def clova_short_stt(file_path: str) -> str | None:
    url = 'https://clovaspeech-gw.ncloud.com/recog/v1/stt?lang=Kor'
    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/json',
        'X-CLOVASPEECH-API-KEY': CLOVA_API_KEY
    }

    # ✅ 경로 및 키 확인
    print("CLOVA_API_KEY 설정됨:", CLOVA_API_KEY is not None)
    print("오디오 파일 존재:", os.path.exists(file_path))

    with open(file_path, 'rb') as f:
        audio_data = f.read()

    response = requests.post(url, headers=headers, data=audio_data)

    try:
        result = response.json()
    except ValueError:
        print("JSON 파싱 실패")
        print(response.text)
        return None

    # ✅ 응답 상태 확인
    print("📡 상태 코드:", response.status_code)
    print("📄 응답 내용:", result)

    if response.status_code == 200 and "text" in result:
        return result["text"]
    else:
        print("Clova 응답에 'text' 없음 또는 실패 상태")
        return None
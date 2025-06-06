import pyaudio
import threading
import requests
import io
import wave
import os
from dotenv import load_dotenv

load_dotenv()
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def convert_frames_to_wav_bytes(frames, format, channels, rate, audio):
    buffer = io.BytesIO()
    wf = wave.open(buffer, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return buffer.getvalue()

def clova_stt_from_bytes(audio_bytes: bytes):
    url = 'https://clovaspeech-gw.ncloud.com/recog/v1/stt?lang=Kor'
    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/json',
        'X-CLOVASPEECH-API-KEY': CLOVA_API_KEY
    }
    response = requests.post(url, headers=headers, data=audio_bytes)
    print("상태 코드:", response.status_code)
    print("응답 내용:", response.text)
    try:
        result = response.json()
        return result.get("text")
    except ValueError:
        print("JSON 파싱 실패")
        return None

def record_and_get_text():
    global recording
    recording = True
    frames = []

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)

    print("녹음 시작 (엔터로 종료)")

    def record():
        while recording:
            data = stream.read(CHUNK)
            frames.append(data)

    t = threading.Thread(target=record)
    t.start()
    input("▶ Enter 키를 누르면 녹음 종료\n")
    recording = False
    t.join()

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_bytes = convert_frames_to_wav_bytes(frames, FORMAT, CHANNELS, RATE, audio)
    print("STT 요청 중...")
    text = clova_stt_from_bytes(audio_bytes)
    if text:
        print("인식된 텍스트:", text)
    else:
        print("STT 실패")
    return text  # 반드시 결과를 반환해야 메인 파이프라인에서 활용 가능



# supertoen API를 사용하여 STT를 수행하고, 세그먼트 정보를 반환하는 함수 ( 자막용 )
def clova_stt_with_segments(audio_path: str):
    url = "https://clovaspeech-gw.ncloud.com/recog/v1/stt?lang=Kor&sttEnable=true&callback="

    headers = {
        'Content-Type': 'application/octet-stream',
        'Accept': 'application/json',
        'X-CLOVASPEECH-API-KEY': CLOVA_API_KEY
    }

    with open(audio_path, 'rb') as f:
        response = requests.post(url, headers=headers, data=f.read())

    if response.status_code != 200:
        return {"error": "Clova 요청 실패", "status": response.status_code, "message": response.text}

    try:
        result = response.json()
        # Clova의 'segments'는 start/end 포함됨
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": round(seg.get("start"), 2),
                "end": round(seg.get("end"), 2),
                "text": seg.get("text")
            })
        return segments
    except Exception as e:
        return {"error": "JSON 파싱 실패", "exception": str(e)}




#  모듈로 import될 경우 실행되지 않음
if __name__ == "__main__":
    record_and_get_text()

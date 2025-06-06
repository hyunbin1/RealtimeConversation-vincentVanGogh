import wave

# wav 파일 열기
with wave.open("van_gogh_reply.wav", "rb") as wf:
    print("채널 수:", wf.getnchannels())            # Mono=1, Stereo=2
    print("샘플레이트:", wf.getframerate())         # 예: 16000, 24000, 48000
    print("샘플 너비 (bit):", wf.getsampwidth() * 8) # 예: 16bit, 24bit
    print("총 프레임 수:", wf.getnframes())
    print("재생 시간 (초):", wf.getnframes() / wf.getframerate())
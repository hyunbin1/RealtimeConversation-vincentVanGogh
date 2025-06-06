from supertoneAPi import generate_tts
from rag import chunk_text, build_faiss, retrieve_top_k, save_faiss_index, load_faiss_index
from gpt import generate_answer, save_answer
from audioAndSTT import record_and_get_text
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import os
from g2pk import G2p
import wave


app = FastAPI()
g2p = G2p()

TXT_PATH = "answer.txt"
OUTPUT_WAV_PATH = "van_gogh_reply.wav"

# 한국어 → 영어 음소 변환 매핑
korean_to_eng_phoneme = {
    "아": "a", "야": "ya", "어": "eo", "여": "yeo",
    "오": "o", "요": "yo", "우": "u", "유": "yu",
    "으": "eu", "이": "i", "에": "e", "애": "ae",
    "바": "b", "파": "p", "마": "m",
    "다": "d", "타": "t", "나": "n",
    "라": "l", "사": "s", "자": "j", "차": "ch", "샤": "sh",
    "하": "h", "가": "g", "카": "k", "앙": "ng",
    "와": "w", "야": "y"
}

# 영어 음소 → viseme ID 매핑
phoneme_to_viseme = {
    "a": 1, "ae": 1, "ya": 1, "yae": 1,
    "eo": 2, "e": 2, "yeo": 2, "ye": 2,
    "o": 3, "yo": 3,
    "u": 4, "yu": 4,
    "i": 5, "ee": 5,
    "we": 6, "wi": 6, "wo": 6,
    "m": 7, "b": 7, "p": 7,
    "n": 8, "d": 8, "t": 8, "l": 8,
    "s": 9, "sh": 9, "z": 9, "ch": 9, "j": 9,
    "h": 10,
    "g": 11, "k": 11, "ng": 11,
    "r": 12, "w": 13, "y": 13,
    "_": 0,
}


def get_duration(wav_path):
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def run_pipeline():
    text_path = "반고흐_편지_원문.txt"
    index_path = "faiss.index"
    chunks_path = "chunks.json"
    output_wav = OUTPUT_WAV_PATH

    print("start Recording & STT")
    question = record_and_get_text()
    if not question:
        print("STT 실패")
        return False
    print("complete STT : ", question)

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        print(" 캐시된 인덱스 로딩")
        index, chunks = load_faiss_index(index_path, chunks_path)
    else:
        print(" 텍스트 로딩 및 인덱싱 시작")
        with open(text_path, encoding="utf-8") as f:
            full_text = f.read()
        chunks = chunk_text(full_text)
        index, _ = build_faiss(chunks)
        save_faiss_index(index, chunks, index_path, chunks_path)
        print(" 인덱싱 완료 및 저장")

    print("start ChatGPT")
    context = retrieve_top_k(index, question, chunks)
    answer = generate_answer(context, question)

    path = save_answer(answer)
    print("답변 저장:", path)
    print("답변: " + answer)
    print("답변 길이:", len(answer))
    print("complete ChatGPT")

    print("start TTS")
    if len(answer) > 300:
        print("TTS 텍스트가 300자를 초과하여 자릅니다.")
        answer = answer[:300]

    # 기존 wav 파일이 있으면 삭제
    if os.path.exists(output_wav):
        os.remove(output_wav)
        
    generate_tts(answer, output_path=output_wav)
    print("complete TTS")

    return True

# 요청 시 실행 + 결과 반환
@app.get("/api/wav")
async def get_tts_wav():
    success = run_pipeline()
    if success and os.path.exists(OUTPUT_WAV_PATH):
        return FileResponse(
            path=OUTPUT_WAV_PATH,
            media_type="audio/wav",
            filename="van_gogh_reply.wav"
        )
    return {"error": "파이프라인 처리에 실패했습니다."}


@app.get("/api/viseme")
async def get_viseme_sequence():
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        return {"error": "outputs 디렉토리가 없습니다."}

    # 가장 최근 파일 찾기
    txt_files = [f for f in os.listdir(output_dir) if f.endswith(".txt")]
    if not txt_files:
        return {"error": "outputs 디렉토리에 .txt 파일이 없습니다."}
    
    latest_file = max(txt_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
    latest_path = os.path.join(output_dir, latest_file)

    if not os.path.exists(OUTPUT_WAV_PATH):
        return {"error": "wav 파일이 존재하지 않습니다."}

    with open(latest_path, encoding="utf-8") as f:
        text = f.read()

    phonemes = g2p(text)
    duration = get_duration(OUTPUT_WAV_PATH)
    interval = duration / max(1, len(phonemes))

    viseme_seq = []
    for i, ph in enumerate(phonemes):
        if isinstance(ph, list):
            ph = ''.join(ph)
        eng_ph = korean_to_eng_phoneme.get(ph, "_")
        viseme_id = phoneme_to_viseme.get(eng_ph, 0)
        viseme_seq.append({
            "time": round(i * interval, 3),
            "viseme": viseme_id
        })

    return JSONResponse(content=viseme_seq)


# FastAPI 서버만 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pipeline:app", host="0.0.0.0", port=8000, reload=True)

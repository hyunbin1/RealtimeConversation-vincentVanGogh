from fastapi import FastAPI, Request 
from fastapi.responses import FileResponse, JSONResponse
from supertoneAPi import generate_tts
from rag import chunk_text, build_faiss, retrieve_top_k, save_faiss_index, load_faiss_index
from gpt import generate_answer, save_answer
from audioAndSTT import record_and_get_text
from g2pk import G2p
import os
import wave
import glob

app = FastAPI()
g2p = G2p()

WAV_PREFIX = "van_gogh_reply"
TXT_PREFIX = "answer"
WAV_EXT = ".wav"
TXT_EXT = ".txt"

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

def get_next_index(prefix: str, ext: str) -> int:
    files = glob.glob(f"{prefix}_*{ext}")
    indices = [int(f.split("_")[-1].split(".")[0]) for f in files if f.split("_")[-1].split(".")[0].isdigit()]
    return max(indices, default=0) + 1

def get_duration(wav_path):
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def save_answer(answer, index: int):
    path = f"{TXT_PREFIX}_{index}{TXT_EXT}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(answer)
    return path

def run_pipeline():
    text_path = "반고흐_편지_원문.txt"
    index_path = "faiss.index"
    chunks_path = "chunks.json"
    index = get_next_index(WAV_PREFIX, WAV_EXT)
    output_wav = f"{WAV_PREFIX}_{index}{WAV_EXT}"
    output_txt = f"{TXT_PREFIX}_{index}{TXT_EXT}"

    print("start Recording & STT")
    question = record_and_get_text()
    if not question:
        print("STT 실패")
        return None, None
    print("complete STT : ", question)

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        print(" 캐시된 인덱스 로딩")
        index_obj, chunks = load_faiss_index(index_path, chunks_path)
    else:
        print(" 텍스트 로딩 및 인덱싱 시작")
        with open(text_path, encoding="utf-8") as f:
            full_text = f.read()
        chunks = chunk_text(full_text)
        index_obj, _ = build_faiss(chunks)
        save_faiss_index(index_obj, chunks, index_path, chunks_path)
        print(" 인덱싱 완료 및 저장")

    print("start ChatGPT")
    context = retrieve_top_k(index_obj, question, chunks)
    answer = generate_answer(context, question)
    save_answer(answer, index)
    print("답변 저장 완료")
    print("complete ChatGPT")

    print("start TTS")
    if len(answer) > 300:
        print("TTS 텍스트가 300자를 초과하여 자릅니다.")
        answer = answer[:300]
    generate_tts(answer, output_path=output_wav)
    print("complete TTS")

    return output_wav, output_txt


def run_pipeline1(question_text: str):
    text_path = "반고흐_편지_원문.txt"
    index_path = "faiss.index"
    chunks_path = "chunks.json"
    index = get_next_index(WAV_PREFIX, WAV_EXT)
    output_wav = f"{WAV_PREFIX}_{index}{WAV_EXT}"
    output_txt = f"{TXT_PREFIX}_{index}{TXT_EXT}"

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        index_obj, chunks = load_faiss_index(index_path, chunks_path)
    else:
        with open(text_path, encoding="utf-8") as f:
            full_text = f.read()
        chunks = chunk_text(full_text)
        index_obj, _ = build_faiss(chunks)
        save_faiss_index(index_obj, chunks, index_path, chunks_path)

    context = retrieve_top_k(index_obj, question_text, chunks)
    answer = generate_answer(context, question_text)
    save_answer(answer, index)

    if len(answer) > 300:
        answer = answer[:300]
    generate_tts(answer, output_path=output_wav)

    return output_wav, output_txt

@app.get("/api/wav")
async def get_tts_wav():
    wav_path, _ = run_pipeline()
    if wav_path and os.path.exists(wav_path):
        return FileResponse(
            path=wav_path,
            media_type="audio/wav",
            filename=os.path.basename(wav_path)
        )
    return {"error": "파이프라인 처리에 실패했습니다."}

@app.get("/api/viseme/{index}")
async def get_viseme_sequence(index: int):
    wav_path = f"{WAV_PREFIX}_{index}{WAV_EXT}"
    txt_path = f"{TXT_PREFIX}_{index}{TXT_EXT}"

    if not os.path.exists(txt_path):
        return {"error": f"{txt_path} 파일이 존재하지 않습니다."}
    if not os.path.exists(wav_path):
        return {"error": f"{wav_path} 파일이 존재하지 않습니다."}

    with open(txt_path, encoding="utf-8") as f:
        text = f.read()

    print("GPT 텍스트:", text)

    phonemes = g2p(text)
    print("Phonemes:", phonemes)

    duration = get_duration(wav_path)
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

@app.get("/api/test")
async def get_test_wav():
    question = "반고흐의 해바라기에 대해서 설명해줘"
    wav_path, _ = run_pipeline1(question)
    if wav_path and os.path.exists(wav_path):
        return FileResponse(
            path=wav_path,
            media_type="audio/wav",
            filename=os.path.basename(wav_path)
        )
    return {"error": "파이프라인 처리에 실패했습니다."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pipeline:app", host="0.0.0.0", port=8000, reload=True)

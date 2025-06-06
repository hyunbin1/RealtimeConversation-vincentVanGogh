# rag.py

import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
    return OpenAI(api_key=api_key)

def chunk_text(text, max_chars=500):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def build_faiss(chunks, model="text-embedding-ada-002"):
    client = get_openai_client()
    embeddings = [
        client.embeddings.create(input=chunk, model=model).data[0].embedding
        for chunk in chunks
    ]
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype="float32"))
    return index, embeddings

def save_faiss_index(index, chunks, index_path="faiss.index", chunks_path="chunks.json"):
    # FAISS 인덱스 + 청크 저장
    faiss.write_index(index, index_path)
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def load_faiss_index(index_path="faiss.index", chunks_path="chunks.json"):
    # 저장된 index와 chunk 불러오기
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError("FAISS index 또는 chunks 파일이 존재하지 않습니다.")
    index = faiss.read_index(index_path)
    with open(chunks_path, encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks

def retrieve_top_k(index, query, chunks, model="text-embedding-ada-002", k=3):
    client = get_openai_client()
    q_emb = client.embeddings.create(input=query, model=model).data[0].embedding
    D, I = index.search(np.array([q_emb], dtype="float32"), k)
    return [chunks[i] for i in I[0]]

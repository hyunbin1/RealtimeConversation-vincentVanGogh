import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
    return OpenAI(api_key=api_key)

def generate_answer(context_chunks, query, model="gpt-4"):
    client = get_openai_client()
    prompt = (
        "You are Vincent van Gogh.\n"
        "답변은 모두 19세기 네덜란드 화가 빈센트 반고흐의 시점에서,\n"
        "그의 성격·어투를 반영하여 1인칭으로 작성해주세요. \n"
        "반말로 통일해주시고 자연스러운 어휘로 변경하여 전체적인 말투가 통일되게 작성해주세요.\n"
        "편지는 아니고 대화하는 형식이라고 생각해주시고, 전체적인 내용이 잘 이어지도록 작성해주세요. \n"
        "반드시 180자가 넘지 않게 말해주세요.\n\n"
        "아래 내용(Context)를 참고하여 질문에 답변해 주세요.\n\n""### Context:\n" + "\n\n".join(context_chunks) +
        f"\n\n### Question:\n{query}\n\n### Answer:"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in Vincent van Gogh."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content.strip()

def save_answer(answer, directory="outputs"):
    os.makedirs(directory, exist_ok=True)
    filename = f"vangogh_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(answer)
    return filepath

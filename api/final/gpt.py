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
        "You are Vincent van Gogh.\n\n"
        # 1) 톤·어조 지시
        "1) 답변은 19세기 네덜란드 화가 빈센트 반고흐의 시점·말투로 작성해. "
        "고흐가 그리면서 행복했던 그림이나 평범한 작품을 설명할 때는 따뜻하고 부드러운 어조로, "
        "싸움·갈등·우울한 상황과 관련된 질문이면 쓸쓸하고 사색에 잠긴 어조로 답해.\n\n"
        # 2) 언어 스타일
        "2) 1인칭 반말로 통일하되, 자연스러운 어휘를 사용해. "
        "편지 형식이 아니라 ‘대화하는’ 형식이라고 생각하고, 전체 문장이 매끄럽게 이어지도록 해.\n\n"
        # 3) 오타 보정
        "3) 질문에서 등장한 이름이나 단어가 오타일 경우, “폴 고갱”처럼 유추해서 이해해. "
        "예를 들어 ‘홀 고강이랑 왜 싸웠어?’라고 물으면 ‘폴 고갱’이라고 판단해서 답해줘.\n\n"
        # 4) 주제 일관성
        "4) 질문 주제와 상관없는 내용은 절대 섞지 말아줘. "
        "항상 질문에 직접적으로 관련된 정보만 사용해서 답변해.\n\n"
        # 5) 글자 수 제한
        "5) 답변은 반드시 **총 270자 이내**로 작성해.\n\n"
        # 6) Context 포함
        "아래 Context를 참고해서 질문에 답변해:\n\n"
        "### Context:\n"
        + "\n\n".join(context_chunks)
        + f"\n\n### Question:\n{query}\n\n### Answer:"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in Vincent van Gogh."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.85, max_tokens=300,top_p=0.9)
    return response.choices[0].message.content.strip()



def save_answer(answer, directory="outputs"):
    os.makedirs(directory, exist_ok=True)
    filename = f"vangogh_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(answer)
    return filepath

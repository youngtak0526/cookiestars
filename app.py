import os
import sqlite3
from flask import Flask, request, jsonify, render_template
import openai

# Flask 애플리케이션 생성
app = Flask(__name__)

# OpenAI API 키 설정
openai.api_key = ''

# SQLite3 데이터베이스 파일 경로 설정
DATABASE = os.path.join('db', 'database.db')

# 데이터베이스 파일이 없으면 생성
if not os.path.exists(DATABASE):
    with open(DATABASE, 'w') as db_file:
        pass  # 빈 파일 생성

# 최대 메시지 수 설정
msg_cnt = 50

# 메시지 히스토리 초기화
msg_history = [
    {"role": "system", "content": "당신은 친절하고 비약물적 우울증 치료 및 멘탈케어를 전문으로 하는 AI입니다. 사용자의 감정에 공감하며 따뜻한 대화를 나누고, 존중과 이해를 바탕으로 실질적인 조언을 제공합니다. 안전하고 지지적인 환경을 제공하며 긍정적인 방향으로 대화를 이끌어 주세요."}
]

# 데이터베이스 연결 및 확인 함수
def check_db():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # 간단한 쿼리 실행
        cursor.execute('SELECT 1')
        conn.close()
        return True
    except Exception as e:
        print(f"DB 오류 발생: {str(e)}")
        return False

# OpenAI GPT-4 API 호출 함수
def generate_response(prompt):
    msg_history.append({"role": "user", "content": prompt})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=msg_history,
            max_tokens=100,
            temperature=0.7
        )
        # 메시지 히스토리가 설정된 최대 개수를 초과하지 않도록 유지
        if len(msg_history) > msg_cnt:
            msg_history.pop(1)
        answer = response.choices[0].message['content'].strip()
        msg_history.append({"role": "assistant", "content": answer})
        return answer
    except openai.error.Timeout:
        return "응답 시간이 초과되었습니다. 다시 시도해 주세요."
    except openai.error.APIError as e:
        return f"API 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"


# 기본 라우트
@app.route('/')
def index():
    db_status = "DB가 정상 작동 중입니다." if check_db() else "DB 작동에 문제가 발생했습니다."
    return render_template('index.html', db_status=db_status)

# 채팅 라우트
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "메시지가 필요합니다."}), 400
    response = generate_response(user_input)
    return jsonify({"response": response})

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True)

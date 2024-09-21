import os
import sqlite3
from flask import Flask, request, jsonify, render_template
import openai
from flask_cors import CORS

# Flask 애플리케이션 생성
app = Flask(__name__)
CORS(app)

# OpenAI API 키 설정
openai.api_key = ''

# SQLite3 데이터베이스 파일 경로 설정
DATABASE = os.path.join('db', 'database.db')

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthdate TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 최대 메시지 수 설정
msg_cnt = 50

# 메시지 히스토리 초기화
msg_history = [
    {"role": "system", "content": "당신은 친절하고 비약물적 우울증 치료 및 멘탈케어를 전문으로 하는 AI입니다. 사용자의 감정에 공감하며 따뜻한 대화를 나누고, 존중과 이해를 바탕으로 실질적인 조언을 제공합니다. 안전하고 지지적인 환경을 제공하며 긍정적인 방향으로 대화를 이끌어 주세요."}
]

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

@app.route('/')
def index():
    return render_template('membership.html')

# 회원가입 라우트
@app.route('/membership', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({"status": "error", "error": "잘못된 요청입니다."}), 400  # 빈 요청 처리

    name = data.get("name")
    birthdate = data.get("birthdate")
    email = data.get("email")
    password = data.get("password")

    # 유효성 검사
    if not all([name, birthdate, email, password]):
        return jsonify({"status": "error", "error": "모든 필드를 입력해 주세요."}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # 데이터 삽입
        cursor.execute('''
            INSERT INTO users (name, birthdate, email, password)
            VALUES (?, ?, ?, ?)
        ''', (name, birthdate, email, password))
        
        conn.commit()  # 변경사항 저장

        return jsonify({"status": "success", "message": "회원가입 성공!"}), 201  # 성공 메시지

    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "error": "이미 등록된 이메일입니다."}), 400
    except sqlite3.Error as e:
        return jsonify({"status": "error", "error": f"DB 오류 발생: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": f"오류가 발생했습니다: {str(e)}"}), 500
    finally:
        conn.close()

# DB 내용 확인 라우트
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"status": "error", "error": f"DB 오류 발생: {str(e)}"}), 500
    finally:
        conn.close()

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
    init_db()  # 데이터베이스 초기화
    app.run(debug=True)

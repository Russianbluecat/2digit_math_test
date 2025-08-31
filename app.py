import streamlit as st
import random
import time

def init_session_state():
    """세션 상태 초기화"""
    defaults = {
        'game_started': False,
        'current_question': 0,
        'score': 0,
        'questions': [],
        'answers': [],
        'user_answers': [],
        'question_start_time': None,
        'game_finished': False,
        'waiting_for_answer': True,
        'last_result': "",
        'operation_mode': "random"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def generate_question():
    """두 자리 수 연산 문제 생성"""
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    
    mode = st.session_state.operation_mode
    
    if mode == "addition":
        operation = '+'
        answer = num1 + num2
    elif mode == "subtraction":
        operation = '-'
        # 뺄셈에서 무조건 큰 수에서 작은 수를 빼도록 수정
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
    else:  # 랜덤
        if random.choice([True, False]):
            operation = '+'
            answer = num1 + num2
        else:
            operation = '-'
            # 뺄셈에서 무조건 큰 수에서 작은 수를 빼도록 수정
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
    
    question = f"{num1} {operation} {num2}"
    return question, answer

def generate_all_questions():
    """10개의 문제 미리 생성"""
    questions = []
    answers = []
    for _ in range(10):
        question, answer = generate_question()
        questions.append(question)
        answers.append(answer)
    return questions, answers

def start_game():
    """게임 시작"""
    # 기존 입력 필드 초기화
    clear_input_fields()
    
    st.session_state.update({
        'game_started': True,
        'current_question': 0,
        'score': 0,
        'game_finished': False,
        'user_answers': [],
        'waiting_for_answer': True,
        'last_result': "",
        'question_start_time': time.time()
    })
    
    st.session_state.questions, st.session_state.answers = generate_all_questions()
    st.rerun()

def clear_input_fields():
    """입력 필드 초기화"""
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith('user_input_')]
    for key in keys_to_delete:
        del st.session_state[key]

def submit_answer():
    """답안 제출 처리"""
    current_idx = st.session_state.current_question
    correct_answer = st.session_state.answers[current_idx]
    user_input = st.session_state.get(f"user_input_{current_idx}", "")
    
    # 시간 확인
    elapsed_time = time.time() - st.session_state.question_start_time
    
    if elapsed_time > 5.0:  # 5초 초과
        st.session_state.user_answers.append(None)
        st.session_state.last_result = f"⏰ 시간 초과! 정답은 {correct_answer}입니다."
    else:
        try:
            user_answer = int(user_input.strip()) if user_input.strip() else None
            st.session_state.user_answers.append(user_answer)
            
            if user_answer == correct_answer:
                st.session_state.score += 1
                st.session_state.last_result = "✅ 정답입니다!"
            else:
                st.session_state.last_result = f"❌ 틀렸습니다. 정답은 {correct_answer}입니다."
        except ValueError:
            st.session_state.user_answers.append(None)
            st.session_state.last_result = f"❌ 올바른 숫자를 입력해주세요. 정답은 {correct_answer}입니다."
    
    # 다음 문제로 이동 또는 게임 종료
    if st.session_state.current_question < 9:
        st.session_state.current_question += 1
        st.session_state.waiting_for_answer = False
    else:
        st.session_state.game_finished = True
        st.session_state.waiting_for_answer = False

def next_question():
    """다음 문제로 이동"""
    st.session_state.waiting_for_answer = True
    st.session_state.question_start_time = time.time()

def reset_game():
    """게임 리셋"""
    clear_input_fields()
    
    st.session_state.update({
        'game_started': False,
        'current_question': 0,
        'score': 0,
        'game_finished': False,
        'waiting_for_answer': True,
        'last_result': "",
        'questions': [],
        'answers': [],
        'user_answers': [],
        'question_start_time': None
    })
    st.rerun()

def display_game_rules():
    """게임 규칙 표시"""
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
    <h3>🎯 게임 소개</h3>
    <p style='font-size: 18px;'>두 자리 수 연산을 5초 이내에 풀어보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **📋 게임 규칙:**
    - 총 10문제가 출제됩니다
    - 각 문제당 제한시간은 5초입니다  
    - 덧셈, 뺄셈, 또는 랜덤 연산이 나옵니다
    - 5초를 초과하면 자동으로 오답 처리됩니다
    """)

def display_question_timer():
    """문제와 타이머 표시"""
    current_idx = st.session_state.current_question
    elapsed = time.time() - st.session_state.question_start_time
    remaining = max(0, 5 - elapsed)
    
    # 현재 문제 표시
    st.markdown(f"""
    <div style='text-align: center; padding: 30px 0;'>
    <h2>문제 {current_idx + 1}</h2>
    <h1 style='font-size: 3.5em; color: #1f77b4; margin: 20px 0;'>{st.session_state.questions[current_idx]} = ?</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 남은 시간 표시
    if remaining > 0:
        color = "red" if remaining <= 1 else "orange" if remaining <= 2 else "green"
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
        <h3 style='color: {color}; font-size: 1.5em;'>⏰ {remaining:.1f}초</h3>
        </div>
        """, unsafe_allow_html=True)
        return True
    return False

def display_answer_input():
    """답안 입력 인터페이스 표시"""
    current_idx = st.session_state.current_question
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 자동 포커스를 위한 JavaScript
        st.markdown("""
        <script>
        setTimeout(function() {
            const inputs = document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                const lastInput = inputs[inputs.length - 1];
                lastInput.focus();
                lastInput.select();
                
                // Enter 키 이벤트 리스너 추가
                lastInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const buttons = document.querySelectorAll('button[kind="primary"]');
                        if (buttons.length > 0) {
                            buttons[buttons.length - 1].click();
                        }
                    }
                });
            }
        }, 200);
        </script>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input(
            "답:",
            key=f"user_input_{current_idx}",
            placeholder="숫자 입력 후 Enter",
            label_visibility="collapsed"
        )
        
        if st.button("📱 제출", type="primary", use_container_width=True, key=f"submit_{current_idx}"):
            submit_answer()
            st.rerun()

def display_final_results():
    """최종 결과 화면 표시"""
    percentage = (st.session_state.score / 10) * 100
    
    st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 20px 0; color: white;'>
    <h2>🎯 최종 결과</h2>
    <h1 style='font-size: 2.5em; margin: 20px 0;'>{percentage:.0f}%</h1>
    <p style='font-size: 20px;'>10문제 중 {st.session_state.score}개 정답!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 성과에 따른 메시지
    if percentage >= 90:
        st.balloons()
        st.success("🏆 훌륭합니다! 수학 천재시네요!")
    elif percentage >= 70:
        st.success("👏 잘했습니다! 계산이 빠르시네요!")
    elif percentage >= 50:
        st.info("💪 괜찮습니다! 조금 더 연습하면 더 좋아질 거예요!")
    else:
        st.info("📚 연습이 필요해요! 다시 도전해보세요!")

def display_detailed_results():
    """상세 결과 표시"""
    with st.expander("📊 상세 결과 보기"):
        for i in range(10):
            question = st.session_state.questions[i]
            correct = st.session_state.answers[i]
            user = st.session_state.user_answers[i]
            
            if user is None:
                status = "❌ 시간 초과"
                user_display = "시간 초과"
            elif user == correct:
                status = "✅ 정답"
                user_display = str(user)
            else:
                status = "❌ 오답"
                user_display = str(user)
            
            st.write(f"**{i+1}.** {question} = {correct} | 입력: {user_display} | {status}")

def setup_mobile_styles():
    """모바일 최적화 CSS 설정"""
    st.markdown("""
    <style>
    /* 모바일 최적화 */
    .stApp {
        max-width: 100%;
        padding: 10px;
    }
    
    /* 입력 필드 크기 조정 */
    .stTextInput input {
        font-size: 20px !important;
        text-align: center !important;
        height: 50px !important;
    }
    
    /* 버튼 크기 조정 */
    .stButton button {
        font-size: 18px !important;
        height: 50px !important;
        border-radius: 10px !important;
    }
    
    /* 진행률 바 스타일 */
    .stProgress > div > div {
        background-color: #1f77b4 !important;
    }
    
    @media (max-width: 768px) {
        .stTextInput input {
            font-size: 24px !important;
            height: 60px !important;
        }
        .stButton button {
            font-size: 20px !important;
            height: 60px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="두 자리 수 연산 퀴즈", 
        page_icon="🧮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    setup_mobile_styles()
    init_session_state()
    
    st.title("🧮 두 자리 수 연산 퀴즈")
    
    # 게임 시작 전 화면
    if not st.session_state.game_started:
        display_game_rules()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎮 시작하기", type="primary", use_container_width=True):
                start_game()
    
    # 게임 진행 중
    elif st.session_state.game_started and not st.session_state.game_finished:
        current_idx = st.session_state.current_question
        
        # 진행률 표시
        progress = current_idx / 10
        st.progress(progress, text=f"문제 {current_idx + 1}/10")
        
        # 답안 입력 대기 상태
        if st.session_state.waiting_for_answer:
            # 시간이 남아있는 경우에만 입력 화면 표시
            if display_question_timer():
                display_answer_input()
                # 주기적 업데이트를 위한 짧은 대기
                time.sleep(0.1)
                st.rerun()
            else:
                # 시간 초과 자동 처리
                submit_answer()
                st.rerun()
        
        # 결과 표시 + 다음 문제 화면
        else:
            # 결과 메시지 표시
            if "정답" in st.session_state.last_result:
                st.success(f"🎉 {st.session_state.last_result}")
            else:
                st.error(f"😅 {st.session_state.last_result}")
            
            # 다음 문제가 있으면 2초 후 자동으로 시작
            if current_idx < 10:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='text-align: center; padding: 20px 0;'>
                <h3>다음 문제</h3>
                <h1 style='font-size: 3em; color: #1f77b4;'>{st.session_state.questions[current_idx]} = ?</h1>
                <p style='color: #666; font-size: 16px;'>2초 후 자동 시작...</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 2초 대기 후 자동으로 다음 문제 시작
                time.sleep(2)
                next_question()
                st.rerun()
    
    # 게임 완료 화면
    elif st.session_state.game_finished:
        st.markdown("## 🎉 게임 완료!")
        
        # 마지막 문제 결과 표시
        if st.session_state.last_result:
            if "정답" in st.session_state.last_result:
                st.success(f"🎉 {st.session_state.last_result}")
            else:
                st.error(f"😅 {st.session_state.last_result}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 최종 결과 표시
        display_final_results()
        
        # 상세 결과 표시
        display_detailed_results()
        
        # 다시 하기 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 다시 하기", type="primary", use_container_width=True):
                reset_game()

if __name__ == "__main__":
    main()

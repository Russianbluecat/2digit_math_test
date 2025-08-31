import streamlit as st
import random
import time

def init_session_state():
    """세션 상태 초기화"""
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    if 'game_finished' not in st.session_state:
        st.session_state.game_finished = False
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = True
    if 'last_result' not in st.session_state:
        st.session_state.last_result = ""
    if 'operation_mode' not in st.session_state:
        st.session_state.operation_mode = "random"

def generate_question():
    """두 자리 수 연산 문제 생성"""
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    
    # 선택된 연산 모드에 따라 문제 생성
    mode = st.session_state.operation_mode
    
    if mode == "addition":  # 덧셈만
        operation = '+'
        answer = num1 + num2
    elif mode == "subtraction":  # 뺄셈만
        operation = '-'
        answer = num1 - num2
    else:  # 랜덤 (덧셈 또는 뺄셈)
        if random.choice([True, False]):
            operation = '+'
            answer = num1 + num2
        else:
            operation = '-'
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
    st.session_state.game_started = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.game_finished = False
    st.session_state.user_answers = []
    st.session_state.waiting_for_answer = True
    st.session_state.last_result = ""
    st.session_state.questions, st.session_state.answers = generate_all_questions()
    st.session_state.question_start_time = time.time()
    st.rerun()

def submit_answer():
    """답안 제출 처리"""
    current_idx = st.session_state.current_question
    correct_answer = st.session_state.answers[current_idx]
    user_input = st.session_state.get(f"user_input_{current_idx}", "")
    
    # 시간 확인
    elapsed_time = time.time() - st.session_state.question_start_time
    
    if elapsed_time > 5.0:  # 5초 초과
        st.session_state.user_answers.append(None)
        st.session_state.last_result = f"⏰ 시간 초과! 틀렸습니다. 정답은 {correct_answer}였습니다."
    else:
        try:
            user_answer = int(user_input) if user_input.strip() else None
            st.session_state.user_answers.append(user_answer)
            
            if user_answer == correct_answer:
                st.session_state.score += 1
                st.session_state.last_result = "✅ 맞췄습니다!"
            else:
                st.session_state.last_result = f"❌ 틀렸습니다. 정답은 {correct_answer}였습니다."
        except ValueError:
            st.session_state.user_answers.append(None)
            st.session_state.last_result = f"❌ 올바른 숫자를 입력해주세요. 정답은 {correct_answer}였습니다."
    
    # 다음 문제로 이동 또는 게임 종료
    if st.session_state.current_question < 9:
        st.session_state.current_question += 1
        st.session_state.question_start_time = time.time()
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
    for key in list(st.session_state.keys()):
        if key.startswith('user_input_'):
            del st.session_state[key]
    
    st.session_state.game_started = False
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.game_finished = False
    st.session_state.waiting_for_answer = True
    st.session_state.last_result = ""
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.user_answers = []
    st.session_state.question_start_time = None
    st.rerun()

def main():
    st.set_page_config(
        page_title="두 자리 수 연산 퀴즈", 
        page_icon="🧮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    init_session_state()
    
    st.title("🧮 두 자리 수 연산 퀴즈")
    
    # 게임 시작 전 화면
    if not st.session_state.game_started:
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎮 시작하기", type="primary", use_container_width=True):
                start_game()
    
    # 게임 진행 중
    elif st.session_state.game_started and not st.session_state.game_finished:
        current_idx = st.session_state.current_question
        
        # 진행률 표시
        progress = (current_idx) / 10
        st.progress(progress, text=f"문제 {current_idx + 1}/10")
        
        # 답안 입력 대기 상태
        if st.session_state.waiting_for_answer:
            # 현재 문제 표시
            st.markdown(f"""
            <div style='text-align: center; padding: 30px 0;'>
            <h2>문제 {current_idx + 1}</h2>
            <h1 style='font-size: 3em; color: #1f77b4;'>{st.session_state.questions[current_idx]} = ?</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # 남은 시간 표시 및 자동 처리
            if st.session_state.question_start_time:
                elapsed = time.time() - st.session_state.question_start_time
                remaining = max(0, 5 - elapsed)
                
                # 시간 표시
                if remaining > 0:
                    st.markdown(f"""
                    <div style='text-align: center;'>
                    <h3 style='color: {"red" if remaining <= 1 else "orange" if remaining <= 2 else "green"};'>
                    ⏰ 남은 시간: {remaining:.1f}초
                    </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 답안 입력 (모바일 최적화)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        user_input = st.text_input(
                            "답:", 
                            key=f"user_input_{current_idx}",
                            placeholder="답을 입력하세요",
                            label_visibility="collapsed"
                        )
                        
                        if st.button("제출", type="primary", use_container_width=True):
                            submit_answer()
                            st.rerun()
                    
                    # Enter 키 지원을 위한 JavaScript
                    st.markdown("""
                    <script>
                    setTimeout(function() {
                        const input = document.querySelector('input[type="text"]');
                        if (input) {
                            input.addEventListener('keydown', function(e) {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    const submitBtn = document.querySelector('[data-testid="stButton"] button');
                                    if (submitBtn) submitBtn.click();
                                }
                            });
                        }
                    }, 100);
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # 자동 새로고침 (시간 체크)
                    time.sleep(0.1)
                    st.rerun()
                else:
                    # 시간 초과
                    submit_answer()
                    st.rerun()
        
        # 결과 표시 + 다음 문제 상태
        else:
            # 결과 메시지 표시
            if "맞췄습니다" in st.session_state.last_result:
                st.success(st.session_state.last_result)
            else:
                st.error(st.session_state.last_result)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 다음 문제가 있으면 표시
            if current_idx < 10:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px 0;'>
                <h2>문제 {current_idx + 1}</h2>
                <h1 style='font-size: 3em; color: #1f77b4;'>{st.session_state.questions[current_idx]} = ?</h1>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("다음 문제 시작!", type="primary", use_container_width=True):
                        next_question()
                        st.rerun()
    
    # 게임 완료 화면
    elif st.session_state.game_finished:
        st.markdown("## 🎉 게임 완료!")
        
        # 마지막 문제 결과 표시
        if st.session_state.last_result:
            if "맞췄습니다" in st.session_state.last_result:
                st.success(st.session_state.last_result)
            else:
                st.error(st.session_state.last_result)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 최종 점수 계산
        percentage = (st.session_state.score / 10) * 100
        
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin: 20px 0;'>
        <h2>🎯 최종 결과</h2>
        <h1 style='color: #1f77b4;'>10문제 중 {percentage:.0f}% 맞췄습니다!</h1>
        <p style='font-size: 18px;'>정답: {st.session_state.score}개 | 오답: {10 - st.session_state.score}개</p>
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
        
        # 상세 결과 보기
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
                
                st.write(f"{i+1}. {question} = {correct} | 입력: {user_display} | {status}")
        
        # 다시 하기 버튼 (모바일 최적화)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 다시 하기", type="primary", use_container_width=True):
                reset_game()

def reset_game():
    """게임 리셋"""
    # 모든 input 키 삭제
    for key in list(st.session_state.keys()):
        if key.startswith('user_input_'):
            del st.session_state[key]
    
    st.session_state.game_started = False
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.game_finished = False
    st.session_state.waiting_for_answer = True
    st.session_state.last_result = ""
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.user_answers = []
    st.session_state.question_start_time = None
    st.rerun()

def main():
    st.set_page_config(
        page_title="두 자리 수 연산 퀴즈", 
        page_icon="🧮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # 모바일 최적화 CSS
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
    
    init_session_state()
    
    st.title("🧮 두 자리 수 연산 퀴즈")
    
    # 게임 시작 전 화면
    if not st.session_state.game_started:
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎮 시작하기", type="primary", use_container_width=True):
                start_game()
    
    # 게임 진행 중
    elif st.session_state.game_started and not st.session_state.game_finished:
        current_idx = st.session_state.current_question
        
        # 진행률 표시
        progress = (current_idx) / 10
        st.progress(progress, text=f"문제 {current_idx + 1}/10")
        
        # 답안 입력 대기 상태
        if st.session_state.waiting_for_answer:
            # 현재 문제 표시
            st.markdown(f"""
            <div style='text-align: center; padding: 30px 0;'>
            <h2>문제 {current_idx + 1}</h2>
            <h1 style='font-size: 3.5em; color: #1f77b4; margin: 20px 0;'>{st.session_state.questions[current_idx]} = ?</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # 시간 및 입력 처리
            if st.session_state.question_start_time:
                elapsed = time.time() - st.session_state.question_start_time
                remaining = max(0, 5 - elapsed)
                
                if remaining > 0:
                    # 남은 시간 표시
                    color = "red" if remaining <= 1 else "orange" if remaining <= 2 else "green"
                    st.markdown(f"""
                    <div style='text-align: center; margin: 20px 0;'>
                    <h3 style='color: {color}; font-size: 1.5em;'>⏰ {remaining:.1f}초</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 답안 입력
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        user_input = st.text_input(
                            "답:",
                            key=f"user_input_{current_idx}",
                            placeholder="숫자 입력",
                            label_visibility="collapsed"
                        )
                        
                        submit_col1, submit_col2 = st.columns(2)
                        with submit_col1:
                            if st.button("📱 제출", type="primary", use_container_width=True):
                                submit_answer()
                                st.rerun()
                        with submit_col2:
                            if st.button("⏩ 넘어가기", use_container_width=True):
                                st.session_state[f"user_input_{current_idx}"] = ""
                                submit_answer()
                                st.rerun()
                    
                    # 자동 새로고침 (시간 체크)
                    time.sleep(0.1)
                    st.rerun()
                else:
                    # 시간 초과 자동 처리
                    submit_answer()
                    st.rerun()
        
        # 결과 표시 + 다음 문제 화면
        else:
            # 결과 메시지 표시
            if "맞췄습니다" in st.session_state.last_result:
                st.success(f"🎉 {st.session_state.last_result}")
            else:
                st.error(f"😅 {st.session_state.last_result}")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # 다음 문제 표시
            if current_idx < 10:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px 0;'>
                <h3>다음 문제</h3>
                <h1 style='font-size: 3em; color: #1f77b4;'>{st.session_state.questions[current_idx]} = ?</h1>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("▶️ 시작!", type="primary", use_container_width=True):
                        next_question()
                        st.rerun()
    
    # 게임 완료 화면
    elif st.session_state.game_finished:
        st.markdown("## 🎉 게임 완료!")
        
        # 마지막 문제 결과 표시
        if st.session_state.last_result:
            if "맞췄습니다" in st.session_state.last_result:
                st.success(f"🎉 {st.session_state.last_result}")
            else:
                st.error(f"😅 {st.session_state.last_result}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 최종 점수 계산
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
        
        # 상세 결과 보기
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
        
        # 다시 하기 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 다시 하기", type="primary", use_container_width=True):
                reset_game()

if __name__ == "__main__":
    main()

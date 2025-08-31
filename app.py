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
        'show_result': False,
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
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
    else:  # 랜덤
        if random.choice([True, False]):
            operation = '+'
            answer = num1 + num2
        else:
            operation = '-'
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
    st.session_state.update({
        'game_started': True,
        'current_question': 0,
        'score': 0,
        'game_finished': False,
        'show_result': False,
        'user_answers': [],
        'last_result': "",
        'question_start_time': time.time()
    })
    
    st.session_state.questions, st.session_state.answers = generate_all_questions()
    st.rerun()

def check_answer():
    """답안 확인 및 처리"""
    current_idx = st.session_state.current_question
    correct_answer = st.session_state.answers[current_idx]
    user_input = st.session_state.get(f"answer_input", "")
    
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
    
    # 다음 문제로 바로 이동 (결과 표시는 동시에)
    if st.session_state.current_question < 9:
        st.session_state.current_question += 1
        st.session_state.question_start_time = time.time()
        st.session_state.show_result = True
    else:
        st.session_state.game_finished = True
    
    # 입력 필드 초기화
    if 'answer_input' in st.session_state:
        del st.session_state['answer_input']

def next_question():
    """다음 문제로 이동"""
    if st.session_state.current_question < 9:
        st.session_state.current_question += 1
        st.session_state.show_result = False
        st.session_state.question_start_time = time.time()
    else:
        st.session_state.game_finished = True

def reset_game():
    """게임 리셋"""
    # 모든 관련 세션 상태 초기화
    keys_to_delete = [key for key in list(st.session_state.keys()) if key.startswith('answer_input')]
    for key in keys_to_delete:
        del st.session_state[key]
    
    st.session_state.update({
        'game_started': False,
        'current_question': 0,
        'score': 0,
        'game_finished': False,
        'show_result': False,
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
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin: 20px 0;'>
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
    - 숫자 입력 후 Enter 키를 누르거나 제출 버튼을 클릭하세요
    """)
    
    # 연산 모드 선택
    st.markdown("**🎮 연산 모드 선택:**")
    operation_mode = st.selectbox(
        "연산 종류를 선택하세요:",
        ["random", "addition", "subtraction"],
        format_func=lambda x: {"random": "🎲 랜덤 (덧셈+뺄셈)", 
                              "addition": "➕ 덧셈만", 
                              "subtraction": "➖ 뺄셈만"}[x],
        key="operation_select"
    )
    st.session_state.operation_mode = operation_mode

def display_question_with_timer():
    """문제와 실시간 타이머 표시"""
    current_idx = st.session_state.current_question
    elapsed = time.time() - st.session_state.question_start_time
    remaining = max(0, 5 - elapsed)
    
    # 현재 문제 표시
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 0;'>
    <h2>문제 {current_idx + 1}/10</h2>
    <h1 style='font-size: 4em; color: #1f77b4; margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>{st.session_state.questions[current_idx]} = ?</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 남은 시간 표시
    if remaining > 0:
        color = "#ff4444" if remaining <= 1 else "#ff8800" if remaining <= 2 else "#44aa44"
        width = (remaining / 5) * 100
        
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
        <div style='background: #eee; border-radius: 10px; height: 20px; margin: 10px auto; width: 300px; max-width: 90%;'>
        <div style='background: {color}; height: 100%; border-radius: 10px; width: {width}%; transition: width 0.1s;'></div>
        </div>
        <h3 style='color: {color}; font-size: 1.8em; margin: 10px 0;'>⏰ {remaining:.1f}초</h3>
        </div>
        """, unsafe_allow_html=True)
        return True
    return False

def display_answer_input():
    """개선된 답안 입력 인터페이스"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 폼을 사용하여 Enter 키 지원
        with st.form(key="answer_form", clear_on_submit=True):
            user_input = st.text_input(
                "답:",
                key="answer_input",
                placeholder="숫자 입력 후 Enter",
                label_visibility="collapsed"
            )
            
            submit_button = st.form_submit_button(
                "📱 제출", 
                type="primary", 
                use_container_width=True
            )
            
            # 폼 제출 시 답안 확인
            if submit_button:
                check_answer()
                st.rerun()

def display_result_and_next():
    """결과 표시와 동시에 다음 문제 + 입력칸 표시"""
    current_idx = st.session_state.current_question
    
    # 이전 문제 결과 표시
    if "정답" in st.session_state.last_result:
        st.success(f"🎉 {st.session_state.last_result}")
    else:
        st.error(f"😅 {st.session_state.last_result}")
    
    # 다음 문제가 있는 경우
    if current_idx < 10:
        st.markdown("<div style='margin: 20px 0; border-top: 2px dashed #ccc;'></div>", unsafe_allow_html=True)
        
        # 현재 문제 표시 + 입력칸 (결과 표시와 동시에)
        if display_question_with_timer():
            display_answer_input()
            # 타이머 업데이트
            time.sleep(0.1)
            st.rerun()
        else:
            # 시간 초과 처리
            check_answer()
            st.rerun()
    else:
        # 모든 문제 완료
        time.sleep(1)
        st.session_state.game_finished = True
        st.rerun()

def display_final_results():
    """최종 결과 화면 표시"""
    percentage = (st.session_state.score / 10) * 100
    
    # 성과에 따른 이모지와 메시지
    if percentage >= 90:
        emoji = "🏆"
        grade = "최고"
        message = "수학 천재시네요!"
        st.balloons()
    elif percentage >= 70:
        emoji = "🥇"
        grade = "우수"
        message = "계산이 빠르시네요!"
    elif percentage >= 50:
        emoji = "🥈"
        grade = "보통"
        message = "조금 더 연습하면 더 좋아질 거예요!"
    else:
        emoji = "🥉"
        grade = "연습필요"
        message = "다시 도전해보세요!"
    
    st.markdown(f"""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin: 20px 0; color: white; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
    <h1 style='font-size: 3em; margin: 10px 0;'>{emoji}</h1>
    <h2>🎯 최종 결과</h2>
    <h1 style='font-size: 3.5em; margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{percentage:.0f}%</h1>
    <p style='font-size: 24px; margin: 10px 0;'>10문제 중 {st.session_state.score}개 정답!</p>
    <p style='font-size: 18px; opacity: 0.9;'>{grade} 등급 - {message}</p>
    </div>
    """, unsafe_allow_html=True)

def display_detailed_results():
    """상세 결과 표시"""
    with st.expander("📊 상세 결과 보기", expanded=False):
        st.markdown("### 문제별 결과")
        
        for i in range(10):
            question = st.session_state.questions[i]
            correct = st.session_state.answers[i]
            user = st.session_state.user_answers[i]
            
            if user is None:
                status_color = "#ff4444"
                status = "❌ 시간 초과"
                user_display = "시간 초과"
            elif user == correct:
                status_color = "#44aa44"
                status = "✅ 정답"
                user_display = str(user)
            else:
                status_color = "#ff4444"
                status = "❌ 오답"
                user_display = str(user)
            
            st.markdown(f"""
            <div style='padding: 10px; margin: 5px 0; border-left: 4px solid {status_color}; background: #f8f9fa; border-radius: 5px;'>
            <strong>{i+1}.</strong> {question} = {correct} | 
            <strong>입력:</strong> {user_display} | 
            <span style='color: {status_color};'><strong>{status}</strong></span>
            </div>
            """, unsafe_allow_html=True)

def setup_mobile_styles():
    """모바일 최적화 CSS 설정"""
    st.markdown("""
    <style>
    /* 전체 앱 스타일 */
    .stApp {
        max-width: 100%;
        padding: 10px;
    }
    
    /* 입력 필드 최적화 */
    .stTextInput input {
        font-size: 24px !important;
        text-align: center !important;
        height: 60px !important;
        border: 2px solid #1f77b4 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .stTextInput input:focus {
        border-color: #0d5aa7 !important;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.25) !important;
    }
    
    /* 버튼 최적화 */
    .stButton button {
        font-size: 20px !important;
        height: 60px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* 폼 제출 버튼 */
    .stFormSubmitButton button {
        font-size: 20px !important;
        height: 60px !important;
        background: linear-gradient(135deg, #1f77b4 0%, #0d5aa7 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: bold !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* 진행률 바 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1f77b4 0%, #44aa44 100%) !important;
        border-radius: 10px !important;
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .stTextInput input {
            font-size: 28px !important;
            height: 70px !important;
        }
        .stButton button, .stFormSubmitButton button {
            font-size: 22px !important;
            height: 70px !important;
        }
    }
    
    /* 숨겨진 라벨 */
    .stTextInput label {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

def auto_focus_script():
    """자동 포커스 JavaScript (개선된 버전)"""
    st.markdown("""
    <script>
    function focusInput() {
        setTimeout(function() {
            const inputs = document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                const input = inputs[inputs.length - 1];
                input.focus();
                input.select();
            }
        }, 100);
    }
    
    // 페이지 로드 시 포커스
    focusInput();
    
    // Streamlit 재렌더링 후 포커스 (MutationObserver 사용)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                focusInput();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
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
    auto_focus_script()
    
    st.title("🧮 두 자리 수 연산 퀴즈")
    
    # 게임 시작 전 화면
    if not st.session_state.game_started:
        display_game_rules()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎮 게임 시작!", type="primary", use_container_width=True):
                start_game()
    
    # 게임 진행 중
    elif st.session_state.game_started and not st.session_state.game_finished:
        current_idx = st.session_state.current_question
        
        # 진행률 표시
        progress = (current_idx + 1) / 10
        st.progress(progress, text=f"진행률: {current_idx + 1}/10 문제")
        
        # 현재 점수 표시
        st.markdown(f"""
        <div style='text-align: center; margin: 10px 0;'>
        <span style='background: #e8f4f8; padding: 8px 16px; border-radius: 20px; font-weight: bold; color: #1f77b4;'>
        현재 점수: {st.session_state.score}/{current_idx + (1 if st.session_state.show_result else 0)}
        </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 결과 표시 중인 경우 (이전 문제 결과 + 현재 문제 입력)
        if st.session_state.show_result:
            display_result_and_next()
        
        # 첫 문제 또는 순수 답안 입력 상태
        else:
            # 시간 체크
            elapsed = time.time() - st.session_state.question_start_time
            if elapsed > 5.0:
                # 시간 초과 자동 처리
                check_answer()
                st.rerun()
            else:
                # 문제와 타이머 표시
                if display_question_with_timer():
                    display_answer_input()
                    # 타이머 업데이트를 위한 자동 새로고침
                    time.sleep(0.1)
                    st.rerun()
    
    # 게임 완료 화면
    elif st.session_state.game_finished:
        st.markdown("## 🎉 게임 완료!")
        
        # 마지막 문제 결과 표시 (아직 표시되지 않은 경우)
        if st.session_state.last_result and st.session_state.show_result:
            if "정답" in st.session_state.last_result:
                st.success(f"🎉 {st.session_state.last_result}")
            else:
                st.error(f"😅 {st.session_state.last_result}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 최종 결과 표시
        display_final_results()
        
        # 상세 결과 표시
        display_detailed_results()
        
        # 액션 버튼들
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 다시 하기", type="primary", use_container_width=True):
                reset_game()
        with col2:
            if st.button("🏠 처음으로", type="secondary", use_container_width=True):
                reset_game()

if __name__ == "__main__":
    main()

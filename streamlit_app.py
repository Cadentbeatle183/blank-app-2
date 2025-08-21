import streamlit as st
import random

# --- 게임 초기화 및 상태 관리 ---

# 세션 상태가 초기화되었는지 확인하고, 게임을 처음부터 다시 시작합니다.
def init_game():
    st.session_state.rows = 20
    st.session_state.cols = 20
    st.session_state.mines = 40
    
    # 지뢰와 숫자가 있는 실제 보드 생성
    board = [[' ' for _ in range(st.session_state.cols)] for _ in range(st.session_state.rows)]
    mines_loc = set()
    
    while len(mines_loc) < st.session_state.mines:
        r, c = random.randint(0, st.session_state.rows - 1), random.randint(0, st.session_state.cols - 1)
        if (r, c) not in mines_loc:
            mines_loc.add((r, c))
            board[r][c] = '*' 
            
    for r in range(st.session_state.rows):
        for c in range(st.session_state.cols):
            if board[r][c] == '*':
                continue
            count = sum(1 for dr in [-1, 0, 1] for dc in [-1, 0, 1]
                        if 0 <= r + dr < st.session_state.rows and 0 <= c + dc < st.session_state.cols and board[r + dr][c + dc] == '*')
            if count > 0:
                board[r][c] = str(count)

    st.session_state.board = board
    st.session_state.mines_loc = mines_loc
    
    # 사용자에게 보이는 보드 상태 (덮힘, 깃발, 드러남)
    st.session_state.revealed_board = [[' ' for _ in range(st.session_state.cols)] for _ in range(st.session_state.rows)]
    st.session_state.game_over = False
    st.session_state.win = False

# --- 게임 로직 ---

# 빈 칸을 클릭했을 때 주변의 빈 칸과 숫자를 연쇄적으로 여는 함수
def uncover(r, c):
    if not (0 <= r < st.session_state.rows and 0 <= c < st.session_state.cols):
        return
    if st.session_state.revealed_board[r][c] != ' ':
        return
    
    st.session_state.revealed_board[r][c] = 'U' # 'U'는 드러났음을 의미

    if st.session_state.board[r][c] == ' ':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                uncover(r + dr, c + dc)

# 버튼 클릭 이벤트 핸들러
def handle_click(r, c):
    if st.session_state.game_over:
        return
    
    # 깃발 모드
    if st.session_state.flag_mode:
        if st.session_state.revealed_board[r][c] == 'F':
            st.session_state.revealed_board[r][c] = ' '
        elif st.session_state.revealed_board[r][c] == ' ':
            st.session_state.revealed_board[r][c] = 'F'
    # 일반 클릭 모드
    else:
        if st.session_state.board
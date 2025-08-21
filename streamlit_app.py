import streamlit as st
import random

# --- 게임 초기화 및 상태 관리 ---

def init_game():
    # 100x100 크기로 보드 설정
    st.session_state.rows = 100
    st.session_state.cols = 100
    # 지뢰 수도 10% 비율에 맞춰 1,000개로 설정
    st.session_state.mines = 1000
    
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

def uncover(r, c):
    if not (0 <= r < st.session_state.rows and 0 <= c < st.session_state.cols):
        return
    if st.session_state.revealed_board[r][c] != ' ':
        return
    
    st.session_state.revealed_board[r][c] = 'U'

    if st.session_state.board[r][c] == ' ':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                uncover(r + dr, c + dc)

def handle_click(r, c):
    if st.session_state.game_over:
        return
    
    if st.session_state.flag_mode:
        if st.session_state.revealed_board[r][c] == 'F':
            st.session_state.revealed_board[r][c] = ' '
        elif st.session_state.revealed_board[r][c] == ' ':
            st.session_state.revealed_board[r][c] = 'F'
    else:
        if st.session_state.board[r][c] == '*':
            st.session_state.game_over = True
            st.session_state.revealed_board[r][c] = 'B'
        else:
            uncover(r, c)
            
    check_win()

def check_win():
    revealed_count = sum(row.count('U') for row in st.session_state.revealed_board)
    if revealed_count == st.session_state.rows * st.session_state.cols - st.session_state.mines:
        st.session_state.win = True
        st.session_state.game_over = True

# --- Streamlit UI 구성 ---

st.set_page_config(page_title="Streamlit 지뢰찾기", layout="wide")
st.title("streamlit 지뢰찾기 💣")

if 'game_over' not in st.session_state:
    init_game()

if st.session_state.game_over:
    if st.session_state.win:
        st.success("🎉 축하합니다! 모든 지뢰를 피하고 승리했습니다!")
    else:
        st.error("💥 지뢰를 밟았습니다! 게임 오버!")

st.session_state.flag_mode = st.checkbox("🚩 깃발 모드", False)

for r in range(st.session_state.rows):
    row_cols = st.columns(st.session_state.cols)
    for c in range(st.session_state.cols):
        with row_cols[c]:
            state = st.session_state.revealed_board[r][c]
            
            display_value = " "
            button_disabled = st.session_state.game_over or state == 'U'
            
            if state == 'F':
                display_value = "🚩"
            elif st.session_state.game_over and st.session_state.board[r][c] == '*':
                display_value = "💣"
            elif state == 'U':
                display_value = st.session_state.board[r][c]
                button_disabled = True
            
            st.button(
                display_value,
                key=f"btn_{r}_{c}",
                on_click=handle_click,
                args=(r, c),
                disabled=button_disabled
            )

st.button("🎮 다시 시작하기", on_on_click=init_game, key="restart_button")
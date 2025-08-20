import streamlit as st
import random

# --- 게임 초기화 및 상태 관리 ---
def init_game():
    st.session_state.rows = 8
    st.session_state.cols = 8
    st.session_state.mines = 10
    
    st.session_state.board, st.session_state.mines_loc = create_board(
        st.session_state.rows,
        st.session_state.cols,
        st.session_state.mines
    )
    st.session_state.revealed_board = [[' ' for _ in range(st.session_state.cols)] for _ in range(st.session_state.rows)]
    st.session_state.game_over = False
    st.session_state.win = False

def create_board(rows, cols, mines):
    board = [[' ' for _ in range(cols)] for _ in range(rows)]
    mines_loc = set()
    
    while len(mines_loc) < mines:
        r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
        if (r, c) not in mines_loc:
            mines_loc.add((r, c))
            board[r][c] = '*' 
            
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == '*':
                continue
            
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in mines_loc:
                        count += 1
            if count > 0:
                board[r][c] = str(count)
    return board, mines_loc

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
        st.success
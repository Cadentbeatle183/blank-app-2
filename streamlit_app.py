import streamlit as st
import random

# --- 게임 초기화 및 상태 관리 ---

# 세션 상태가 초기화되었는지 확인하고, 게임을 처음부터 다시 시작합니다.
def init_game():
    st.session_state.rows = 20
    st.session_state.cols = 20
    st.session_state.mines = 50  # 지뢰 개수를 50개로 설정했습니다.
    
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
        if st.session_state.board[r][c] == '*':
            st.session_state.game_over = True
            st.session_state.revealed_board[r][c] = 'B' # 'B'는 터진 지뢰를 의미
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

# 게임이 처음 실행될 때만 초기화
if 'game_over' not in st.session_state:
    init_game()

# 게임 상태 메시지
if st.session_state.game_over:
    if st.session_state.win:
        st.success("🎉 축하합니다! 모든 지뢰를 피하고 승리했습니다!")
    else:
        st.error("💥 지뢰를 밟았습니다! 게임 오버!")

# 깃발 모드 체크박스
st.session_state.flag_mode = st.checkbox("🚩 깃발 모드", False)

# 게임 보드 UI
for r in range(st.session_state.rows):
    row_cols = st.columns(st.session_state.cols)
    for c in range(st.session_state.cols):
        with row_cols[c]:
            state = st.session_state.revealed_board[r][c]
            
            display_value = ""
            button_disabled = st.session_state.game_over or state == 'U'
            
            if state == ' ': # 덮인 칸
                display_value = " "
            elif state == 'F': # 깃발
                display_value = "🚩"
            elif st.session_state.game_over and st.session_state.board[r][c] == '*':
                display_value = "💣" # 게임 오버 시 지뢰 보여주기
            else: # 드러난 칸 (숫자)
                display_value = st.session_state.board[r][c]
                button_disabled = True # 숫자는 다시 누를 수 없음
            
            st.button(
                display_value,
                key=f"btn_{r}_{c}",
                on_click=handle_click,
                args=(r, c),
                disabled=button_disabled
            )

# 다시 시작 버튼
st.button("🎮 다시 시작하기", on_click=init_game, key="restart_button")
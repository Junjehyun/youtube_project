"""
[목요일 포맷] 何個ある？ (몇 개 있을까요?)

목표: "정답 칸 딱 1개"가 아니라 "정답 값이 여러 개(3~5개) 섞여 있고,
그 개수를 맞히는" 문제를 만든다.

숫자찾기(number_find)와 다른 점:
  - 이상값이 1개가 아니라 무작위 개수(N개, 3~5개)로 등장한다.
  - "N"이 정답이 된다. 문제를 만드는 시점에 N을 정확히 몇 개로 뿌렸는지
    코드가 기억하고 있으므로, 나중에 댓글로 달리는 숫자와 실제 정답을
    정확히 비교할 수 있다 (이게 목요일 포맷을 만든 목적 — "댓글이 숫자로
    나오는지 확인").
  - 타이틀에 정답 개수를 공개하지 않는다.
"""

import random

from PIL import ImageFont

from render_common import (
    new_canvas,
    draw_banner,
    draw_centered_text,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    BANNER_HEIGHT,
    FONT_PATH,
    GRID_TEXT_COLOR,
)

MIN_COUNT = 3   # 정답 개수의 최소값
MAX_COUNT = 5   # 정답 개수의 최대값


def generate_count_how_many_puzzle(rows: int = 13, cols: int = 8) -> dict:
    """
    개수세기 문제 하나를 무작위로 생성한다.

    Returns:
        {
            "format": "count_how_many",
            "rows": 13, "cols": 8,
            "base_value": 175,          # 대부분의 칸에 들어갈 값
            "target_value": 174,        # 여러 번 섞여 들어갈 "다른" 값
            "target_positions": [[3, 5], [7, 1], [10, 6]],  # 정답 값이 들어갈 칸들
            "count": 3,                 # target_positions의 개수 = 정답
        }
    """
    base_value = random.randint(100, 999)
    target_value = base_value - 1

    # 격자 안의 모든 칸 좌표 (row, col) 목록을 만든다.
    all_positions = [(r, c) for r in range(rows) for c in range(cols)]

    # 이번 문제의 정답 개수를 3~5개 중에서 무작위로 정한다.
    count = random.randint(MIN_COUNT, MAX_COUNT)

    # random.sample(목록, 개수) : 목록에서 "겹치지 않게" count개를 무작위로 뽑는다.
    # (겹치지 않아야 "정답 칸이 3개"라고 했을 때 실제로 서로 다른 3칸이 된다)
    target_positions = random.sample(all_positions, count)

    return {
        "format": "count_how_many",
        "rows": rows,
        "cols": cols,
        "base_value": base_value,
        "target_value": target_value,
        # JSON으로 저장할 때 튜플은 리스트로 바뀌므로, 여기서도 리스트로 통일해둔다.
        "target_positions": [list(pos) for pos in target_positions],
        "count": count,
    }


def render_count_grid(puzzle: dict):
    """문제 데이터를 받아 개수세기 격자 이미지를 그린다."""
    rows = puzzle["rows"]
    cols = puzzle["cols"]
    base_value = puzzle["base_value"]
    target_value = puzzle["target_value"]

    # 빠르게 "이 칸이 정답 칸인가?"를 확인하기 위해 리스트를 set으로 바꿔둔다.
    # (칸 개수가 100개 안팎이라 리스트로 해도 상관없지만, set이 더 명확하다)
    target_positions = {tuple(pos) for pos in puzzle["target_positions"]}

    img, draw = new_canvas()

    # 일본 채널 대상이라 화면 문구는 전부 일본어로 넣는다.
    # 정답 개수(N)를 타이틀에 절대 공개하지 않는다 (댓글로 맞혀보게 하는 게 목적).
    draw_banner(
        draw,
        title_text=f"{target_value}は何個ある？",          # "174는 몇 개 있을까요?"
        subtitle_lines=[
            "数えたら",                                    # "다 세었다면"
            "コメントで教えてください！",                    # "댓글로 알려주세요!"
        ],
    )

    grid_font = ImageFont.truetype(FONT_PATH, 50)
    grid_top = BANNER_HEIGHT + 40
    grid_bottom = CANVAS_HEIGHT - 40
    cell_width = CANVAS_WIDTH / cols
    cell_height = (grid_bottom - grid_top) / rows

    for row in range(rows):
        for col in range(cols):
            # 숫자찾기는 "정답 칸이 정확히 1개"였지만, 여기서는 정답 칸 집합
            # (target_positions) 안에 (row, col)이 들어있는지로 판단한다.
            if (row, col) in target_positions:
                value = target_value
            else:
                value = base_value

            cell_center_x = int(cell_width * col + cell_width / 2)
            cell_center_y = int(grid_top + cell_height * row + cell_height / 2)

            draw_centered_text(
                draw, str(value), grid_font, GRID_TEXT_COLOR,
                center_x=cell_center_x, center_y=cell_center_y,
            )

    return img


# "python src/count_how_many.py"로 이 파일만 직접 실행했을 때 동작하는 테스트 코드.
if __name__ == "__main__":
    puzzle = generate_count_how_many_puzzle()
    print("생성된 문제:", puzzle)
    print("정답(개수):", puzzle["count"])

    img = render_count_grid(puzzle)
    img.save("output/test_count_grid.png")
    print("저장 완료: output/test_count_grid.png")

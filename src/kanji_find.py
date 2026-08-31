"""
[화요일 포맷] 한자 하나 찾기 (未/末 등)

목표: 격자를 거의 똑같이 생긴 한자로 채우고, 딱 한 칸만 아주 비슷하게
생긴 "다른 한자"로 바꿔서 시청자가 찾아보게 만드는 문제.

숫자찾기(puzzle_generator.py + render_image.py)와 다른 점:
  1) 격자에 들어가는 값이 숫자가 아니라 한자 1글자.
     data/kanji_pairs.json에 미리 등록해둔 "헷갈리기 쉬운 한자 쌍"
     (未/末, 土/士 처럼 획 하나 차이로 비슷하게 생긴 것들) 중 하나를
     무작위로 골라 기본값/정답으로 쓴다.
  2) 화면(타이틀)에 정답을 공개하지 않는다. 화요일은 "댓글 테스트"가
     목적이므로, 정답을 맞혔으면 댓글에 남겨달라고 유도하는 문구를 넣는다.
"""

import json
import os
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

# 이 파일 기준이 아니라 "프로젝트 루트에서 실행한다"는 프로젝트 규칙에 맞춰
# 상대 경로를 그대로 쓴다 (pipeline.py의 LOG_PATH 등과 동일한 방식).
KANJI_PAIRS_PATH = os.path.join("data", "kanji_pairs.json")


def _load_kanji_pairs() -> list:
    """data/kanji_pairs.json을 읽어서 [["未", "末"], ["土", "士"], ...] 형태로 돌려준다."""
    with open(KANJI_PAIRS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_kanji_find_puzzle(rows: int = 11, cols: int = 7) -> dict:
    """
    한자찾기 문제 하나를 무작위로 생성한다.

    puzzle_generator.generate_number_find_puzzle()과 구조가 거의 같다.
    다른 점은 base_value/target_value가 숫자가 아니라 한자 1글자라는 것뿐이다.
    이렇게 구조를 맞춰두면 render_video.py의 build_video() 등 다른 코드를
    그대로 재사용할 수 있다.

    Args:
        rows: 격자의 세로 칸 수. 한자는 숫자(3자리)보다 획이 복잡해서
              숫자찾기(13줄)보다 살짝 적은 11줄을 기본값으로 뒀다.
        cols: 격자의 가로 칸 수

    Returns:
        {
            "format": "kanji_find",
            "rows": 11, "cols": 7,
            "base_value": "未",     # 대부분의 칸에 들어갈 한자
            "target_value": "末",   # 딱 한 칸에만 들어갈 "다른" 한자 (=정답)
            "target_row": 3,
            "target_col": 5,
        }
    """
    pairs = _load_kanji_pairs()
    pair = random.choice(pairs)  # 예: ["未", "末"]

    # random.sample(pair, 2)는 리스트 안의 원소 2개를 순서까지 섞어서 뽑아준다.
    # 이렇게 하면 "未가 기본값이고 末이 정답"일 때도, 반대일 때도 둘 다 나온다.
    base_value, target_value = random.sample(pair, 2)

    target_row = random.randint(0, rows - 1)
    target_col = random.randint(0, cols - 1)

    return {
        "format": "kanji_find",
        "rows": rows,
        "cols": cols,
        "base_value": base_value,
        "target_value": target_value,
        "target_row": target_row,
        "target_col": target_col,
    }


def render_kanji_grid(puzzle: dict):
    """
    문제 데이터를 받아 한자 격자 이미지를 그린다.
    render_image.py의 render_number_grid()와 구조가 거의 동일하지만,
    타이틀에 정답을 공개하지 않는다는 점이 다르다.
    """
    rows = puzzle["rows"]
    cols = puzzle["cols"]
    base_value = puzzle["base_value"]
    target_value = puzzle["target_value"]
    target_row = puzzle["target_row"]
    target_col = puzzle["target_col"]

    img, draw = new_canvas()

    # 일본 채널 대상이라 화면 문구는 전부 일본어로 넣는다.
    # 정답 한자를 타이틀에 절대 넣지 않는다 (댓글 유도가 목적이므로).
    draw_banner(
        draw,
        title_text="違う漢字を探せ！",                     # "다른 한자를 찾아라!"
        subtitle_lines=[
            "10秒以内に見つけたら",                         # "10초 안에 찾았다면"
            "コメントで教えてください！",                    # "댓글로 알려주세요!"
        ],
    )

    # 한자는 숫자(2~3글자)보다 한 글자라 조금 더 크게 그려야 잘 보인다.
    grid_font = ImageFont.truetype(FONT_PATH, 58)
    grid_top = BANNER_HEIGHT + 40
    grid_bottom = CANVAS_HEIGHT - 40
    cell_width = CANVAS_WIDTH / cols
    cell_height = (grid_bottom - grid_top) / rows

    for row in range(rows):
        for col in range(cols):
            if row == target_row and col == target_col:
                value = target_value
            else:
                value = base_value

            cell_center_x = int(cell_width * col + cell_width / 2)
            cell_center_y = int(grid_top + cell_height * row + cell_height / 2)

            draw_centered_text(
                draw, value, grid_font, GRID_TEXT_COLOR,
                center_x=cell_center_x, center_y=cell_center_y,
            )

    return img


# "python src/kanji_find.py"로 이 파일만 직접 실행했을 때 동작하는 테스트 코드.
if __name__ == "__main__":
    puzzle = generate_kanji_find_puzzle()
    print("생성된 문제:", puzzle)

    img = render_kanji_grid(puzzle)
    img.save("output/test_kanji_grid.png")
    print("저장 완료: output/test_kanji_grid.png")

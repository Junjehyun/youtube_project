"""
[Phase 2 / 월·수·금 포맷] 숫자찾기 이미지 렌더러

목표: puzzle_generator.py가 만든 "문제 데이터(딕셔너리)"를 받아서,
실제로 눈에 보이는 1080×1920 세로 이미지(쇼츠 규격)를 그린다.

전체적으로 이런 구조로 그려진다 (레퍼런스 영상과 동일한 레이아웃):
  ┌────────────────────────────┐
  │   (검정 배경)                │
  │   숨은 174를 찾아라! (타이틀) │  ← 배너 영역 (화면 위쪽)
  │   10초 이내에 찾으면...      │
  │   당신의 뇌는 젊습니다!      │
  ├────────────────────────────┤
  │  175 175 175 175 175 175   │
  │  175 175 174 175 175 175   │  ← 숫자 격자 영역 (화면 아래쪽)
  │  175 175 175 175 175 175   │
  │        ...                 │
  └────────────────────────────┘

캔버스 크기/색상/배너 그리기 같은 "여러 포맷이 공통으로 쓰는 부분"은
render_common.py로 분리되어 있다. 이 파일은 그중 "숫자 격자를 채우는 방식"만
따로 담당한다.
"""

from PIL import Image, ImageFont

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


def render_number_grid(puzzle: dict) -> Image.Image:
    """
    문제 데이터를 받아 완성된 PIL 이미지를 반환한다.

    이 함수는 아직 파일로 저장하지 않는다. 이미지 객체만 돌려주고,
    저장은 이 함수를 부르는 쪽(pipeline.py)에서 img.save(...)로 한다.

    Args:
        puzzle: generate_number_find_puzzle()이 만든 딕셔너리

    Returns:
        PIL.Image.Image 객체
    """
    rows = puzzle["rows"]
    cols = puzzle["cols"]
    base_value = puzzle["base_value"]
    target_value = puzzle["target_value"]
    target_row = puzzle["target_row"]
    target_col = puzzle["target_col"]

    img, draw = new_canvas()

    # 일본 채널 대상이라 화면 문구는 전부 일본어로 넣는다.
    # 타이틀에 정답(target_value)을 그대로 공개한다.
    # (월·수·금 포맷은 "찾아보세요" 재미가 핵심이지, 댓글 유도가 목적이 아니기 때문)
    draw_banner(
        draw,
        title_text=f"隠れた{target_value}を探せ！",       # "숨은 174를 찾아라!"
        subtitle_lines=[
            "10秒以内に見つければ",                        # "10초 이내에 찾으면"
            "あなたの脳は若いです！",                        # "당신의 뇌는 젊습니다!"
        ],
    )

    # 숫자 격자 그리기.
    # 배너 아래부터 화면 끝까지의 공간을 rows x cols 칸으로 나눠서,
    # 각 칸의 정중앙에 숫자를 하나씩 그린다.
    grid_font = ImageFont.truetype(FONT_PATH, 50)
    grid_top = BANNER_HEIGHT + 40      # 배너 아래 여백
    grid_bottom = CANVAS_HEIGHT - 40   # 화면 맨 아래 여백
    cell_width = CANVAS_WIDTH / cols
    cell_height = (grid_bottom - grid_top) / rows

    for row in range(rows):
        for col in range(cols):
            # 지금 그리는 칸이 정답 칸(target_row, target_col)이면 target_value를,
            # 아니면 base_value를 넣는다. 이게 이 함수에서 가장 중요한 규칙이다.
            if row == target_row and col == target_col:
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


# "python src/render_image.py"로 이 파일만 직접 실행했을 때 동작하는 테스트 코드.
if __name__ == "__main__":
    from puzzle_generator import generate_number_find_puzzle

    puzzle = generate_number_find_puzzle()
    print("생성된 문제:", puzzle)

    img = render_number_grid(puzzle)
    img.save("output/test_grid.png")
    print("저장 완료: output/test_grid.png")

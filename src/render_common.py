"""
[공통 모듈] 여러 포맷이 함께 쓰는 캔버스/색상/폰트 설정과, 텍스트를
가운데 정렬로 그리는 도우미 함수를 모아둔 파일.

처음에는 render_image.py 한 파일 안에 숫자찾기용으로만 이 내용이 있었는데,
화(한자찾기)/목(개수세기)/토(2단퀴즈) 포맷이 추가되면서 4개 파일이 전부
"1080x1920 캔버스를 만들고, 검정 배너를 그리고, 텍스트를 가운데 정렬해서
그리는" 같은 코드를 반복해서 가지게 됐다. 그래서 그 공통 부분만 이 파일
하나로 모아두고, 각 포맷 파일은 여기서 필요한 것만 가져다 쓴다.
"""

from PIL import Image, ImageDraw, ImageFont

# 이 채널은 일본 시청자를 대상으로 하기 때문에, 화면에 들어가는 문구는
# 전부 일본어다 (히라가나/가타카나/한자 모두 사용). macOS 기본 한국어
# 폰트(AppleSDGothicNeo)는 脳/教/内 같은 흔한 한자도 깨져서(네모 박스) 나와서
# 못 쓰고, 대신 이 Mac에 이미 들어있는 중국어(간체)용 폰트를 대신 쓴다.
# 이 폰트가 일본어 문장 전체(한자+히라가나+가타카나+전각 기호)를 깨짐 없이
# 그려주는 것을 직접 확인했다.
# 나중에 "설정 > 언어 및 지역"에서 일본어를 추가하면 진짜 일본어 폰트
# (히라기노 카쿠고딕 등)가 설치되는데, 그때는 이 경로만 그 폰트로 바꾸면
# 더 자연스러운 일본어 글꼴로 바뀐다.
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# 화면 크기: 유튜브 쇼츠 표준 세로 비율(9:16)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920

# 색상은 (R, G, B) 형태, 각 값은 0~255.
BG_COLOR = (246, 242, 234)         # 격자 영역 배경색 (연한 베이지)
BANNER_COLOR = (10, 10, 10)        # 상단 배너 배경색 (거의 검정)
TITLE_COLOR = (255, 214, 0)        # 타이틀 글자색 (네온 느낌의 노란색)
SUBTITLE_COLOR = (225, 225, 225)   # 서브텍스트 글자색 (밝은 회색)
GRID_TEXT_COLOR = (35, 35, 35)     # 격자 안 글자색 (진한 회색)

BANNER_HEIGHT = 460  # 상단 검정 배너가 차지하는 높이(px). 그 아래는 격자 영역.


def new_canvas() -> tuple:
    """
    빈 캔버스(도화지)와, 그 위에 그림을 그릴 도구(draw)를 함께 만들어 돌려준다.
    모든 포맷의 렌더링 함수는 이 함수로 시작한다.

    Returns:
        (img, draw) 튜플. img는 나중에 파일로 저장할 이미지 객체,
        draw는 그 위에 사각형/글자를 그릴 때 쓰는 도구.
    """
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_centered_text(draw, text, font, fill, center_x, center_y) -> None:
    """
    텍스트를 (center_x, center_y) 지점에 "가운데 정렬"로 그려주는 도우미 함수.

    Pillow의 draw.text(...)는 기본적으로 텍스트의 "왼쪽 위 모서리" 좌표를
    기준으로 그리기 때문에, 그냥 쓰면 글자들이 칸 중앙이 아니라 삐뚤빼뚤하게
    찍힌다. 그래서 먼저 글자의 실제 가로/세로 크기를 재본 뒤(textbbox),
    그 절반만큼 왼쪽·위로 이동시켜서 정중앙에 오도록 보정한다.
    """
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top

    x = center_x - text_width // 2
    y = center_y - text_height // 2

    draw.text((x, y), text, font=font, fill=fill)


def draw_banner(draw, title_text: str, subtitle_lines: list,
                 title_font_size: int = 64, subtitle_font_size: int = 42) -> None:
    """
    화면 상단의 검정 배너 + 타이틀 한 줄 + 서브텍스트 여러 줄을 그린다.

    Args:
        draw: new_canvas()로 만든 draw 도구
        title_text: 배너 상단에 크게 나올 제목 (예: "숨은 174를 찾아라!")
        subtitle_lines: 제목 아래에 작게 나올 문구들. 리스트에 담긴 순서대로
                        한 줄씩 세로로 나열해서 그린다.
                        예: ["10초 안에 찾았다면", "댓글에 정답을 남겨주세요!"]
    """
    draw.rectangle([(0, 0), (CANVAS_WIDTH, BANNER_HEIGHT)], fill=BANNER_COLOR)

    title_font = ImageFont.truetype(FONT_PATH, title_font_size)
    draw_centered_text(
        draw, title_text, title_font, TITLE_COLOR,
        center_x=CANVAS_WIDTH // 2, center_y=150,
    )

    subtitle_font = ImageFont.truetype(FONT_PATH, subtitle_font_size)
    start_y = 270
    line_gap = 65  # 서브텍스트 줄 사이 간격(px)
    for i, line in enumerate(subtitle_lines):
        draw_centered_text(
            draw, line, subtitle_font, SUBTITLE_COLOR,
            center_x=CANVAS_WIDTH // 2, center_y=start_y + i * line_gap,
        )

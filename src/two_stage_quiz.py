"""
[토요일 포맷] 2단 퀴즈 15초

목표: 문제 2개를 한 영상 안에 순서대로 이어붙여서, 시청자가 첫 번째
문제를 풀고 나서도 "두 번째 문제도 있네?" 하고 끝까지 보게 만드는 포맷.
목적이 "시청시간(retention) 테스트"이기 때문에, 문제 자체의 난이도보다
"두 번째 문제까지 이탈 없이 보게 만드는 것"이 더 중요하다.

숫자찾기(number_find)와 다른 점:
  - 문제 데이터를 2세트 만든다 (1번 문제 + 2번 문제).
    문제 생성 로직 자체는 새로 만들 필요 없이, 이미 검증된
    generate_number_find_puzzle()을 그대로 두 번 불러서 재사용한다.
  - 이미지도 2장 그려서, 각각 화면 오른쪽 위에 "1번 문제"/"2번 문제" 표시를
    작게 덧붙인다 (몇 번째 문제인지 알려줘서 "다음 문제 있음"을 예고).
  - 영상 합성 단계(render_video.py)에서 두 이미지를 순서대로 이어붙여
    (concatenate) 15초짜리 영상 하나로 만든다. 이 부분만 render_video.py에
    build_two_stage_video()라는 새 함수로 추가했다.
"""

from PIL import ImageDraw, ImageFont

from puzzle_generator import generate_number_find_puzzle
from render_image import render_number_grid
from render_common import FONT_PATH, CANVAS_WIDTH

# 전체 15초를 1번 문제/2번 문제에 어떻게 나눌지.
# 1번 문제를 살짝 더 길게 둬서 여유 있게 풀게 하고, 2번 문제는 조금 짧게
# 둬서 "이제 곧 끝난다"는 긴장감으로 끝까지 보게 만든다. (8 + 7 = 15초)
STAGE_1_DURATION_SEC = 8
STAGE_2_DURATION_SEC = 7


def generate_two_stage_quiz_puzzle() -> dict:
    """
    2단 퀴즈용 문제 데이터를 생성한다. 서로 다른 숫자찾기 문제 2개를 담는다.

    Returns:
        {
            "format": "two_stage_quiz",
            "stage_1": {...숫자찾기 문제 딕셔너리...},
            "stage_2": {...숫자찾기 문제 딕셔너리...},
            "stage_1_duration_sec": 8,
            "stage_2_duration_sec": 7,
        }
    """
    return {
        "format": "two_stage_quiz",
        "stage_1": generate_number_find_puzzle(),
        "stage_2": generate_number_find_puzzle(),
        "stage_1_duration_sec": STAGE_1_DURATION_SEC,
        "stage_2_duration_sec": STAGE_2_DURATION_SEC,
    }


def render_two_stage_images(puzzle: dict) -> list:
    """
    2개의 문제를 각각 이미지로 그리고, "몇 번째 문제인지" 라벨을 덧붙인 뒤
    이미지 2장을 리스트로 돌려준다. (순서: [1번 문제 이미지, 2번 문제 이미지])
    """
    # 일본 채널 대상이라 라벨도 일본어로 넣는다.
    img1 = render_number_grid(puzzle["stage_1"])
    _stamp_stage_label(img1, "問題1")                 # "1번 문제"

    img2 = render_number_grid(puzzle["stage_2"])
    _stamp_stage_label(img2, "問題2（ラスト！）")        # "2번 문제 (마지막!)"

    return [img1, img2]


def _stamp_stage_label(img, text: str) -> None:
    """
    이미 다 그려진 이미지 위, 오른쪽 위 구석에 작은 라벨 글자를 덧그린다.
    render_number_grid()가 그려준 그림은 그대로 두고 그 "위에 얹기만" 하는
    방식이라, 숫자찾기 렌더링 코드를 전혀 건드리지 않고도 라벨을 추가할 수 있다.
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 32)
    draw.text((CANVAS_WIDTH - 240, 20), text, font=font, fill=(255, 255, 255))


# "python src/two_stage_quiz.py"로 이 파일만 직접 실행했을 때 동작하는 테스트 코드.
if __name__ == "__main__":
    from render_video import build_two_stage_video

    puzzle = generate_two_stage_quiz_puzzle()
    print("생성된 문제:", puzzle)

    img1, img2 = render_two_stage_images(puzzle)
    img1.save("output/test_stage1.png")
    img2.save("output/test_stage2.png")
    print("이미지 저장 완료: output/test_stage1.png, output/test_stage2.png")

    build_two_stage_video(
        image_paths=["output/test_stage1.png", "output/test_stage2.png"],
        durations=[puzzle["stage_1_duration_sec"], puzzle["stage_2_duration_sec"]],
        audio_path="assets/bgm/tension.mp3",
        out_path="output/test_two_stage.mp4",
    )
    print("저장 완료: output/test_two_stage.mp4")

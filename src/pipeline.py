"""
[Phase 4~6] 총괄 지휘자

문제 생성 → 이미지 렌더링 → 영상 합성을 순서대로 실행해서, 명령어 한 줄로
mp4 영상 하나를 완성해주는 스크립트. 지금은 4개 포맷을 모두 지원한다.

| 요일    | 포맷              | 담당 파일                  |
|---------|-------------------|----------------------------|
| 월·수·금 | number_find       | puzzle_generator.py + render_image.py |
| 화      | kanji_find        | kanji_find.py               |
| 목      | count_how_many    | count_how_many.py           |
| 토      | two_stage_quiz    | two_stage_quiz.py (영상 2장 이어붙이기) |

오늘이 무슨 요일인지는 data/calendar.json을 보고 자동으로 정한다.
어떤 포맷을 쓸지 직접 지정하고 싶으면 --format 옵션을 쓰면 된다.

실행 방법 (반드시 프로젝트 루트 폴더에서, 가상환경을 켠 상태로):
    cd "/Users/jun_jehyun/Desktop/JJH/01.Project/04.youtube_project"
    source .venv/bin/activate

    python src/pipeline.py                       # 오늘 요일에 맞는 포맷 자동 실행
    python src/pipeline.py --format kanji_find    # 포맷을 직접 지정해서 실행
    python src/pipeline.py --date 260901          # 다른 날짜(요일)로 테스트
"""

import argparse
import json
import os
from datetime import date, datetime

from puzzle_generator import generate_number_find_puzzle
from render_image import render_number_grid
from render_video import build_video, build_two_stage_video

from kanji_find import generate_kanji_find_puzzle, render_kanji_grid
from count_how_many import generate_count_how_many_puzzle, render_count_grid
from two_stage_quiz import generate_two_stage_quiz_puzzle, render_two_stage_images

# 이 파일 전체에서 반복해서 쓰는 값들은 위에 상수로 모아둔다.
OUTPUT_DIR = "output"
LOG_PATH = "data/log.json"
CALENDAR_PATH = "data/calendar.json"
BGM_PATH = "assets/bgm/tension.mp3"
DEFAULT_DURATION_SEC = 10

# date.weekday()는 월요일을 0, 일요일을 6으로 돌려준다. 그 순서와 맞춘 이름표.
WEEKDAY_NAMES = [
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
]


def run(date_str: str = None, format_name: str = None) -> str:
    """
    영상 하나를 처음부터 끝까지 자동으로 생성한다.

    Args:
        date_str: 파일 이름에 쓸 날짜 문자열 (예: "260901", YYMMDD 형식).
                  지정하지 않으면 오늘 날짜를 자동으로 사용한다.
        format_name: "number_find" / "kanji_find" / "count_how_many" /
                     "two_stage_quiz" 중 하나. 지정하지 않으면
                     data/calendar.json에서 오늘 요일에 맞는 포맷을 찾아 쓴다.

    Returns:
        생성된 mp4 파일 경로
    """
    if date_str is None:
        target_date = date.today()
        date_str = target_date.strftime("%y%m%d")
    else:
        target_date = _parse_date_str(date_str)

    if format_name is None:
        format_name = _pick_format_by_weekday(target_date)

    print(f"날짜: {date_str} / 포맷: {format_name}")

    if format_name == "number_find":
        video_path = _run_single_image_format(
            date_str, generate_number_find_puzzle, render_number_grid,
        )
    elif format_name == "kanji_find":
        video_path = _run_single_image_format(
            date_str, generate_kanji_find_puzzle, render_kanji_grid,
        )
    elif format_name == "count_how_many":
        video_path = _run_single_image_format(
            date_str, generate_count_how_many_puzzle, render_count_grid,
        )
    elif format_name == "two_stage_quiz":
        video_path = _run_two_stage_format(date_str)
    else:
        raise ValueError(f"알 수 없는 포맷입니다: {format_name}")

    print(f"\n완료: {video_path}")
    return video_path


def _pick_format_by_weekday(target_date) -> str:
    """data/calendar.json을 보고 target_date의 요일에 맞는 포맷 이름을 찾는다."""
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        calendar = json.load(f)

    weekday_name = WEEKDAY_NAMES[target_date.weekday()]
    format_name = calendar.get(weekday_name)

    if format_name is None:
        raise ValueError(
            f"'{weekday_name}'에 대한 포맷이 data/calendar.json에 지정되어 있지 않습니다. "
            f"(예: 일요일은 아직 정해지지 않음) --format 옵션으로 직접 지정해서 실행해보세요."
        )
    return format_name


def _parse_date_str(date_str: str):
    """'260901' 같은 문자열을 실제 날짜(date) 객체로 바꾼다. 요일을 알아내기 위해 필요하다."""
    return datetime.strptime(date_str, "%y%m%d").date()


def _run_single_image_format(date_str: str, generate_fn, render_fn) -> str:
    """
    이미지 1장짜리 포맷(number_find / kanji_find / count_how_many) 공통 처리.

    Args:
        generate_fn: 문제 데이터를 만드는 함수 (인자 없이 호출 가능해야 함)
        render_fn: 문제 데이터를 받아 PIL 이미지를 돌려주는 함수
    """
    # 1) 문제 데이터 생성
    puzzle = generate_fn()
    print("[1/3] 문제 생성 완료:", puzzle)

    # 2) 이미지 렌더링
    img = render_fn(puzzle)
    img_path = os.path.join(OUTPUT_DIR, f"{date_str}_temp.png")
    img.save(img_path)
    print(f"[2/3] 이미지 저장 완료: {img_path}")

    # 3) 영상 합성
    video_path = os.path.join(OUTPUT_DIR, f"{date_str}.mp4")
    build_video(
        image_path=img_path,
        audio_path=BGM_PATH,
        duration_sec=DEFAULT_DURATION_SEC,
        out_path=video_path,
    )
    print(f"[3/3] 영상 저장 완료: {video_path}")

    save_log(date_str, puzzle)
    return video_path


def _run_two_stage_format(date_str: str) -> str:
    """토요일 2단 퀴즈 포맷 전용 처리 (이미지 2장 → 영상 2개 이어붙이기)."""
    # 1) 문제 데이터 생성 (1번 문제 + 2번 문제)
    puzzle = generate_two_stage_quiz_puzzle()
    print("[1/3] 문제 생성 완료:", puzzle)

    # 2) 이미지 2장 렌더링
    img1, img2 = render_two_stage_images(puzzle)
    img1_path = os.path.join(OUTPUT_DIR, f"{date_str}_stage1_temp.png")
    img2_path = os.path.join(OUTPUT_DIR, f"{date_str}_stage2_temp.png")
    img1.save(img1_path)
    img2.save(img2_path)
    print(f"[2/3] 이미지 저장 완료: {img1_path}, {img2_path}")

    # 3) 두 이미지를 이어붙여서 영상 합성
    video_path = os.path.join(OUTPUT_DIR, f"{date_str}.mp4")
    build_two_stage_video(
        image_paths=[img1_path, img2_path],
        durations=[puzzle["stage_1_duration_sec"], puzzle["stage_2_duration_sec"]],
        audio_path=BGM_PATH,
        out_path=video_path,
    )
    print(f"[3/3] 영상 저장 완료: {video_path}")

    save_log(date_str, puzzle)
    return video_path


def save_log(date_str: str, puzzle: dict) -> None:
    """
    문제 생성 기록을 data/log.json 파일에 차곡차곡 쌓아서 저장한다.

    동작 방식:
      1) data/log.json 파일이 이미 있으면 그 내용을 읽어와서(logs) 이어붙인다.
      2) 없으면 빈 리스트에서 새로 시작한다.
      3) 마지막에 오늘 기록을 추가한 전체 목록을 다시 파일에 덮어쓴다.
    """
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    # {"date": date_str, **puzzle} : puzzle 딕셔너리의 내용을 그대로 펼치면서
    # 맨 앞에 "date" 항목만 하나 추가하는 문법이다.
    logs.append({"date": date_str, **puzzle})

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        # ensure_ascii=False : 한글/한자가 코드로 저장되지 않고 그대로 저장되게 한다.
        # indent=2           : 사람이 읽기 편하게 줄바꿈/들여쓰기를 넣는다.
        json.dump(logs, f, ensure_ascii=False, indent=2)


def _parse_args():
    """터미널에서 --format, --date 같은 옵션을 받을 수 있게 해주는 함수."""
    parser = argparse.ArgumentParser(description="숏츠 영상 자동 생성 파이프라인")
    parser.add_argument(
        "--format", dest="format_name", default=None,
        help=(
            "강제로 지정할 포맷 (number_find / kanji_find / count_how_many / "
            "two_stage_quiz). 지정하지 않으면 오늘 요일에 맞는 포맷을 "
            "data/calendar.json에서 자동으로 고른다."
        ),
    )
    parser.add_argument(
        "--date", dest="date_str", default=None,
        help="YYMMDD 형식의 날짜 (예: 260902). 다른 요일로 테스트할 때 사용.",
    )
    return parser.parse_args()


# 파이썬 파일에서 아주 자주 보게 될 관용구.
# "python src/pipeline.py"처럼 이 파일을 직접 실행했을 때만 실행된다.
if __name__ == "__main__":
    args = _parse_args()
    run(date_str=args.date_str, format_name=args.format_name)

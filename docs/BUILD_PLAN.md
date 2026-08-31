# 구현 설계도 (초안 → 완성)

`WORKFLOW.md`가 "왜/무엇을" 다룬 문서라면, 이 문서는 "어떤 순서로, 어떤 파일에, 어떤 코드를" 만들지를 다룬다. 코딩을 전혀 몰라도 따라올 수 있도록 각 단계마다 비유와 예시를 넣었다.

---

## 0. 큰 그림: 우리가 만드는 건 "숫자 찍는 기계"

전체 파이프라인을 한 문장으로 요약하면:

> 매일 아침, "오늘은 무슨 요일이니까 어떤 문제를 낼지" 자동으로 정하고 → 문제를 랜덤하게 만들고 → 그 문제를 이미지로 그리고 → 소리를 붙이고 → mp4로 완성해서 → 정해진 폴더에 던져놓는 것.

공장 조립 라인처럼 생각하면 쉽다:

```
재료 투입              가공 1              가공 2              가공 3            포장
(오늘 날짜)  →  (문제 데이터 생성)  →  (이미지 그리기)  →  (영상+소리 합성)  →  (mp4 저장)
```

각 "가공 단계"가 파이썬 파일 하나씩이 된다. 그래서 처음부터 5개 파일을 한번에 만드는 게 아니라, **조립 라인의 앞부분부터 하나씩 완성하고 눈으로 확인하면서 다음 단계로 넘어간다.**

---

## 1. 완성됐을 때의 최종 파일 구조

```
04.youtube_project/
├── src/
│   ├── puzzle_generator.py   # [1단계] 숫자찾기 문제 데이터를 만드는 코드 (월·수·금)
│   ├── render_common.py      # [6단계] 모든 포맷이 공통으로 쓰는 캔버스/배너/텍스트 도우미
│   ├── render_image.py       # [2단계] 숫자찾기 이미지(png)를 그리는 코드 (월·수·금)
│   ├── kanji_find.py         # [6단계] 한자찾기 문제 생성+그리기 (화)
│   ├── count_how_many.py     # [6단계] 개수세기 문제 생성+그리기 (목)
│   ├── two_stage_quiz.py     # [6단계] 2단 퀴즈 문제 생성+그리기 (토)
│   ├── render_video.py       # [3단계] 그림+소리를 영상(mp4)으로 합치는 코드 (2단퀴즈용 이어붙이기 포함)
│   ├── pipeline.py           # [4~6단계] 요일 판단 + 4개 포맷을 모두 실행하는 "총괄 지휘자"
│   └── check_setup.py        # (이미 완성됨) 환경 점검용
├── data/
│   ├── calendar.json         # [5단계] 요일 → 어떤 포맷을 쓸지 매핑표
│   ├── kanji_pairs.json      # [6단계] 화요일용 헷갈리는 한자 쌍 데이터
│   └── log.json              # "언제 무슨 문제/정답으로 영상을 만들었는지" 기록장 (실행하면 자동 생성)
├── assets/{fonts,bgm,sfx}/
└── output/YYMMDD.mp4
```

(애초 계획에는 포맷별 파일을 `src/formats/` 서브폴더에 넣는 안이 있었지만, 파일이 4개뿐이라 폴더를 나누는 대신 기존 파일들과 같은 위치에 평평하게 두는 쪽으로 단순화했다 — Phase 6 참고)

Phase 1~6까지 전부 구현 완료된 상태. 아래는 그 과정을 순서대로 설명한다.

---

## 2. 데이터가 어떻게 흘러가는지 (제일 중요한 개념)

이 파이프라인의 핵심은 **"문제 데이터"를 먼저 순수한 정보(딕셔너리/JSON)로 확정한 뒤, 그 정보를 가지고 그림을 그리고, 그 그림을 가지고 영상을 만든다**는 것이다. 이렇게 하면:

- 정답이 코드 단계에서 100% 확정되므로 지난번 `387` 같은 이상값 버그가 원천적으로 생기지 않는다.
- 나중에 화면 디자인만 바꾸고 싶을 때, 문제 생성 코드는 안 건드리고 그림 그리는 코드만 고치면 된다.

월·수·금(숫자찾기) 기준으로 실제 데이터 예시:

```json
{
  "date": "2026-09-01",
  "format": "number_find",
  "rows": 13,
  "cols": 8,
  "base_value": 175,
  "target_value": 174,
  "target_row": 0,
  "target_col": 5,
  "title": "숨은 174를 찾아라!",
  "subtitle": "10초 이내에 찾으면 당신의 뇌는 젊습니다!",
  "duration_sec": 10
}
```

이 JSON 하나가 있으면 → 이미지도 그릴 수 있고 → 영상도 만들 수 있고 → 나중에 "그날 정답이 뭐였지?"도 바로 확인 가능하다.

---

## 3. 단계별 구현 순서 (Phase)

각 Phase는 "무엇을 만들지 → 어떻게 만들지 → 다 됐는지 확인하는 방법"으로 구성했다. 순서대로만 따라가면 된다.

### Phase 1 — 문제 데이터 생성기 (`src/puzzle_generator.py`) ✅ 구현 완료

**목표**: "175로 가득 찬 격자 중 한 칸만 174로 다른" 문제를 코드로 만든다.

**최종 코드** (실제로 `src/puzzle_generator.py`에 들어 있는 코드, 주석은 파일에서 더 자세히 볼 수 있음):
```python
import random

def generate_number_find_puzzle(rows: int = 13, cols: int = 8) -> dict:
    base_value = random.randint(100, 999)   # 예: 175
    target_value = base_value - 1           # 예: 174 (한 끗 다르게)
    target_row = random.randint(0, rows - 1)
    target_col = random.randint(0, cols - 1)
    return {
        "format": "number_find",
        "rows": rows, "cols": cols,
        "base_value": base_value,
        "target_value": target_value,
        "target_row": target_row,
        "target_col": target_col,
    }

if __name__ == "__main__":
    puzzle = generate_number_find_puzzle()
    print("생성된 문제:", puzzle)
```

**왜 이렇게 하나?**: 이상값(target)이 딱 하나만 존재한다는 걸 코드가 "구조적으로" 보장한다. 격자를 실제로 다 채우는 게 아니라, "기본값이 뭐고 어디 하나만 다르다"는 규칙만 저장한다 — 그림 그릴 때 그 규칙대로 채우면 된다.

**완료 확인 방법**: 터미널에서 `python src/puzzle_generator.py`를 여러 번 실행해서 매번 `target_value`가 `base_value`와 다르고, 좌표가 격자 범위 안에 있는지 눈으로 확인. (검증 완료 — 정상 동작)

---

### Phase 2 — 이미지 렌더러 (`src/render_image.py`) ✅ 구현 완료

**목표**: Phase 1의 딕셔너리를 받아서 실제 1080×1920 그림(PNG)을 그린다.

**최종 코드 요약** (전체 주석은 `src/render_image.py` 참고):
```python
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # macOS 내장 한글 폰트
CANVAS_WIDTH, CANVAS_HEIGHT = 1080, 1920
BANNER_HEIGHT = 460

def render_number_grid(puzzle: dict) -> Image.Image:
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(246, 242, 234))
    draw = ImageDraw.Draw(img)

    # 1) 상단 검정 배너
    draw.rectangle([(0, 0), (CANVAS_WIDTH, BANNER_HEIGHT)], fill=(10, 10, 10))
    # 2) 네온 타이틀 + 서브텍스트 (가운데 정렬로 그림)
    # 3) rows x cols 격자를 순회하며 숫자 텍스트 그리기
    #    (row, col)이 target_row/col이면 target_value, 아니면 base_value
    return img
```

실제 구현에서는 텍스트를 칸 정중앙에 예쁘게 배치하기 위해 `_draw_centered_text()`라는 도우미 함수를 하나 더 만들어서, 글자 크기를 잰 뒤 중앙 좌표로 보정해서 그린다. (Pillow는 기본적으로 텍스트를 "왼쪽 위" 기준으로 그리기 때문)

**왜 이렇게 하나?**: `check_setup.py`에서 이미 검증한 Pillow 캔버스 생성 로직을 그대로 재사용하고, 격자 그리는 반복문만 추가하는 구조라 리스크가 낮다.

**완료 확인 방법**: `python src/render_image.py` 실행 → `output/test_grid.png`로 저장된 것을 열어서, 레퍼런스 영상과 비슷한 레이아웃인지, 이상값이 정확히 1칸만 다른지 확인. (검증 완료 — 레퍼런스와 동일한 레이아웃으로 정상 출력됨)

---

### Phase 3 — 영상 합성기 (`src/render_video.py`) ✅ 구현 완료

**목표**: Phase 2에서 만든 PNG + 배경음(mp3)을 합쳐서 mp4로 만든다.

**최종 코드**:
```python
import os
from moviepy import ImageClip, AudioFileClip

def build_video(image_path, audio_path, duration_sec, out_path):
    clip = ImageClip(image_path).with_duration(duration_sec)

    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).with_duration(duration_sec)
        clip = clip.with_audio(audio)
    else:
        print(f"안내: 배경음 파일을 찾을 수 없어 무음으로 만듭니다. ({audio_path})")

    has_audio = clip.audio is not None
    clip.write_videofile(out_path, fps=30, codec="libx264", audio=has_audio)
```

(moviepy 2.x 문법 — 지난번 `check_setup.py` 고칠 때 확인한 것과 동일한 API. `os.path.exists`로 배경음 파일 유무를 먼저 확인해서, 아직 `assets/bgm/`에 파일이 없어도 에러 없이 무음 영상으로 진행되도록 만들었다.)

**완료 확인 방법**: 생성된 mp4를 재생해서 레퍼런스 영상과 화질/비율(1080×1920)이 같은지 확인. (검증 완료 — `ffprobe`로 1080×1920 h264, 정확히 지정한 길이(초)로 생성됨을 확인)

---

### Phase 4 — 총괄 지휘자 (`src/pipeline.py`) ✅ 구현 완료

**목표**: Phase 1~3을 순서대로 실행하는 "메인 스크립트" 하나로 묶는다. 이게 있어야 사람이 명령어 한 줄만 치면 끝까지 자동으로 돌아간다.

**최종 코드 요약** (전체는 `src/pipeline.py` 참고):
```python
from datetime import date
from puzzle_generator import generate_number_find_puzzle
from render_image import render_number_grid
from render_video import build_video

def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = date.today().strftime("%y%m%d")   # 예: "260901"

    puzzle = generate_number_find_puzzle()
    img = render_number_grid(puzzle)
    img_path = f"output/{date_str}_temp.png"
    img.save(img_path)

    video_path = f"output/{date_str}.mp4"
    build_video(img_path, audio_path="assets/bgm/tension.mp3",
                duration_sec=10, out_path=video_path)

    save_log(date_str, puzzle)   # data/log.json에 정답 기록
    return video_path

if __name__ == "__main__":
    run()
```

`save_log()`는 `data/log.json`을 열어서(없으면 새로 만들어서) 그날 생성한 문제 정보를 리스트 맨 뒤에 추가하고 다시 저장하는 함수다. `if __name__ == "__main__": run()`이 파일 맨 아래 반드시 있어야 `python src/pipeline.py`로 실행했을 때 실제로 `run()`이 호출된다 (이 줄이 빠지면 함수만 정의되고 아무 일도 안 일어난다).

실행은 터미널에서:
```bash
cd "/Users/jun_jehyun/Desktop/JJH/01.Project/04.youtube_project"
source .venv/bin/activate
python src/pipeline.py
```

**완료 확인 방법**: 명령어 한 줄로 `output/` 폴더에 mp4가 자동 생성되고, `data/log.json`에 그날 정답이 기록되는지 확인. (검증 완료 — 1080×1920, 10초 mp4 정상 생성 + 로그 기록 확인) **여기까지 되면 "숫자찾기(월·수·금) 완전 자동화"는 끝난 것.**

---

### Phase 5 — 요일 매핑 (`data/calendar.json`) ✅ 구현 완료

**목표**: "오늘이 무슨 요일이니까 어떤 문제를 낼지"를 자동으로 정한다.

```json
{
  "monday": "number_find",
  "tuesday": "kanji_find",
  "wednesday": "number_find",
  "thursday": "count_how_many",
  "friday": "number_find",
  "saturday": "two_stage_quiz",
  "sunday": null
}
```

`pipeline.py`의 `_pick_format_by_weekday()` 함수가 실행 시점의 요일을 확인해서 이 표를 보고 어떤 포맷을 쓸지 자동으로 고른다. (일요일은 사용자가 준 표에 없어서 일단 `null`로 비워둠 — 실행하면 "포맷이 지정되어 있지 않다"는 안내와 함께 에러가 나도록 만들어뒀다. 나중에 정해지면 calendar.json만 고치면 된다.)

**완료 확인 방법**: `python src/pipeline.py --date 260831`(월)부터 `--date 260906`(일)까지 하루씩 날짜를 바꿔가며 실행 → 월/수/금은 `number_find`, 화는 `kanji_find`, 목은 `count_how_many`, 토는 `two_stage_quiz`가 자동으로 선택되고, 일요일은 의도한 대로 에러가 나는 것까지 확인 완료.

---

### Phase 6 — 나머지 포맷 3종 추가 ✅ 구현 완료

Phase 1~4로 "숫자찾기"가 완성된 뒤, 같은 패턴으로 나머지 3개 요일 포맷을 추가했다.

> **설계 변경 한 가지**: 애초 계획은 `src/formats/` 서브폴더를 만드는 것이었는데, 실제로 만들어보니 파일이 4개뿐이라 서브폴더로 나누면 파이썬 import 경로만 복잡해지고 얻는 이득이 없었다. 그래서 기존 파일들과 똑같이 `src/` 바로 아래 평평하게 두는 것으로 단순화했다. (`src/kanji_find.py`, `src/count_how_many.py`, `src/two_stage_quiz.py`)

또한 4개 포맷이 공통으로 쓰는 "캔버스 만들기 / 배너+타이틀 그리기 / 텍스트 가운데 정렬" 로직은 `src/render_common.py`라는 파일로 새로 뽑아냈다. (포맷이 1개였을 땐 `render_image.py` 안에 있어도 됐지만, 4개로 늘어나면서 같은 코드를 4번 복사하지 않기 위함)

| 포맷 | 파일 | 데이터 생성 시 다른 점 | 그리기 시 다른 점 |
|---|---|---|---|
| `kanji_find` (화) | `src/kanji_find.py` | 숫자 대신 `data/kanji_pairs.json`에서 헷갈리는 한자 쌍(未/末, 土/士, 千/干, 人/入, 大/犬, 鳥/烏, 力/刀, 白/自)을 뽑아 기본값/이상값으로 사용 | 정답을 타이틀에 공개하지 않고 "댓글에 정답을 남겨주세요!" 문구로 유도 |
| `count_how_many` (목) | `src/count_how_many.py` | 이상값이 1개가 아니라 3~5개(무작위) 등장 → 그 개수(N)가 정답. `random.sample`로 겹치지 않는 좌표 N개를 뽑음 | 정답 개수(N)를 공개하지 않고 "댓글에 개수를 남겨주세요!" 문구로 유도 |
| `two_stage_quiz` (토) | `src/two_stage_quiz.py` | `generate_number_find_puzzle()`을 두 번 호출해서 1번/2번 문제를 각각 생성 (기존 로직 재사용) | 이미지도 2장 그려서 오른쪽 위에 "1번 문제"/"2번 문제(마지막!)" 라벨을 추가로 얹고, `render_video.py`의 새 함수 `build_two_stage_video()`로 두 이미지를 이어붙여(`concatenate_videoclips`) 8초+7초=15초 영상 완성 |

**완료 확인 방법**: `python src/pipeline.py --date <각 요일 날짜>`로 4개 포맷 전부 실행 → 이미지 육안 확인(한자찾기: 정답 1칸만 다름/제목에 미공개, 개수세기: 지정한 개수만큼만 다름/제목에 미공개, 2단퀴즈: 라벨 정상 표시) + `ffprobe`로 2단퀴즈 mp4가 정확히 15초인 것까지 확인 완료.

---

### Phase 7 — 자동 실행 스케줄링

**목표**: 사람이 매일 터미널을 열어서 실행하지 않아도, 정해진 시각에 `pipeline.py`가 알아서 돌게 한다.

macOS는 `launchd`(또는 간단히 `cron`)로 "매일 오전 8시에 이 스크립트 실행"을 등록할 수 있다. 이 단계는 Phase 1~6이 안정화된 뒤에 진행 — 아직 검증 안 된 코드를 무인으로 돌리는 건 위험하다.

**완료 확인 방법**: 스케줄 등록 후 다음날 아침, 사람이 아무것도 안 눌렀는데 `output/`에 새 mp4가 생겼는지 확인.

---

### Phase 8 — 유튜브 업로드 자동화

**목표**: 완성된 mp4를 `google-api-python-client`로 자동 업로드.

이 단계는 `docs/SETUP.md` 6장에서 이미 사전 준비(OAuth, `client_secret.json`)를 안내해뒀다. Phase 7까지 끝난 뒤, 처음에는 "영상은 자동 생성 + 업로드는 사람이 최종 승인 후 수동"으로 시작하고, 화·목 댓글 테스트 결과가 쌓이면 업로드까지 완전 자동화하는 게 안전하다 (`WORKFLOW.md` 5장 참고).

---

## 4. 지금 당장 할 일 (요약)

1. ~~`src/puzzle_generator.py`에 `generate_number_find_puzzle()` 함수 작성 (Phase 1)~~ ✅ 완료
2. ~~`src/render_image.py`에 `render_number_grid()` 함수 작성 (Phase 2)~~ ✅ 완료
3. ~~`src/render_video.py`에 `build_video()` 함수 작성 (Phase 3)~~ ✅ 완료
4. ~~`src/pipeline.py`로 세 개 연결해서 명령어 한 줄로 mp4 완성 확인 (Phase 4)~~ ✅ 완료
5. ~~`data/calendar.json` 요일 매핑 만들기 (Phase 5)~~ ✅ 완료
6. ~~화(한자찾기)/목(何個ある)/토(2단퀴즈) 포맷 추가 (Phase 6)~~ ✅ 완료

**4개 요일 포맷 전부 완전 자동화 완성.** `python src/pipeline.py`만 실행하면 오늘 요일에 맞는 포맷으로 mp4가 자동 생성된다. 남은 할 일은:

- [ ] `assets/bgm/`에 실제 배경음(mp3) 파일 넣기 → 현재는 파일이 없어서 무음으로 생성됨 (이거 하나만 넣으면 소리까지 완성)
- [ ] Phase 7: 매일 자동으로 실행되도록 스케줄 등록 (launchd/cron)
- [ ] Phase 8: 유튜브 업로드 자동화 (OAuth 준비는 `docs/SETUP.md` 6장 참고)

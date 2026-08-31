# 사용 설명서 (HOW TO)

이 문서 하나만 보고도 이 프로젝트를 처음 만지는 사람이 영상을 뽑아낼 수 있도록 쓴 "조작법" 문서다. 코드가 왜 이렇게 짜여 있는지가 궁금하면 `docs/WORKFLOW.md`(왜/무엇을)와 `docs/BUILD_PLAN.md`(어떻게 만들었는지)를 보면 되고, 이 문서는 "그래서 지금 당장 뭘 어떻게 눌러야 하는지"만 다룬다.

---

## 0. 이 프로젝트가 하는 일 (한 줄 요약)

터미널에서 명령어 한 줄만 치면, 오늘 요일에 맞는 숏츠 퀴즈 영상(mp4)이 `output/` 폴더에 자동으로 생성된다.

| 요일 | 영상 종류 |
|---|---|
| 월·수·금 | 숫자찾기 (예: 隠れた174を探せ！) |
| 화 | 한자 하나 찾기 (未/末 등, 정답은 화면에 안 나옴) |
| 목 | 何個ある？ (특정 숫자가 몇 개 있는지 세기, 정답은 화면에 안 나옴) |
| 토 | 2단 퀴즈 15초 (문제 2개를 이어붙인 영상) |
| 일 | 아직 정해지지 않음 (실행하면 일부러 에러가 남) |

---

## 1. 시작하기 전에 (터미널을 새로 열 때마다 항상 하는 것)

터미널(macOS 기본 터미널 앱 또는 VS Code 터미널)을 켜고 아래 두 줄을 순서대로 입력한다.

```bash
cd "/Users/jun_jehyun/Desktop/JJH/01.Project/04.youtube_project"
source .venv/bin/activate
```

두 번째 줄을 실행하면 프롬프트(커서) 앞에 `(.venv)`라는 표시가 붙는다. **이게 안 붙어 있으면 이후 명령어들이 전부 실패한다** (필요한 패키지들이 이 가상환경 안에만 설치돼 있기 때문). 터미널 창을 닫았다가 다시 열면 이 표시가 사라지므로, 그때마다 두 줄을 다시 입력해야 한다.

---

## 2. 가장 기본적인 사용법: 영상 하나 만들기

가상환경이 켜진 상태(`(.venv)` 표시 확인)에서:

```bash
python src/pipeline.py
```

이 한 줄이면 끝이다. 터미널에 아래처럼 진행 상황이 순서대로 출력된다.

```
날짜: 260901 / 포맷: kanji_find
[1/3] 문제 생성 완료: {...}
[2/3] 이미지 저장 완료: output/260901_temp.png
[3/3] 영상 저장 완료: output/260901.mp4

완료: output/260901.mp4
```

- 오늘이 무슨 요일인지는 자동으로 판단해서, 위 0장 표에 맞는 포맷으로 만들어준다.
- 완성된 영상은 `output/오늘날짜.mp4` (예: `output/260901.mp4`)로 저장된다.
- `output/오늘날짜_temp.png` 처럼 `_temp`가 붙은 파일은 영상을 만들기 위해 중간에 그려둔 이미지다. 영상만 있으면 되고 이 파일은 필요 없으니, 확인 끝나면 지워도 된다.

---

## 3. 결과물 확인하기 (업로드 전 검수)

캔바와 다르게 "다운로드" 절차가 없다. `output/` 폴더에 mp4가 이미 로컬 파일로 만들어져 있으니:

1. Finder에서 `output/` 폴더를 연다.
2. 방금 생성된 mp4 파일을 더블클릭한다 (QuickTime Player로 바로 재생됨).
3. 화면 문구(일본어)가 이상하지 않은지, 정답 위치가 이상하지 않은지 눈으로 확인한다.
4. 괜찮으면 그 파일을 유튜브에 수동으로 업로드한다. (자동 업로드는 아직 준비 전 — `docs/WORKFLOW.md` 5장 참고)

**주의**: 지금 상태는 배경음악 파일이 없어서 무음 영상으로 만들어진다. 터미널에 `안내: 배경음 파일을 찾을 수 없어 무음으로 만듭니다`라는 문구가 뜨면 정상이다 (에러 아님). 배경음 추가 방법은 5장 참고.

---

## 4. 특정 요일 포맷을 강제로 테스트해보고 싶을 때

기본적으로는 오늘 요일에 맞는 포맷이 자동으로 선택되지만, "오늘은 월요일인데 화요일 한자찾기가 잘 만들어지는지 미리 보고 싶다" 같은 경우엔 옵션을 쓴다.

**포맷을 직접 지정하기** (`--format`):
```bash
python src/pipeline.py --format number_find       # 숫자찾기 (월·수·금)
python src/pipeline.py --format kanji_find         # 한자찾기 (화)
python src/pipeline.py --format count_how_many     # 何個ある？ (목)
python src/pipeline.py --format two_stage_quiz     # 2단 퀴즈 (토)
```

**다른 날짜로 테스트하기** (`--date`, YYMMDD 형식):
```bash
python src/pipeline.py --date 260905   # 2026년 9월 5일(토) 기준으로 실행 → two_stage_quiz가 자동 선택됨
```

두 옵션은 같이 쓸 수도 있다. `--format`을 지정하면 `--date`의 요일 판단은 무시되고 지정한 포맷이 강제로 쓰인다.

---

## 5. 배경음악(BGM) 추가하기

1. 유튜브 스튜디오의 **오디오 라이브러리**(studio.youtube.com → 오디오 보관함)에서 저작권 걱정 없는 배경음악을 mp3로 다운로드한다. (10초짜리 짧은 문제이므로 긴장감 있는 짧은 루프 곡이 잘 어울린다)
2. 다운로드한 파일을 `assets/bgm/tension.mp3`라는 이름으로 저장한다. (파일명을 다르게 하고 싶으면 `src/pipeline.py` 안의 `BGM_PATH` 값을 그 파일명으로 바꾸면 된다)
3. 그 이후로는 `python src/pipeline.py`를 실행할 때마다 자동으로 그 배경음이 붙는다. 별도 설정 변경 필요 없음.

---

## 6. "그날 정답이 뭐였지?" 확인하기

`python src/pipeline.py`를 실행할 때마다 `data/log.json`에 그날 만든 문제의 정답 정보가 자동으로 쌓인다. 텍스트 편집기나 VS Code로 그냥 열어보면 된다.

```json
[
  {
    "date": "260901",
    "format": "kanji_find",
    "base_value": "干",
    "target_value": "千",
    "target_row": 7,
    "target_col": 2
  }
]
```

화(한자찾기)·목(何個ある) 포맷은 화면에 정답을 안 보여주고 댓글 유도만 하기 때문에, 나중에 "실제 댓글이 정답과 얼마나 일치했는지" 확인할 때 이 파일을 기준으로 삼으면 된다.

---

## 7. 자주 겪을 수 있는 문제

| 증상 | 원인 / 해결 방법 |
|---|---|
| `zsh: command not found: python` | 가상환경이 안 켜져 있음. 1장의 `source .venv/bin/activate`를 먼저 실행 |
| `ModuleNotFoundError: No module named 'xxx'` | 가상환경이 안 켜져 있거나, `pip install -r requirements.txt`를 아직 안 한 상태. `docs/SETUP.md` 4단계 참고 |
| `ValueError: 'sunday'에 대한 포맷이 지정되어 있지 않습니다` | 일부러 넣어둔 안내 메시지. 일요일 포맷이 아직 안 정해져서 나는 정상적인 에러. `--format`으로 직접 지정해서 실행하면 됨 |
| 영상은 만들어졌는데 소리가 없음 | 정상. `assets/bgm/`에 배경음 파일이 없으면 무음으로 만들어짐 (5장 참고) |
| 격자에 글자가 네모 박스(□)로 깨져 나옴 | 폰트가 그 글자를 지원하지 않는 것. `src/render_common.py`의 `FONT_PATH`를 다른 폰트로 바꿔야 함 |
| 이미지/영상이 이상하게 나옴 (레이아웃 깨짐 등) | `output/`에 있는 `_temp.png` 파일을 먼저 열어서, 문제가 "그림 그리는 단계"인지 "영상으로 합치는 단계"인지 구분해서 확인 |

---

## 8. 뭘 고치면 뭐가 바뀌는지 (커스터마이징 지도)

| 바꾸고 싶은 것 | 고칠 파일 |
|---|---|
| 화면 글꼴 | `src/render_common.py`의 `FONT_PATH` |
| 화면 배경색/글자색 | `src/render_common.py`의 `BG_COLOR`, `TITLE_COLOR` 등 |
| 숫자찾기 화면 문구 | `src/render_image.py` |
| 한자찾기에 쓰이는 한자 쌍 목록 | `data/kanji_pairs.json` |
| 何個ある(목요일)의 정답 개수 범위(현재 3~5개) | `src/count_how_many.py`의 `MIN_COUNT`, `MAX_COUNT` |
| 2단 퀴즈(토요일)의 초 배분(현재 8초+7초) | `src/two_stage_quiz.py`의 `STAGE_1_DURATION_SEC`, `STAGE_2_DURATION_SEC` |
| 요일별로 어떤 포맷을 쓸지 | `data/calendar.json` |
| 배경음 파일 경로 | `src/pipeline.py`의 `BGM_PATH` |
| 영상 길이(현재 10초) | `src/pipeline.py`의 `DEFAULT_DURATION_SEC` |

---

## 9. 명령어 요약 (치트시트)

```bash
# 터미널을 새로 열 때마다 항상 먼저:
cd "/Users/jun_jehyun/Desktop/JJH/01.Project/04.youtube_project"
source .venv/bin/activate

# 오늘 요일에 맞는 영상 자동 생성
python src/pipeline.py

# 포맷을 직접 지정
python src/pipeline.py --format kanji_find

# 다른 날짜(요일)로 테스트
python src/pipeline.py --date 260905

# 개별 파일만 따로 테스트해보고 싶을 때
python src/puzzle_generator.py    # 문제 데이터만 생성해서 확인
python src/render_image.py        # 숫자찾기 이미지만 그려서 output/test_grid.png로 확인
python src/kanji_find.py          # 한자찾기 이미지만 확인
python src/count_how_many.py      # 개수세기 이미지만 확인
python src/two_stage_quiz.py      # 2단 퀴즈 이미지+영상까지 확인
```

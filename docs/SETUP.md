# 프로젝트 초기 설치 및 세팅 메뉴얼

숏츠(넘버 퍼즐형) 자동 생성 파이프라인 — Python 기반.

- 대상 OS: macOS (Apple Silicon, arm64)
- 확인된 현재 환경: Homebrew 설치됨 / 시스템 Python 3.9.6(`/usr/bin/python3`, Apple 번들) / ffmpeg 미설치
- 결정된 스택: Pillow, NumPy, MoviePy, edge-tts, google-api-python-client (자세한 배경은 이전 검토 보고서 참고)

---

## 0. 사전 확인

터미널에서 아래를 실행해 현재 상태를 확인한다.

```bash
brew --version
python3 --version
which ffmpeg
```

`ffmpeg`가 없다고 나오면(`ffmpeg not found`) 아래 1단계를 그대로 진행한다.

---

## 1. Homebrew 패키지 설치

시스템 Python(3.9.6)은 Apple이 번들한 구버전이라 이 프로젝트에는 쓰지 않는다. `brew`로 최신 Python과 ffmpeg를 새로 설치한다.

```bash
brew install python@3.12 ffmpeg
```

설치 후 버전 확인:

```bash
python3.12 --version
ffmpeg -version
```

---

## 2. 프로젝트 폴더 구조 생성

```bash
cd "/Users/jun_jehyun/Desktop/JJH/01.Project/04.youtube_project"

mkdir -p src assets/fonts assets/bgm assets/sfx data output docs
```

| 폴더 | 용도 |
|---|---|
| `src/` | 파이썬 스크립트(격자 생성, 합성, 렌더링 로직) |
| `assets/fonts/` | 한글 폰트 파일(타이틀/부제용) |
| `assets/bgm/` | 배경음악 |
| `assets/sfx/` | 정답 효과음 등 |
| `data/` | 문제 데이터셋(JSON/CSV) |
| `output/` | 렌더링된 mp4 결과물 |
| `docs/` | 프로젝트 문서(.md) — 이 파일이 위치한 곳 |

---

## 3. 가상환경(venv) 생성

시스템 Python 환경을 오염시키지 않도록 프로젝트 전용 가상환경을 만든다.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

가상환경이 활성화되면 프롬프트 앞에 `(.venv)`가 표시된다. 이후 모든 설치·실행은 이 상태에서 진행한다.

---

## 4. 의존성 설치

프로젝트 루트에 `requirements.txt`를 생성한다.

```txt
Pillow>=10.0
numpy>=1.26
moviepy>=1.0.3
edge-tts>=6.1
pydub>=0.25
google-api-python-client>=2.100
google-auth-oauthlib>=1.2
google-auth-httplib2>=0.2
python-dotenv>=1.0
```

설치:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> `moviepy`는 내부적으로 `ffmpeg` 바이너리를 호출한다. 2단계에서 설치한 ffmpeg가 PATH에 잡혀 있어야 정상 동작한다(`which ffmpeg`로 재확인).

---

## 5. 설치 검증

`src/check_setup.py` 파일을 만들어 아래 내용을 넣고 실행한다.

```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import moviepy.editor as mpy

# 1) Pillow로 세로 숏츠 캔버스 생성 테스트
img = Image.new("RGB", (1080, 1920), color=(246, 242, 234))
draw = ImageDraw.Draw(img)
draw.text((80, 80), "setup check", fill=(30, 30, 30))
img.save("output/setup_check.png")

# 2) NumPy 랜덤 좌표 생성 테스트
pos = np.random.randint(0, 10, size=2)
print("random grid position:", pos)

# 3) MoviePy로 정지 이미지 1초 영상 생성 테스트
clip = mpy.ImageClip("output/setup_check.png").set_duration(1).resize(height=1920)
clip.write_videofile("output/setup_check.mp4", fps=24, codec="libx264", audio=False)

print("OK: 이미지/영상 파이프라인 정상 동작")
```

```bash
python src/check_setup.py
```

`output/setup_check.mp4`가 생성되고 콘솔에 `OK: ...` 문구가 뜨면 이미지·영상 처리 환경 세팅은 완료된 것이다.

---

## 6. YouTube 업로드 자동화 준비 (선택, 나중에 사용)

Phase 3(자동 업로드) 단계에서 필요한 사전 준비만 미리 적어둔다. 지금 당장 진행할 필요는 없다.

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성
2. **YouTube Data API v3** 활성화
3. OAuth 2.0 클라이언트 ID(데스크톱 앱 유형) 생성 후 `client_secret.json` 다운로드
4. 해당 파일은 프로젝트 루트가 아닌 `.gitignore` 처리된 위치(예: `secrets/`)에 보관

---

## 7. Git 저장소 초기화 (선택)

버전 관리를 시작하려면:

```bash
git init
```

`.gitignore` 생성:

```
.venv/
output/*.mp4
__pycache__/
*.pyc
secrets/
.env
```

---

## 완료 체크리스트

- [ ] `brew install python@3.12 ffmpeg` 완료
- [ ] 폴더 구조 생성 완료
- [ ] `.venv` 생성 및 활성화 확인
- [ ] `requirements.txt` 기반 설치 완료
- [ ] `check_setup.py` 실행 성공 (mp4 생성 확인)

이 체크리스트가 모두 완료되면 다음 문서(격자 이미지 생성 로직 구현)로 넘어간다.

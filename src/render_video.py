"""
[Phase 3] 영상 합성기

목표: render_image.py(그리고 kanji_find.py / count_how_many.py / two_stage_quiz.py)가
만든 정지 이미지(PNG)에 배경음(오디오)을 붙여서, 최종적으로 유튜브에 올릴 수 있는
mp4 영상 파일을 만든다.

이 파일에는 함수가 2개 있다.
  - build_video()           : 이미지 1장짜리 포맷용 (숫자찾기/한자찾기/개수세기)
  - build_two_stage_video() : 이미지 2장을 이어붙이는 포맷용 (토요일 2단 퀴즈)

중요: 이 프로젝트에 설치된 moviepy는 2.x 버전이다 (pip install 시
requirements.txt에 버전 상한을 안 걸어놔서 최신 버전이 깔렸다).
moviepy 1.x와 2.x는 사용법이 다르므로 주의:
  - (1.x) import moviepy.editor as mpy   →  (2.x) from moviepy import ImageClip
  - (1.x) clip.set_duration(10)          →  (2.x) clip.with_duration(10)
  - (1.x) clip.resize(height=1920)       →  (2.x) clip.resized(height=1920)
이건 src/check_setup.py를 처음 실행했을 때 겪었던 에러와 같은 원인이다.
"""

import os

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


def build_video(image_path: str, audio_path: str, duration_sec: float, out_path: str) -> None:
    """
    정지 이미지 1장을 지정된 길이의 mp4 영상으로 만들어 저장한다.

    Args:
        image_path: 영상에 쓸 정지 이미지 경로 (예: "output/260901_temp.png")
        audio_path: 배경음 파일 경로 (예: "assets/bgm/tension.mp3").
                    파일이 실제로 존재하지 않으면 무음 영상으로 만든다.
        duration_sec: 영상 길이(초). 예: 10
        out_path: 결과 mp4를 저장할 경로 (예: "output/260901.mp4")
    """
    clip = ImageClip(image_path).with_duration(duration_sec)

    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).with_duration(duration_sec)
        clip = clip.with_audio(audio)
    else:
        print(f"안내: 배경음 파일을 찾을 수 없어 무음으로 만듭니다. ({audio_path})")

    has_audio = clip.audio is not None
    clip.write_videofile(out_path, fps=30, codec="libx264", audio=has_audio)


def build_two_stage_video(image_paths: list, durations: list, audio_path: str, out_path: str) -> None:
    """
    이미지 여러 장(토요일 포맷은 2장)을 각각 지정된 길이만큼 순서대로
    보여주고 하나로 이어붙여서 mp4로 만든다.

    예를 들어 image_paths=[1번문제.png, 2번문제.png], durations=[8, 7]이면:
    "1번문제.png를 8초 보여준 뒤 → 곧바로 2번문제.png를 7초 보여주는"
    총 15초짜리 영상 하나가 만들어진다.

    Args:
        image_paths: 순서대로 이어붙일 이미지 경로 리스트
        durations: 각 이미지를 몇 초씩 보여줄지 (image_paths와 개수가 같아야 함)
        audio_path: 배경음 파일 경로. 전체 길이(durations 합)에 맞춰 잘라 붙인다.
        out_path: 결과 mp4를 저장할 경로
    """
    # zip(image_paths, durations) : 두 리스트를 짝지어서 (이미지, 길이) 쌍으로 묶어준다.
    clips = [ImageClip(path).with_duration(sec) for path, sec in zip(image_paths, durations)]

    # concatenate_videoclips : 클립 여러 개를 순서대로 이어붙여 하나로 만든다.
    final_clip = concatenate_videoclips(clips)

    total_duration = sum(durations)
    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).with_duration(total_duration)
        final_clip = final_clip.with_audio(audio)
    else:
        print(f"안내: 배경음 파일을 찾을 수 없어 무음으로 만듭니다. ({audio_path})")

    has_audio = final_clip.audio is not None
    final_clip.write_videofile(out_path, fps=30, codec="libx264", audio=has_audio)


# "python src/render_video.py"로 이 파일만 직접 실행했을 때 동작하는 테스트 코드.
# Phase 2에서 만들어둔 output/test_grid.png가 있다는 전제로 짧은 영상을 만들어본다.
# (먼저 "python src/render_image.py"를 한 번 실행해서 test_grid.png를 만들어둬야 한다)
if __name__ == "__main__":
    build_video(
        image_path="output/test_grid.png",
        audio_path="assets/bgm/tension.mp3",
        duration_sec=10,
        out_path="output/test_video.mp4",
    )
    print("저장 완료: output/test_video.mp4")

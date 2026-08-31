from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import ImageClip

# 1) Pillow로 세로 숏츠 캔버스 생성 테스트
img = Image.new("RGB", (1080, 1920), color=(246, 242, 234))
draw = ImageDraw.Draw(img)
draw.text((80, 80), "setup check", fill=(30, 30, 30))
img.save("output/setup_check.png")

# 2) NumPy 랜덤 좌표 생성 테스트
pos = np.random.randint(0, 10, size=2)
print("random grid position:", pos)

# 3) MoviePy로 정지 이미지 1초 영상 생성 테스트
clip = ImageClip("output/setup_check.png").with_duration(1).resized(height=1920)
clip.write_videofile("output/setup_check.mp4", fps=24, codec="libx264", audio=False)

print("OK: 이미지/영상 파이프라인 정상 동작")
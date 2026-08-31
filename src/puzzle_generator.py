"""
[Phase 1] 문제 데이터 생성기

목표: "175로 가득 찬 격자 중 한 칸만 174로 다른" 문제를 코드로 만든다.

여기서는 실제로 격자 칸을 하나하나 다 채우지 않는다. 대신
"기본값이 175이고, 몇 번째 줄/칸 하나만 174로 다르다"는 규칙만
딕셔너리(정보 꾸러미) 형태로 만들어서 돌려준다.

이 규칙(딕셔너리)을 가지고 실제로 화면에 숫자를 그리는 일은
render_image.py가 담당한다. 즉 이 파일은 "무엇을 그릴지 정하는 것"만
책임지고, "어떻게 그릴지"는 신경 쓰지 않는다. 역할을 나눠두면
나중에 디자인만 바꾸고 싶을 때 이 파일은 건드릴 필요가 없다.
"""

import random


def generate_number_find_puzzle(rows: int = 13, cols: int = 8) -> dict:
    """
    숫자찾기 문제 하나를 무작위로 생성한다.

    Args:
        rows: 격자의 세로 칸 수 (기본 13줄)
        cols: 격자의 가로 칸 수 (기본 8칸)

    Returns:
        문제 정보를 담은 딕셔너리. 예:
        {
            "format": "number_find",
            "rows": 13, "cols": 8,
            "base_value": 175,      # 대부분의 칸에 들어갈 값
            "target_value": 174,    # 딱 한 칸에만 들어갈 "다른" 값 (=정답)
            "target_row": 3,        # 정답 칸의 세로 위치 (0부터 세기 시작)
            "target_col": 5,        # 정답 칸의 가로 위치 (0부터 세기 시작)
        }
    """
    # random.randint(a, b) : a 이상 b 이하의 정수 중 하나를 무작위로 뽑는다.
    # 세 자리 숫자(100~999) 중 하나를 기본값으로 정한다. 예: 175
    base_value = random.randint(100, 999)

    # 정답 값은 기본값에서 1을 뺀 값으로 정한다. 예: base_value가 175면 target_value는 174.
    # (너무 차이가 크면 눈에 확 띄어서 "찾는 재미"가 없어지기 때문에 1 차이로 둔다)
    target_value = base_value - 1

    # 정답이 들어갈 칸의 좌표(몇 번째 줄, 몇 번째 칸)도 무작위로 정한다.
    # rows가 13이면 target_row는 0~12 중 하나, cols가 8이면 target_col은 0~7 중 하나.
    target_row = random.randint(0, rows - 1)
    target_col = random.randint(0, cols - 1)

    return {
        "format": "number_find",
        "rows": rows,
        "cols": cols,
        "base_value": base_value,
        "target_value": target_value,
        "target_row": target_row,
        "target_col": target_col,
    }


# 아래 if 문은 파이썬의 관용적인 패턴이다.
# "python src/puzzle_generator.py"처럼 이 파일을 직접 실행했을 때만 실행되고,
# 다른 파일(예: pipeline.py)에서 이 파일의 함수를 "빌려 쓸 때"(import)는 실행되지 않는다.
# 그래서 이 파일 하나만 따로 테스트해보고 싶을 때 유용하다.
if __name__ == "__main__":
    puzzle = generate_number_find_puzzle()
    print("생성된 문제:", puzzle)

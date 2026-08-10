from pathlib import Path

from ultralytics import YOLOWorld


ROOT = Path(__file__).resolve().parents[1]

IMAGE_PATH = (
    ROOT
    / "static"
    / "originals"
    / "living"
    / "spring"
    / "SPLV01.png"
)


# SPLV01에 들어 있는 상품 종류
CLASSES = [
    "armchair",
    "coffee table",
    "floor lamp",
    "candle",
]


# YOLO-World 모델
model = YOLOWorld("yolov8s-worldv2.pt")

# 우리가 찾고 싶은 상품 종류 지정
model.set_classes(CLASSES)


# 탐지 실행
results = model.predict(
    source=str(IMAGE_PATH),
    conf=0.15,
    verbose=False,
)


print("\n===== SPLV01 탐지 결과 =====")


result = results[0]

image_height, image_width = result.orig_shape


for box in result.boxes:

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    class_name = CLASSES[class_id]

    x1, y1, x2, y2 = box.xyxy[0].tolist()

    # 바운딩박스 중심 좌표
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # HTML에서 사용할 % 좌표
    x_percent = center_x / image_width * 100
    y_percent = center_y / image_height * 100

    print(
        f"{class_name:<15}"
        f"신뢰도={confidence:.2f} "
        f"x={x_percent:.1f}% "
        f"y={y_percent:.1f}%"
    )
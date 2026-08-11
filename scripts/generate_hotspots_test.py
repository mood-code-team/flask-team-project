from pathlib import Path
import csv

from ultralytics import YOLOWorld


# 프로젝트 루트
ROOT = Path(__file__).resolve().parent.parent

# 테스트할 장면
SCENE_CODE = "SUBE01"

IMAGE_PATH = (
    ROOT
    / "static"
    / "originals"
    / "bedroom"
    / "summer"
    / f"{SCENE_CODE}.png"
)


# 결과 CSV
OUTPUT_CSV = (
    ROOT
    / "static"
    / "csv"
    / "gallery_hotspots.csv"
)


# SPLV01에 들어있는 실제 상품 코드와
# YOLO가 찾아야 할 객체 이름을 연결
PRODUCTS = [
    {
        "product_code": "MC-BD-004",
        "class_names": [
            "bed",
            "bed frame",
            "white bed",
        ],
    },
    {
        "product_code": "MC-LT-008",
        "class_names": [
            "side table",
            "bedside table",
            "blue side table",
        ],
    },
    {
        "product_code": "MC-LT-006",
        "class_names": [
            "floor lamp",
            "lamp",
            "blue floor lamp",
        ],
    },
    {
        "product_code": "MC-DF-001",
        "class_names": [
            "lavender sachet",
            "sachet",
            "small pouch",
            "fabric pouch",
        ],
    },
]


# YOLO-World 모델
model = YOLOWorld("yolov8s-worldv2.pt")

classes = []

for product in PRODUCTS:
    classes.extend(product["class_names"])

classes = list(dict.fromkeys(classes))

model.set_classes(classes)


# 객체 탐지
results = model.predict(
    source=str(IMAGE_PATH),
    conf=0.10,
    verbose=False,
)

result = results[0]

image_height, image_width = result.orig_shape


# class 이름별 가장 신뢰도가 높은 탐지 결과 보관
best_detections = {}

for box in result.boxes:

    class_id = int(box.cls[0])
    class_name = model.names[class_id]

    confidence = float(box.conf[0])

    x1, y1, x2, y2 = box.xyxy[0].tolist()

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    x_percent = center_x / image_width * 100
    y_percent = center_y / image_height * 100

    current = best_detections.get(class_name)

    if current is None or confidence > current["confidence"]:
        best_detections[class_name] = {
            "x": round(x_percent, 1),
            "y": round(y_percent, 1),
            "confidence": round(confidence, 2),
        }


# CSV에 저장할 데이터 생성
rows = []

for product in PRODUCTS:

    product_code = product["product_code"]

    best_match = None
    best_class_name = None

    for class_name in product["class_names"]:
        detection = best_detections.get(class_name)

        if detection is None:
            continue

        if (
            best_match is None
            or detection["confidence"] > best_match["confidence"]
        ):
            best_match = detection
            best_class_name = class_name

    if best_match is None:
        print(
            f"탐지 실패: {product_code} / "
            f"{product['class_names']}"
        )
        continue

    rows.append(
        {
            "scene_code": SCENE_CODE,
            "product_code": product_code,
            "product_type": best_class_name,
            "x": best_match["x"],
            "y": best_match["y"],
            "confidence": best_match["confidence"],
        }
    )


# CSV 폴더가 없으면 생성
OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# CSV 저장

file_exists = OUTPUT_CSV.is_file()

with OUTPUT_CSV.open(
    "a",
    encoding="utf-8-sig",
    newline="",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "scene_code",
            "product_code",
            "product_type",
            "x",
            "y",
            "confidence",
        ],
    )

    if not file_exists:
        writer.writeheader()

    writer.writerows(rows)


print()
print("===== 저장 완료 =====")
print(OUTPUT_CSV)

for row in rows:
    print(
        row["scene_code"],
        row["product_code"],
        row["product_type"],
        f'x={row["x"]}%',
        f'y={row["y"]}%',
        f'confidence={row["confidence"]}',
    )
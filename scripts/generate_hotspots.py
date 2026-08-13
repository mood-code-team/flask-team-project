from pathlib import Path
import csv

from ultralytics import YOLOWorld


# =========================================================
# 기본 경로
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

CSV_DIR = ROOT / "static" / "csv"
ORIGINALS_DIR = ROOT / "static" / "originals"

OUTPUT_CSV = CSV_DIR / "gallery_hotspots.csv"

SPACES = [
    "living",
    "bedroom",
    "dining",
    "balcony",
]


# =========================================================
# 공간별 상품 컬럼
# =========================================================

PRODUCT_FIELDS = {
    "living": [
        ("sofa_code", "sofa_name"),
        ("table_code", "table_name"),
        ("light_code", "light_name"),
        ("scent_code", "scent_name"),
    ],

    "bedroom": [
        ("bed_code", "bed_name"),
        ("side_table_code", "side_table_name"),
        ("light_code", "light_name"),
        ("scent_code", "scent_name"),
    ],

    "dining": [
        ("dining_code", "dining_name"),
        ("side_table_code", "side_table_name"),
        ("light_code", "light_name"),
        ("scent_code", "scent_name"),
    ],

    "balcony": [
        ("balcony_code", "balcony_name"),
        ("side_table_code", "side_table_name"),
        ("light_code", "light_name"),
        ("scent_code", "scent_name"),
    ],
}


# =========================================================
# 경로 함수
# =========================================================

def get_csv_path(space: str) -> Path:
    return CSV_DIR / f"moodcode_{space}_4seasons_16_final.csv"


def get_scene_image_path(
    space: str,
    season: str,
    image_name: str,
) -> Path:
    return ORIGINALS_DIR / space / season / image_name


# =========================================================
# 장면에서 상품 추출
# =========================================================

def get_scene_products(row: dict, space: str) -> list[dict]:
    products = []

    for code_field, name_field in PRODUCT_FIELDS[space]:

        code = (row.get(code_field) or "").strip()
        name = (row.get(name_field) or "").strip()

        if not code:
            continue

        products.append(
            {
                "code": code,
                "name": name,
                "field": code_field,
            }
        )

    return products


# =========================================================
# 상품 → YOLO 검색어 생성
# =========================================================

def get_detection_classes(product: dict) -> list[str]:

    field = product["field"]
    name = product["name"].lower()

    # 소파 / 암체어
    if field == "sofa_code":

        if "암체어" in name:
            return [
                "armchair",
                "lounge chair",
                "chair",
            ]

        return [
            "sofa",
            "couch",
        ]

    # 침대
    if field == "bed_code":
        return [
            "bed",
            "bed frame",
        ]

    # 다이닝 테이블
    if field == "dining_code":
        return [
            "dining table",
            "table",
        ]

    # 테이블
    if field in ("table_code", "side_table_code"):

        if "커피테이블" in name:
            return [
                "coffee table",
                "side table",
                "table",
            ]

        if "트레이테이블" in name:
            return [
                "side table",
                "tray table",
                "small table",
            ]

        if "보조테이블" in name:
            return [
                "side table",
                "small table",
                "table",
            ]

        return [
            "side table",
            "small table",
            "table",
        ]

    # 조명
    if field == "light_code":

        if "플로어스탠드" in name:
            return [
                "floor lamp",
                "lamp",
            ]

        if "탁상스탠드" in name:
            return [
                "table lamp",
                "lamp",
            ]

        if "펜던트" in name:
            return [
                "pendant lamp",
                "hanging lamp",
                "ceiling lamp",
            ]

        return [
            "lamp",
            "light",
        ]

    # 향 제품
    if field == "scent_code":

        if "향초" in name:
            return [
                "candle",
                "scented candle",
                "glass candle",
                "candle jar",
            ]

        if "라벤더주머니" in name:
            return [
                "lavender sachet",
                "sachet",
                "small pouch",
                "fabric pouch",
            ]

        if "디퓨저" in name:
            return [
                "reed diffuser",
                "diffuser bottle",
                "bottle",
            ]

        return [
            "home fragrance",
            "small container",
        ]

    # 발코니 메인 상품
    if field == "balcony_code":

        if "화분" in name:
            return [
                "plant pot",
                "planter",
                "flower pot",
            ]

        return [
            "outdoor furniture",
            "patio furniture",
        ]

    return []


# =========================================================
# YOLO 모델
# =========================================================

print("YOLO-World 모델 불러오는 중...")

model = YOLOWorld("yolov8s-worldv2.pt")

print("모델 준비 완료")


# =========================================================
# 전체 탐지 결과
# =========================================================

all_rows = []

total_scenes = 0
processed_scenes = 0


# =========================================================
# 4개 공간 처리
# =========================================================

for space in SPACES:

    csv_path = get_csv_path(space)

    if not csv_path.is_file():
        print(f"CSV 없음: {csv_path}")
        continue

    with csv_path.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        rows = list(reader)

    total_scenes += len(rows)

    print()
    print("=" * 60)
    print(f"{space.upper()} 처리 시작")
    print("=" * 60)

    for row in rows:

        scene_code = (row.get("scene_code") or "").strip()
        season = (row.get("season") or "").strip().lower()
        image_name = (row.get("original_image_name") or "").strip()

        if not scene_code or not season or not image_name:
            continue

        image_path = get_scene_image_path(
            space,
            season,
            image_name,
        )

        if not image_path.is_file():
            print(f"[이미지 없음] {scene_code}: {image_path}")
            continue

        products = get_scene_products(
            row,
            space,
        )

        print()
        print(f"[{scene_code}]")

        processed_scenes += 1

        # =================================================
        # 상품 하나씩 탐지
        # =================================================

        for product in products:

            product_code = product["code"]

            search_classes = get_detection_classes(product)

            if not search_classes:

                print(
                    f"  탐지 검색어 없음: "
                    f"{product_code}"
                )

                all_rows.append(
                    {
                        "scene_code": scene_code,
                        "product_code": product_code,
                        "product_type": "",
                        "x": "",
                        "y": "",
                        "confidence": 0,
                        "status": "failed",
                    }
                )

                continue

            # 이 상품 후보 검색어만 설정
            model.set_classes(search_classes)

            results = model.predict(
                source=str(image_path),
                conf=0.10,
                verbose=False,
            )

            result = results[0]

            image_height, image_width = result.orig_shape

            best_detection = None

            # =================================================
            # 가장 신뢰도 높은 탐지 하나 선택
            # =================================================

            for box in result.boxes:

                class_id = int(box.cls[0])

                class_name = model.names[class_id]

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                x_percent = (
                    center_x
                    / image_width
                    * 100
                )

                y_percent = (
                    center_y
                    / image_height
                    * 100
                )

                if (
                    best_detection is None
                    or confidence
                    > best_detection["confidence"]
                ):

                    best_detection = {
                        "class_name": class_name,
                        "x": round(x_percent, 1),
                        "y": round(y_percent, 1),
                        "confidence": round(confidence, 2),
                    }

            # =================================================
            # 탐지 실패
            # =================================================

            if best_detection is None:

                print(
                    f"  ❌ {product_code} "
                    f"탐지 실패"
                )

                all_rows.append(
                    {
                        "scene_code": scene_code,
                        "product_code": product_code,
                        "product_type": "",
                        "x": "",
                        "y": "",
                        "confidence": 0,
                        "status": "failed",
                    }
                )

                continue

            confidence = best_detection["confidence"]

            # =================================================
            # 상태 결정
            # =================================================

            if confidence >= 0.50:
                status = "auto"
            else:
                status = "review"

            print(
                f"  {product_code} "
                f"→ {best_detection['class_name']} "
                f"x={best_detection['x']}% "
                f"y={best_detection['y']}% "
                f"conf={confidence} "
                f"[{status}]"
            )

            all_rows.append(
                {
                    "scene_code": scene_code,
                    "product_code": product_code,
                    "product_type": best_detection["class_name"],
                    "x": best_detection["x"],
                    "y": best_detection["y"],
                    "confidence": confidence,
                    "status": status,
                }
            )


# =========================================================
# CSV 저장
# =========================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with OUTPUT_CSV.open(
    "w",
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
            "status",
        ],
    )

    writer.writeheader()
    writer.writerows(all_rows)


# =========================================================
# 결과 요약
# =========================================================

auto_count = sum(
    1
    for row in all_rows
    if row["status"] == "auto"
)

review_count = sum(
    1
    for row in all_rows
    if row["status"] == "review"
)

failed_count = sum(
    1
    for row in all_rows
    if row["status"] == "failed"
)


print()
print("=" * 60)
print("전체 자동 탐지 완료")
print("=" * 60)

print("전체 장면:", total_scenes)
print("처리 장면:", processed_scenes)

print()
print("AUTO:", auto_count)
print("REVIEW:", review_count)
print("FAILED:", failed_count)

print()
print("저장 위치:")
print(OUTPUT_CSV)
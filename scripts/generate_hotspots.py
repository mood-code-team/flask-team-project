from pathlib import Path
import csv

from ultralytics import YOLOWorld


ROOT = Path(__file__).resolve().parents[1]

OUTPUT_CSV = ROOT / "static" / "csv" / "gallery_hotspots.csv"


GALLERY_CSVS = {
    "living": ROOT / "static" / "csv" / "moodcode_living_4seasons_16_final.csv",
    "bedroom": ROOT / "static" / "csv" / "moodcode_bedroom_4seasons_16_final.csv",
    "dining": ROOT / "static" / "csv" / "moodcode_dining_4seasons_16_final.csv",
    "balcony": ROOT / "static" / "csv" / "moodcode_balcony_4seasons_16_final.csv",
}


PRODUCT_DETECTION_MAP = {
    "sofa_code": [
        "armchair",
        "chair",
        "lounge chair",
        "sofa",
    ],

    "table_code": [
        "coffee table",
        "side table",
        "table",
    ],

    "bed_code": [
        "bed",
        "bed frame",
    ],

    "dining_code": [
        "dining table",
        "table",
    ],

    "balcony_code": [
        "plant pot",
        "planter",
        "flower pot",
    ],

    "side_table_code": [
        "side table",
        "coffee table",
        "table",
    ],

    "light_code": [
        "floor lamp",
        "table lamp",
        "lamp",
    ],

    "scent_code": [
        "candle",
        "scented candle",
        "glass candle",
        "candle jar",
    ],
}


def get_scene_products(row: dict) -> list[dict]:
    products = []

    for code_field, search_terms in PRODUCT_DETECTION_MAP.items():

        product_code = (row.get(code_field) or "").strip()

        if not product_code:
            continue

        name_field = code_field.replace("_code", "_name")

        products.append({
            "code_field": code_field,
            "product_code": product_code,
            "product_name": (row.get(name_field) or "").strip(),
            "search_terms": search_terms,
        })

    return products


def get_image_path(
    space: str,
    season: str,
    image_name: str,
) -> Path:

    return (
        ROOT
        / "static"
        / "originals"
        / space
        / season
        / image_name
    )


def detect_product(
    model,
    image_path: Path,
    search_terms: list[str],
):
    model.set_classes(search_terms)

    results = model.predict(
        source=str(image_path),
        conf=0.12,
        verbose=False,
    )

    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:
        return None

    # 가장 신뢰도가 높은 탐지 결과
    best_box = max(
        result.boxes,
        key=lambda box: float(box.conf[0]),
    )

    confidence = float(best_box.conf[0])

    x1, y1, x2, y2 = best_box.xyxy[0].tolist()

    image_height, image_width = result.orig_shape

    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    x_percent = center_x / image_width * 100
    y_percent = center_y / image_height * 100

    class_id = int(best_box.cls[0])

    product_type = search_terms[class_id]

    return {
        "product_type": product_type,
        "x": round(x_percent, 1),
        "y": round(y_percent, 1),
        "confidence": round(confidence, 2),
    }


model = YOLOWorld("yolov8s-worldv2.pt")

output_rows = []

total_scenes = 0
processed_scenes = 0

auto_count = 0
review_count = 0
failed_count = 0


for space, csv_path in GALLERY_CSVS.items():

    print("\n" + "=" * 60)
    print("공간:", space)
    print("CSV:", csv_path)

    if not csv_path.is_file():
        print("❌ CSV 없음")
        continue

    with csv_path.open(
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        rows = list(csv.DictReader(handle))

    total_scenes += len(rows)

    print("장면 개수:", len(rows))


    for row in rows:

        scene_code = (row.get("scene_code") or "").strip()
        season = (row.get("season") or "").strip().lower()
        image_name = (row.get("original_image_name") or "").strip()

        if not scene_code or not season or not image_name:
            continue

        image_path = get_image_path(
            space,
            season,
            image_name,
        )

        print(f"\n[{scene_code}]")

        if not image_path.is_file():
            print("  ❌ 이미지 없음:", image_path)
            continue

        products = get_scene_products(row)

        for product in products:

            detection = detect_product(
                model,
                image_path,
                product["search_terms"],
            )

            if detection is None:

                status = "failed"
                failed_count += 1

                output_rows.append({
                    "scene_code": scene_code,
                    "product_code": product["product_code"],
                    "product_type": "",
                    "x": "",
                    "y": "",
                    "confidence": "",
                    "status": status,
                })

                print(
                    "  FAILED:",
                    product["product_code"],
                    product["search_terms"],
                )

                continue


            confidence = detection["confidence"]

            if confidence >= 0.50:
                status = "auto"
                auto_count += 1
            else:
                status = "review"
                review_count += 1


            output_rows.append({
                "scene_code": scene_code,
                "product_code": product["product_code"],
                "product_type": detection["product_type"],
                "x": detection["x"],
                "y": detection["y"],
                "confidence": confidence,
                "status": status,
            })


            print(
                f"  {status.upper():6}"
                f" {product['product_code']}"
                f" {detection['product_type']}"
                f" x={detection['x']}%"
                f" y={detection['y']}%"
                f" conf={confidence}"
            )


        processed_scenes += 1


fieldnames = [
    "scene_code",
    "product_code",
    "product_type",
    "x",
    "y",
    "confidence",
    "status",
]


with OUTPUT_CSV.open(
    "w",
    encoding="utf-8-sig",
    newline="",
) as handle:

    writer = csv.DictWriter(
        handle,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(output_rows)


print("\n" + "=" * 60)
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
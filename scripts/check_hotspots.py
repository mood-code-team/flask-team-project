from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]

HOTSPOT_CSV = (
    ROOT
    / "static"
    / "csv"
    / "gallery_hotspots.csv"
)


def main():
    if not HOTSPOT_CSV.is_file():
        print("gallery_hotspots.csv 파일이 없습니다.")
        return

    with HOTSPOT_CSV.open(
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    review_scenes = {}

    review_count = 0
    failed_count = 0

    for row in rows:
        status = (row.get("status") or "").strip().lower()

        # 이미 수동 보정된 manual이나 정상 auto는 제외
        if status not in {"review", "failed"}:
            continue

        scene_code = (row.get("scene_code") or "").strip()
        product_code = (row.get("product_code") or "").strip()
        product_type = (row.get("product_type") or "").strip()
        confidence = (row.get("confidence") or "").strip()

        if not scene_code:
            continue

        if scene_code not in review_scenes:
            review_scenes[scene_code] = []

        review_scenes[scene_code].append({
            "status": status,
            "product_code": product_code,
            "product_type": product_type,
            "confidence": confidence,
        })

        if status == "review":
            review_count += 1
        elif status == "failed":
            failed_count += 1

    print("\n" + "=" * 60)
    print("핫스팟 검수 필요 장면")
    print("=" * 60)

    for scene_code in sorted(review_scenes):

        print(f"\n{scene_code}")
        print(f"  URL: http://127.0.0.1:5000/scene/{scene_code}")

        for item in review_scenes[scene_code]:

            status_text = item["status"].upper()

            if item["confidence"]:
                confidence_text = f" conf={item['confidence']}"
            else:
                confidence_text = ""

            product_type = item["product_type"]

            if product_type:
                type_text = f" / {product_type}"
            else:
                type_text = ""

            print(
                f"  {status_text:<6}"
                f" {item['product_code']}"
                f"{type_text}"
                f"{confidence_text}"
            )

    print("\n" + "=" * 60)
    print("검수 요약")
    print("=" * 60)

    print("검수 필요 장면:", len(review_scenes))
    print("REVIEW:", review_count)
    print("FAILED:", failed_count)


if __name__ == "__main__":
    main()
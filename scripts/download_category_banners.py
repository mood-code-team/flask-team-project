"""카테고리·히어로 배너 이미지 다운로드 (Unsplash → static)."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "static" / "images" / "category"

# slug → 방 구조 인테리어 (카테고리별 고유 photo id, 중복·외관 건물 사진 금지)
CATEGORY_PHOTOS: dict[str, str] = {
    "light": "photo-1600210492486-724fe5c67fb0",       # 밝은 거실 · 자연광
    "sofa": "photo-1555041469-a586c61ea9bc",           # 소파 중심 거실
    "side-table": "photo-1616486338812-3dadae4b4ace",  # 사이드테이블·라운지
    "diffuser": "photo-1615529328331-f8917597711f",    # 아늑한 실내 거실
    "table": "photo-1617806118233-18e1de247200",       # 다이닝룸
    "bed": "photo-1522771739844-6a9f6d5f14af",         # 침실 레이아웃
    "balcony": "photo-1560448204-603b3fc33ddc",        # 야외 테라스 · 발코니
}


def _assert_unique_photos() -> None:
    ids = list(CATEGORY_PHOTOS.values())
    if len(ids) != len(set(ids)):
        raise ValueError("CATEGORY_PHOTOS must not reuse the same photo id")

SIZES = {
    "1920": "w=1920&q=90&auto=format&fit=crop",
    "3840": "w=3840&q=92&auto=format&fit=crop",
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "MoodCode/1.0 (category banner setup)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    if len(data) < 5000:
        raise RuntimeError(f"Download too small: {dest.name} ({len(data)} bytes)")
    dest.write_bytes(data)
    print(f"saved {dest.relative_to(ROOT)} ({len(data) // 1024} KB)")


def main() -> None:
    _assert_unique_photos()
    for slug, photo_id in CATEGORY_PHOTOS.items():
        for label, params in SIZES.items():
            url = f"https://images.unsplash.com/{photo_id}?{params}"
            suffix = "" if label == "3840" else "-2k"
            dest = OUT_DIR / f"{slug}{suffix}.jpg"
            download(url, dest)
    print("Done.")


if __name__ == "__main__":
    main()

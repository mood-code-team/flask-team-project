#!/usr/bin/env python3
"""
Notion Mood Code 기획 페이지 가져오기.

사용:
  python scripts/notion_fetch_spec.py
  python scripts/notion_fetch_spec.py --save docs/NOTION_MOOD_CODE.md

Notion 페이지를 Integration에 연결해야 합니다.
  docs/NOTION_SETUP.md 참고
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

NOTION_PAGE_URL = "https://app.notion.com/p/Mood-Code-3aa8246defc680c79bdfc0acb523a9ec"
NOTION_PAGE_ID = "3aa8246defc680c79bdfc0acb523a9ec"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Mood Code Notion spec")
    parser.add_argument("--save", type=Path, help="Save fetched markdown to file")
    args = parser.parse_args()

    print("Notion Mood Code 페이지 연결 확인")
    print(f"  URL: {NOTION_PAGE_URL}")
    print()
    print("Cursor에서 Notion MCP가 연결되어 있으면 Agent가 notion-fetch로 내용을 읽을 수 있습니다.")
    print("직접 API 호출은 Integration Token(NOTION_TOKEN)이 필요합니다.")
    print()

    token = _read_notion_token()
    if not token:
        print("[안내] NOTION_TOKEN 환경 변수가 없습니다.")
        print("       Notion → Settings → Connections → Integration 생성 후")
        print("       Mood Code 페이지 우측 상단 ··· → Connect to 로 Integration 추가")
        print("       docs/NOTION_SETUP.md 를 따라주세요.")
        return 1

    try:
        content = _fetch_page(token, NOTION_PAGE_ID)
    except urllib.error.HTTPError as exc:
        print(f"[FAIL] Notion API {exc.code}: {exc.reason}")
        if exc.code == 404:
            print("       페이지를 Integration에 공유했는지 확인하세요.")
        return 1

    text = _blocks_to_text(content)
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(text, encoding="utf-8")
        print(f"[OK] 저장됨: {args.save}")
    else:
        print(text[:4000] or "(내용 없음)")
    return 0


def _read_notion_token() -> str | None:
    import os

    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _fetch_page(token: str, page_id: str) -> list:
    page_id = page_id.replace("-", "")
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data.get("results", [])


def _blocks_to_text(blocks: list) -> str:
    lines: list[str] = []
    for block in blocks:
        block_type = block.get("type")
        payload = block.get(block_type, {})
        rich = payload.get("rich_text") or payload.get("text") or []
        text = "".join(part.get("plain_text", "") for part in rich)
        if text:
            lines.append(text)
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())

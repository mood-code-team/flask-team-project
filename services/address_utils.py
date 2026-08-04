"""주소 조합·파싱 — 우편번호 검색 연동."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ParsedAddress:
    postcode: str = ""
    road: str = ""
    jibun: str = ""
    detail: str = ""
    full: str = ""


_POSTCODE_RE = re.compile(r"^\((\d{5})\)\s*")


def compose_address(
    *,
    postcode: str = "",
    road: str = "",
    jibun: str = "",
    detail: str = "",
) -> str:
    """도로명·지번·상세주소를 저장용 한 줄 문자열로 합칩니다."""
    postcode = postcode.strip()
    road = road.strip()
    jibun = jibun.strip()
    detail = detail.strip()

    head_parts: list[str] = []
    if postcode:
        head_parts.append(f"({postcode})")
    if road:
        head_parts.append(road)
    if jibun and jibun != road:
        head_parts.append(f"[지번] {jibun}")

    head = " ".join(head_parts).strip()
    if head and detail:
        return f"{head} | {detail}"
    return head or detail


def parse_address(raw: str | None) -> ParsedAddress:
    """저장된 주소 문자열을 폼 필드용으로 분해합니다."""
    text = (raw or "").strip()
    if not text:
        return ParsedAddress()

    postcode = ""
    rest = text
    match = _POSTCODE_RE.match(text)
    if match:
        postcode = match.group(1)
        rest = text[match.end() :].strip()

    detail = ""
    if " | " in rest:
        main, detail = rest.split(" | ", 1)
    else:
        main = rest

    jibun = ""
    road = main.strip()
    if "[지번]" in main:
        road, jibun = main.split("[지번]", 1)
        road = road.strip()
        jibun = jibun.strip()

    detail = detail.strip()

    return ParsedAddress(
        postcode=postcode,
        road=road,
        jibun=jibun,
        detail=detail,
        full=text,
    )

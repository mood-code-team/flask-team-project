"""채널톡 SDK 설정."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from flask import current_app
from flask_login import current_user


def _member_hash(member_id: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), member_id.encode("utf-8"), hashlib.sha256).hexdigest()


def get_boot_options() -> dict[str, Any] | None:
    """전 페이지 채널톡 boot 옵션."""
    plugin_key = current_app.config.get("CHANNEL_TALK_PLUGIN_KEY", "")
    if not plugin_key:
        return None

    options: dict[str, Any] = {
        "pluginKey": plugin_key,
        "hideChannelButtonOnBoot": True,
        "language": "ko",
    }

    if current_user.is_authenticated and getattr(current_user, "is_active", True):
        guest_emails = {"guest@shop.local"}
        guest_names = {"guest_checkout", "guest"}
        if (
            current_user.email not in guest_emails
            and current_user.username not in guest_names
        ):
            member_id = str(current_user.id)
            options["memberId"] = member_id

            profile: dict[str, str] = {}
            if current_user.full_name:
                profile["name"] = current_user.full_name
            if current_user.email:
                profile["email"] = current_user.email
            if current_user.phone:
                profile["mobileNumber"] = current_user.phone

            from services.membership_service import membership_label

            profile["membershipTier"] = membership_label(current_user.id)
            if current_user.region:
                profile["region"] = current_user.region

            options["profile"] = profile

            secret = current_app.config.get("CHANNEL_TALK_SECRET", "")
            if secret:
                options["memberHash"] = _member_hash(member_id, secret)

    return options


def is_channel_talk_enabled() -> bool:
    return bool(current_app.config.get("CHANNEL_TALK_PLUGIN_KEY"))

"""Helpers to keep the old Flarum vocabulary game out of reaction loops."""

from __future__ import annotations

from typing import Iterable


def _norm(value: object) -> str:
    return str(value or "").casefold()


def _tag_text(tags: object) -> str:
    if tags is None:
        return ""
    if isinstance(tags, str):
        return tags.casefold()
    if isinstance(tags, Iterable):
        parts: list[str] = []
        for tag in tags:
            if isinstance(tag, dict):
                parts.append(_norm(tag.get("name")))
                parts.append(_norm(tag.get("slug")))
            else:
                parts.append(_norm(tag))
        return " ".join(parts)
    return _norm(tags)


def ist_vokabel_thread(title: object = "", tags: object = None) -> bool:
    """True for Daniel's old "one word, one synonym" Flarum game threads."""
    title_text = _norm(title)
    tags_text = _tag_text(tags)
    if "vokabel" in tags_text:
        return True
    return "beginne mit einem wort" in title_text and "synonym" in title_text

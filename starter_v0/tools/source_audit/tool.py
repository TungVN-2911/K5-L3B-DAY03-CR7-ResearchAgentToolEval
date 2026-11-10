from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from tools._shared import domain, err


def _canonical_url(value: str) -> str | None:
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None

    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"

    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower(), host, path, parsed.query, ""))


def _audit_sources(items: list[dict[str, Any]]) -> dict[str, Any]:
    url_indices: dict[str, list[int]] = defaultdict(list)
    source_counts: Counter[str] = Counter()

    for index, item in enumerate(items):
        raw_url = item.get("url")
        if isinstance(raw_url, str) and raw_url.strip():
            canonical = _canonical_url(raw_url)
            if canonical:
                url_indices[canonical].append(index)

        source = item.get("source")
        if not isinstance(source, str) or not source.strip():
            source = domain(raw_url) if isinstance(raw_url, str) else ""
        if source:
            source_counts[source.strip().lower()] += 1

    duplicates = [
        {"url": url, "indices": indices}
        for url, indices in sorted(url_indices.items())
        if len(indices) > 1
    ]
    return {
        "tool": "source_audit",
        "item_count": len(items),
        "unique_url_count": len(url_indices),
        "duplicate_urls": duplicates,
        "source_counts": dict(sorted(source_counts.items())),
    }


def source_audit(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of objects")
        if any(not isinstance(item, dict) for item in items):
            raise TypeError("each item must be an object")
        return _audit_sources(items)
    except Exception as exc:
        return err("source_audit", exc)

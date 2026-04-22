"""File-based provider output cache.

Cache layout:
  cache/{patient_id}/{YYYY-MM-DD}/{provider_key}.json
  cache/{patient_id}/{YYYY-MM-DD}/{provider_key}_image.{ext}   (if image_url present)

Each JSON file includes a top-level _cache_meta block with timing and token cost.
"""

import json
import logging
import mimetypes
import re
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from PIL import Image

from app.services.care_circle.provider_base import WIKIMEDIA_USER_AGENT

_DOWNLOAD_HEADERS = {
    "User-Agent": WIKIMEDIA_USER_AGENT,
}

logger = logging.getLogger(__name__)

CACHE_ROOT = Path(__file__).resolve().parents[3] / "cache"

_IMAGE_KEYS = ("image_url",)
_IMG_SRC_RE = re.compile(r'src=(["\'])(https?://[^"\'> ]+)\1', re.IGNORECASE)
_COMIC_PROVIDER_PREFIX = "comic_"
_COMIC_MAX_WIDTH = 600
_COMIC_JPEG_QUALITY = 82


def _cache_path(patient_id: int, for_date: date, provider_key: str) -> Path:
    return CACHE_ROOT / str(patient_id) / for_date.isoformat() / f"{provider_key}.json"


def _image_ext(url: str, content_type: str | None) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext and ext not in (".jpe",):
            return ext
    parsed_path = urlparse(url).path
    suffix = Path(parsed_path).suffix
    return suffix if suffix else ".jpg"


def _download_image(url: str, dest: Path) -> bool:
    """Download image to dest. Returns True on success."""
    try:
        with httpx.Client(follow_redirects=True, timeout=15, headers=_DOWNLOAD_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return True
    except Exception as exc:
        logger.warning("Failed to download image %s: %s", url, exc)
        return False


def _is_comic_provider(provider_key: str) -> bool:
    return provider_key.startswith(_COMIC_PROVIDER_PREFIX)


def _comic_image_filename(provider_key: str, suffix: str = "") -> str:
    return f"{provider_key}_image{suffix}.jpg"


def _download_and_optimize_comic_image(url: str, dest: Path) -> bool:
    """Download a comic image, resize it to fit the newsletter, and store it as JPEG."""
    try:
        with httpx.Client(follow_redirects=True, timeout=20, headers=_DOWNLOAD_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()

        with Image.open(BytesIO(resp.content)) as image:
            image = image.convert("RGB")
            if image.width > _COMIC_MAX_WIDTH:
                new_height = max(1, int(round(image.height * (_COMIC_MAX_WIDTH / image.width))))
                image = image.resize((_COMIC_MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            image.save(
                dest,
                format="JPEG",
                quality=_COMIC_JPEG_QUALITY,
                optimize=True,
            )
        return True
    except Exception as exc:
        logger.warning("Failed to optimize comic image %s: %s", url, exc)
        return False


SERVED_IMAGE_URL_PREFIX = "/api/v1/care-circle/cached-image"


def _served_url(patient_id: int, for_date: date, filename: str) -> str:
    return f"{SERVED_IMAGE_URL_PREFIX}/{patient_id}/{for_date.isoformat()}/{filename}"


def local_path_for_served_url(url: str) -> Path | None:
    """Resolve a served cache-image URL back to the local filesystem path."""
    prefix = SERVED_IMAGE_URL_PREFIX + "/"
    if not url.startswith(prefix):
        return None
    parts = url[len(prefix):].split("/", 2)
    if len(parts) != 3:
        return None
    patient_id, date_str, filename = parts
    candidate = CACHE_ROOT / patient_id / date_str / filename
    try:
        candidate.resolve().relative_to(CACHE_ROOT.resolve())
    except ValueError:
        return None
    return candidate if candidate.exists() else None


def _process_images(
    result: dict[str, Any],
    cache_dir: Path,
    provider_key: str,
    patient_id: int,
    for_date: date,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """Download remote images to disk, replace src= URLs with served API paths."""
    data = result.get("data")
    if not isinstance(data, dict):
        return result

    result = dict(result)
    result["data"] = dict(data)
    data = result["data"]

    urls_to_download: dict[str, str] = {}
    is_comic_provider = _is_comic_provider(provider_key)

    for key in _IMAGE_KEYS:
        url = data.get(key)
        if isinstance(url, str) and url.startswith("http"):
            if is_comic_provider:
                urls_to_download[url] = _comic_image_filename(provider_key)
            else:
                ext = _image_ext(url, None)
                urls_to_download[url] = f"{provider_key}_image{ext}"

    html = data.get("rendered_html", "")
    for idx, match in enumerate(_IMG_SRC_RE.finditer(html)):
        url = match.group(2)
        if url not in urls_to_download:
            suffix = f"_{idx}" if idx > 0 else ""
            if is_comic_provider:
                urls_to_download[url] = _comic_image_filename(provider_key, suffix)
            else:
                ext = _image_ext(url, None)
                urls_to_download[url] = f"{provider_key}_image{suffix}{ext}"

    if not urls_to_download:
        return result

    url_to_filename: dict[str, str] = {}
    for url, filename in urls_to_download.items():
        local_path = cache_dir / filename
        if force_regenerate and local_path.exists():
            local_path.unlink()

        download_ok = (
            _download_and_optimize_comic_image(url, local_path)
            if is_comic_provider
            else _download_image(url, local_path)
        )
        if local_path.exists() or download_ok:
            url_to_filename[url] = filename
            logger.debug("Cached image for %s -> %s", provider_key, filename)

    for key in _IMAGE_KEYS:
        url = data.get(key)
        if url and url in url_to_filename:
            data[f"{key}_remote"] = url
            data[key] = _served_url(patient_id, for_date, url_to_filename[url])

    if html and url_to_filename:
        def _replace(match: re.Match) -> str:
            quote, url = match.group(1), match.group(2)
            filename = url_to_filename.get(url)
            if filename:
                return f"src={quote}{_served_url(patient_id, for_date, filename)}{quote}"
            return match.group(0)

        data["rendered_html"] = _IMG_SRC_RE.sub(_replace, html)

    return result


def get_cached_result(patient_id: int, for_date: date, provider_key: str) -> dict[str, Any] | None:
    path = _cache_path(patient_id, for_date, provider_key)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to read cache %s: %s", path, exc)
        return None


def save_cached_result(
    patient_id: int,
    for_date: date,
    provider_key: str,
    result: dict[str, Any],
    *,
    elapsed_ms: float | None = None,
    token_usage: dict[str, Any] | None = None,
    force_regenerate: bool = False,
) -> None:
    path = _cache_path(patient_id, for_date, provider_key)
    path.parent.mkdir(parents=True, exist_ok=True)

    result = _process_images(
        result,
        path.parent,
        provider_key,
        patient_id,
        for_date,
        force_regenerate=force_regenerate,
    )

    meta: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "patient_id": patient_id,
        "for_date": for_date.isoformat(),
        "provider_key": provider_key,
    }
    if elapsed_ms is not None:
        meta["elapsed_ms"] = round(elapsed_ms, 1)
    if token_usage:
        total = token_usage.get("total_tokens", 0)
        if total:
            meta["tokens"] = {
                "prompt": token_usage.get("prompt_tokens", 0),
                "completion": token_usage.get("completion_tokens", 0),
                "total": total,
                "model": token_usage.get("model", ""),
            }

    result = dict(result)
    result["_cache_meta"] = meta

    try:
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to write cache %s: %s", path, exc)


def is_cached(patient_id: int, for_date: date, provider_key: str) -> bool:
    return _cache_path(patient_id, for_date, provider_key).exists()

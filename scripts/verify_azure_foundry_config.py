r"""
Simple Azure Foundry config verifier for Care Circle.

Checks the current environment-backed Care Circle Azure settings and performs
an optional live smoke test against the configured text/image deployments.

Usage:
    .\.venv\Scripts\python.exe .\scripts\verify_azure_foundry_config.py
    .\.venv\Scripts\python.exe .\scripts\verify_azure_foundry_config.py --image
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import settings  # noqa: E402
from app.services.care_circle.llm_helpers import (  # noqa: E402
    generate_image_url_with_usage,
    generate_text_with_usage,
)


def _mask_secret(value: str | None) -> str:
    if not value:
        return "<missing>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _require(name: str, value: str | None) -> str:
    if not value or not str(value).strip():
        raise RuntimeError(f"{name} is missing.")
    return str(value).strip()


def _validate_text_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("AZURE_FOUNDRY_TEXT_ENDPOINT is not a valid URL.")
    if not parsed.scheme.startswith("http"):
        raise RuntimeError("AZURE_FOUNDRY_TEXT_ENDPOINT must use http or https.")
    if not parsed.netloc.endswith("services.ai.azure.com"):
        raise RuntimeError(
            "AZURE_FOUNDRY_TEXT_ENDPOINT should point at a Foundry services host ending in services.ai.azure.com."
        )
    if "/api/projects/" not in parsed.path:
        raise RuntimeError(
            "AZURE_FOUNDRY_TEXT_ENDPOINT should include the project path, for example /api/projects/<project-name>."
        )
    return endpoint.rstrip("/")


def _validate_image_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("AZURE_FOUNDRY_IMAGE_ENDPOINT is not a valid URL.")
    if not parsed.scheme.startswith("http"):
        raise RuntimeError("AZURE_FOUNDRY_IMAGE_ENDPOINT must use http or https.")
    if parsed.netloc.endswith("openai.azure.com"):
        return endpoint.rstrip("/")
    if parsed.netloc.endswith("services.ai.azure.com") and "/api/projects/" in parsed.path:
        return endpoint.rstrip("/")
    raise RuntimeError(
        "AZURE_FOUNDRY_IMAGE_ENDPOINT should be either an Azure OpenAI host (*.openai.azure.com) "
        "or a Foundry project endpoint (*.services.ai.azure.com/api/projects/<project-name>)."
    )


def print_config_summary() -> dict[str, str]:
    api_key = _require("AZURE_FOUNDRY_API_KEY", settings.AZURE_FOUNDRY_API_KEY)
    text_endpoint = _validate_text_endpoint(
        _require(
            "AZURE_FOUNDRY_TEXT_ENDPOINT",
            settings.AZURE_FOUNDRY_TEXT_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT,
        )
    )
    image_endpoint = _validate_image_endpoint(
        _require(
            "AZURE_FOUNDRY_IMAGE_ENDPOINT",
            settings.AZURE_FOUNDRY_IMAGE_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT,
        )
    )
    api_version = _require("AZURE_FOUNDRY_API_VERSION", settings.AZURE_FOUNDRY_API_VERSION)
    text_deployment = _require("AZURE_FOUNDRY_TEXT_DEPLOYMENT", settings.AZURE_FOUNDRY_TEXT_DEPLOYMENT)
    image_deployment = _require("AZURE_FOUNDRY_IMAGE_DEPLOYMENT", settings.AZURE_FOUNDRY_IMAGE_DEPLOYMENT)

    print("Azure Foundry config")
    print(f"  CARE_CIRCLE_TEXT_PROVIDER: {settings.CARE_CIRCLE_TEXT_PROVIDER}")
    print(f"  CARE_CIRCLE_IMAGE_PROVIDER: {settings.CARE_CIRCLE_IMAGE_PROVIDER}")
    print(f"  AZURE_FOUNDRY_API_KEY: {_mask_secret(api_key)}")
    print(f"  AZURE_FOUNDRY_TEXT_ENDPOINT: {text_endpoint}")
    print(f"  AZURE_FOUNDRY_IMAGE_ENDPOINT: {image_endpoint}")
    print(f"  AZURE_FOUNDRY_API_VERSION: {api_version}")
    print(f"  AZURE_FOUNDRY_TEXT_DEPLOYMENT: {text_deployment}")
    print(f"  AZURE_FOUNDRY_IMAGE_DEPLOYMENT: {image_deployment}")
    print(f"  Expected text base URL: {text_endpoint}/openai/v1/")
    if image_endpoint.endswith("/openai/v1"):
        print(f"  Expected image base URL: {image_endpoint}/")
    else:
        print(f"  Expected image base URL: {image_endpoint}/openai/v1/")

    if str(settings.CARE_CIRCLE_TEXT_PROVIDER).strip().upper() != "AZURE_FOUNDRY":
        raise RuntimeError("CARE_CIRCLE_TEXT_PROVIDER is not set to AZURE_FOUNDRY.")

    return {
        "text_endpoint": text_endpoint,
        "image_endpoint": image_endpoint,
        "text_deployment": text_deployment,
        "image_deployment": image_deployment,
    }


async def run_text_smoke_test() -> None:
    print("\nRunning text smoke test...")
    response = await generate_text_with_usage(
        prompt="Reply with exactly OK.",
        system="You are a verification assistant. Reply with exactly OK.",
        max_tokens=8,
        temperature=0,
    )
    print("  Text smoke test succeeded")
    print(f"  Model/deployment used: {response.model}")
    print(f"  Response: {response.content!r}")
    print(f"  Tokens: {response.total_tokens}")


async def run_image_smoke_test() -> None:
    print("\nRunning image smoke test...")
    response = await generate_image_url_with_usage("Generate a tiny plain blue square.")
    print("  Image smoke test succeeded")
    print(f"  Model/deployment used: {response.model}")
    print(f"  Returned URL/data prefix: {response.content[:80]}")


async def _main(include_image: bool) -> int:
    try:
        print_config_summary()
        await run_text_smoke_test()
        if include_image:
            await run_image_smoke_test()
        print("\nAzure Foundry verification passed.")
        return 0
    except Exception as exc:
        print("\nAzure Foundry verification failed.")
        print(f"  Error: {exc}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Azure Foundry Care Circle configuration.")
    parser.add_argument(
        "--image",
        action="store_true",
        help="Also run a live image smoke test against AZURE_FOUNDRY_IMAGE_DEPLOYMENT.",
    )
    args = parser.parse_args()
    return asyncio.run(_main(include_image=args.image))


if __name__ == "__main__":
    raise SystemExit(main())

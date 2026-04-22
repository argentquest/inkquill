from types import SimpleNamespace

import pytest

from app.services.care_circle import llm_helpers


pytestmark = pytest.mark.unit


@pytest.fixture
def fake_openai_module(monkeypatch):
    class DummyAsyncOpenAI:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class DummyAsyncAzureOpenAI:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_module = SimpleNamespace(
        AsyncOpenAI=DummyAsyncOpenAI,
        AsyncAzureOpenAI=DummyAsyncAzureOpenAI,
    )
    monkeypatch.setitem(__import__("sys").modules, "openai", fake_module)
    return fake_module


@pytest.fixture
def reset_care_circle_provider_settings(monkeypatch):
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_TEXT_PROVIDER", "AUTO", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_IMAGE_PROVIDER", "AUTO", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "LMSTUDIO_ENABLED", False, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "LMSTUDIO_BASE_URL", "http://localhost:1234/v1", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "LMSTUDIO_MODEL", "local-model", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENROUTER_API_KEY", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENROUTER_SITE_URL", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENROUTER_APP_NAME", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENAI_API_KEY", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "OPENAI_IMAGE_MODEL", "gpt-image-1", raising=False)
    monkeypatch.setattr(
        llm_helpers.settings,
        "CARE_CIRCLE_DEFAULT_TEXT_MODEL",
        "google/gemini-3.1-flash-lite-preview",
        raising=False,
    )
    monkeypatch.setattr(
        llm_helpers.settings,
        "CARE_CIRCLE_DEFAULT_IMAGE_MODEL",
        "gpt-image-1",
        raising=False,
    )
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_ENDPOINT", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_VERSION", "2024-10-21", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_TEXT_DEPLOYMENT", None, raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_IMAGE_DEPLOYMENT", None, raising=False)


def test_build_text_client_uses_azure_foundry_when_selected(
    monkeypatch,
    fake_openai_module,
    reset_care_circle_provider_settings,
):
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_TEXT_PROVIDER", "AZURE_FOUNDRY", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", "azure-key", raising=False)
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_ENDPOINT",
        "https://example-resource.openai.azure.com/",
        raising=False,
    )
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_TEXT_DEPLOYMENT",
        "care-circle-text",
        raising=False,
    )

    client, model_name = llm_helpers._build_text_client()

    assert isinstance(client, fake_openai_module.AsyncAzureOpenAI)
    assert client.kwargs["api_key"] == "azure-key"
    assert client.kwargs["azure_endpoint"] == "https://example-resource.openai.azure.com"
    assert client.kwargs["api_version"] == "2024-10-21"
    assert model_name == "care-circle-text"


def test_build_text_client_normalizes_project_endpoint_to_resource_root(
    monkeypatch,
    fake_openai_module,
    reset_care_circle_provider_settings,
):
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_TEXT_PROVIDER", "AZURE_FOUNDRY", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", "azure-key", raising=False)
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_ENDPOINT",
        "https://aiclassus2-resource.services.ai.azure.com/api/projects/aiclassus2",
        raising=False,
    )
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_TEXT_DEPLOYMENT",
        "care-circle-text",
        raising=False,
    )

    client, _ = llm_helpers._build_text_client()

    assert isinstance(client, fake_openai_module.AsyncAzureOpenAI)
    assert client.kwargs["azure_endpoint"] == "https://aiclassus2-resource.services.ai.azure.com"


def test_build_image_client_uses_azure_foundry_when_selected(
    monkeypatch,
    fake_openai_module,
    reset_care_circle_provider_settings,
):
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_IMAGE_PROVIDER", "AZURE_FOUNDRY", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", "azure-key", raising=False)
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_ENDPOINT",
        "https://example-resource.openai.azure.com/",
        raising=False,
    )
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_IMAGE_DEPLOYMENT",
        "care-circle-image",
        raising=False,
    )

    client, model_name = llm_helpers._build_image_client()

    assert isinstance(client, fake_openai_module.AsyncAzureOpenAI)
    assert model_name == "care-circle-image"


def test_build_text_client_auto_falls_back_to_openrouter_before_azure(
    monkeypatch,
    fake_openai_module,
    reset_care_circle_provider_settings,
):
    monkeypatch.setattr(llm_helpers.settings, "OPENROUTER_API_KEY", "router-key", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", "azure-key", raising=False)
    monkeypatch.setattr(
        llm_helpers.settings,
        "AZURE_FOUNDRY_ENDPOINT",
        "https://example-resource.openai.azure.com/",
        raising=False,
    )

    client, model_name = llm_helpers._build_text_client()

    assert isinstance(client, fake_openai_module.AsyncOpenAI)
    assert client.kwargs["api_key"] == "router-key"
    assert client.kwargs["base_url"] == "https://openrouter.ai/api/v1"
    assert model_name == "google/gemini-3.1-flash-lite-preview"


def test_build_text_client_raises_when_azure_foundry_selected_without_endpoint(
    monkeypatch,
    fake_openai_module,
    reset_care_circle_provider_settings,
):
    monkeypatch.setattr(llm_helpers.settings, "CARE_CIRCLE_TEXT_PROVIDER", "AZURE_FOUNDRY", raising=False)
    monkeypatch.setattr(llm_helpers.settings, "AZURE_FOUNDRY_API_KEY", "azure-key", raising=False)

    with pytest.raises(RuntimeError, match="AZURE_FOUNDRY_ENDPOINT"):
        llm_helpers._build_text_client()

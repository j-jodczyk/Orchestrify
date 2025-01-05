import pytest
from website.backend.handlers.get_models import handle_get_models


@pytest.fixture
def mock_models():
    return {"model1": "details1", "model2": "details2"}


def test_handle_get_models(monkeypatch, mock_models):
    monkeypatch.setattr("website.backend.handlers.get_models.models", mock_models)

    result = handle_get_models()

    assert result == {"models": ["model1", "model2"]}

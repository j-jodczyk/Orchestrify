import pytest
import io
from fastapi.testclient import TestClient
from website.backend.main import app

# from website.backend.handlers.get_models import handle_get_models
# from website.backend.handlers.generate_midi import handle_generate_midi


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}


def test_get_models(client, monkeypatch):
    def mock_handle_get_models():
        return {"models": ["model1", "model2"]}

    monkeypatch.setattr(
        "website.backend.main.handle_get_models", mock_handle_get_models
    )

    response = client.get("/models")
    assert response.status_code == 200
    assert response.json() == {"models": ["model1", "model2"]}


@pytest.mark.asyncio
async def test_generate_midi_no_file(client):
    response = client.post("/generate/", data={})
    assert response.status_code == 400
    assert response.json() == {"success": False, "message": "Missing file"}


@pytest.mark.asyncio
async def test_generate_midi_success(client, monkeypatch, tmpdir):
    from fastapi.responses import StreamingResponse

    async def mock_handle_generate_midi(form_data, file):
        midi_data = b"Mock MIDI data"
        return StreamingResponse(io.BytesIO(midi_data), media_type="audio/midi")

    monkeypatch.setattr(
        "website.backend.main.handle_generate_midi", mock_handle_generate_midi
    )

    mock_file = tmpdir.join("test.mid")
    mock_file.write("Mock content")

    with open(mock_file, "rb") as file:
        response = client.post(
            "/generate/",
            files={"file": ("test.mid", file)},
            data={"model": "model1", "density": 0.5},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/midi"

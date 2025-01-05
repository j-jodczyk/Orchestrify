import pytest
from pydantic import ValidationError
import tempfile
import note_seq
import io
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from website.backend.handlers.generate_midi import handle_generate_midi, GenerateParams


@pytest.fixture
def mock_models():
    return {
        "valid_model": {"tokenizer": "mock_tokenizer", "model": "mock_model"},
    }


@pytest.fixture
def mock_generate_params():
    return {"model": "valid_model", "density": 0.5}


@pytest.fixture
def mock_file():
    midi_data = b"MIDI content"
    return UploadFile(filename="test.mid", file=io.BytesIO(midi_data))


@pytest.fixture
def mock_large_file():
    large_data = b"MIDI content" * 1000000
    return UploadFile(filename="large_test.mid", file=io.BytesIO(large_data))


def test_generate_midi_validation_error(mock_models, monkeypatch):
    monkeypatch.setattr("website.backend.handlers.generate_midi.models", mock_models)

    invalid_params = {"model": "invalid_model", "density": 1.5}
    with pytest.raises(ValueError) as excinfo:
        GenerateParams(**invalid_params)

    errors = excinfo.value.errors()
    assert len(errors) == 2
    assert errors[0]["type"] == "value_error"
    assert "Model 'invalid_model' is not in the list of available models." in errors[0]["msg"]
    assert errors[1]["type"] == "less_than_equal"


@pytest.mark.asyncio
async def test_generate_midi_success(mock_models, mock_generate_params, mock_file, monkeypatch):
    def mock_generate_midi_score(input_file, density, tokenizer, model):
        note_sequence = note_seq.protobuf.music_pb2.NoteSequence()
        note_sequence.tempos.add().qpm = 120.0
        note_sequence.ticks_per_quarter = note_seq.constants.STANDARD_PPQ
        return note_sequence

    monkeypatch.setattr("website.backend.handlers.generate_midi.models", mock_models)
    monkeypatch.setattr(
        "website.backend.handlers.generate_midi.generate_midi_score",
        mock_generate_midi_score,
    )

    response = await handle_generate_midi(mock_generate_params, mock_file)

    assert response.status_code == 200
    assert response.media_type == "audio/midi"


@pytest.mark.asyncio
async def test_generate_midi_large_file(mock_models, mock_generate_params, mock_large_file, monkeypatch):
    monkeypatch.setattr("website.backend.handlers.generate_midi.models", mock_models)

    def mock_generate_midi_score(input_file, density, tokenizer, model):
        raise ValueError("File too large!")

    monkeypatch.setattr(
        "website.backend.handlers.generate_midi.generate_midi_score",
        mock_generate_midi_score,
    )

    with pytest.raises(HTTPException) as excinfo:
        await handle_generate_midi(mock_generate_params, mock_large_file)

    assert excinfo.value.status_code == 500
    assert "The file is too large" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_generate_midi_unexpected_error(mock_models, mock_generate_params, mock_file, monkeypatch):
    async def mock_generate_midi_score(input_file, density, tokenizer, model):
        raise Exception("Unexpected error!")

    monkeypatch.setattr("website.backend.handlers.generate_midi.models", mock_models)
    monkeypatch.setattr(
        "website.backend.handlers.generate_midi.generate_midi_score",
        mock_generate_midi_score,
    )

    with pytest.raises(HTTPException) as excinfo:
        await handle_generate_midi(mock_generate_params, mock_file)

    assert excinfo.value.status_code == 500
    assert "Error processing file" in str(excinfo.value.detail)

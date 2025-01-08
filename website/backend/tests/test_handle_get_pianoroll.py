import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from io import BytesIO
from unittest.mock import MagicMock, patch
from handlers.get_pianoroll import handle_get_painoroll


@pytest.mark.asyncio
async def test_handle_get_painoroll_valid_midi(monkeypatch):
    valid_midi_data = b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\x80MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00"
    file = UploadFile(filename="test.mid", file=BytesIO(valid_midi_data))

    mock_note_sequence = MagicMock()
    monkeypatch.setattr(
        "handlers.get_pianoroll.midi_io.midi_file_to_note_sequence",
        lambda _: mock_note_sequence,
    )
    monkeypatch.setattr("handlers.get_pianoroll.plot_sequence", lambda _: None)
    monkeypatch.setattr(
        "handlers.get_pianoroll.file_html",
        lambda doc, resources, title: "<html>Mock HTML</html>",
    )

    response = await handle_get_painoroll(file)

    assert isinstance(response, HTMLResponse)
    assert response.status_code == 200
    assert "<html>" in response.body.decode()


@pytest.mark.asyncio
async def test_handle_get_painoroll_invalid_file(monkeypatch):
    invalid_data = b"This is not a MIDI file."
    file = UploadFile(filename="invalid.txt", file=BytesIO(invalid_data))

    monkeypatch.setattr(
        "handlers.get_pianoroll.midi_io.midi_file_to_note_sequence",
        lambda _: (_ for _ in ()).throw(ValueError("Invalid MIDI file")),
    )

    with pytest.raises(ValueError, match="Invalid MIDI file"):
        await handle_get_painoroll(file)


@pytest.mark.asyncio
async def test_handle_get_painoroll_empty_file(monkeypatch):
    empty_file = UploadFile(filename="empty.mid", file=BytesIO(b""))

    monkeypatch.setattr(
        "handlers.get_pianoroll.midi_io.midi_file_to_note_sequence",
        lambda _: (_ for _ in ()).throw(ValueError("Empty file")),
    )

    with pytest.raises(Exception):
        await handle_get_painoroll(empty_file)


@pytest.mark.asyncio
async def test_handle_get_painoroll_large_midi(monkeypatch):
    large_midi_data = b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\x80" + b"\x00" * 10**6
    file = UploadFile(filename="large.mid", file=BytesIO(large_midi_data))

    mock_note_sequence = MagicMock()
    monkeypatch.setattr(
        "handlers.get_pianoroll.midi_io.midi_file_to_note_sequence",
        lambda _: mock_note_sequence,
    )
    monkeypatch.setattr("handlers.get_pianoroll.plot_sequence", lambda _: None)
    monkeypatch.setattr(
        "handlers.get_pianoroll.file_html",
        lambda doc, resources, title: "<html>Mock HTML</html>",
    )

    response = await handle_get_painoroll(file)

    assert isinstance(response, HTMLResponse)
    assert response.status_code == 200
    assert "<html>" in response.body.decode()

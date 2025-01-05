import pytest
import os
from unittest.mock import MagicMock, Mock
from src.models.errors import InvalidFileFormatError, UnknownModelError
from src.models.generate_midi import verify_paths, verify_model, generate_midi_score
import note_seq
from music21.stream.base import Score

mock_models = {"model_a": {"model": "path_a", "tokenizer": "path_a"}}


@pytest.fixture
def mock_models_list(monkeypatch):
    monkeypatch.setattr("src.models.generate_midi.models", mock_models)


@pytest.mark.parametrize(
    "path_to_midi,output_path",
    [
        ("valid_file.mid", "valid_directory"),
    ],
)
def test_verify_paths_valid(monkeypatch, path_to_midi, output_path):
    monkeypatch.setattr("os.path.isfile", lambda path: path == "valid_file.mid")
    monkeypatch.setattr("os.path.isdir", lambda path: path == "valid_directory")

    verify_paths(path_to_midi, output_path)


@pytest.mark.parametrize("path_to_midi", ["missing_file.mid"])
def test_verify_paths_file_not_found(monkeypatch, path_to_midi):
    monkeypatch.setattr("os.path.isfile", lambda path: False)  # File does not exist

    with pytest.raises(FileNotFoundError, match="does not exist"):
        verify_paths(path_to_midi, "valid_directory")


@pytest.mark.parametrize("path_to_midi", ["invalid_file.txt"])
def test_verify_paths_invalid_format(monkeypatch, path_to_midi):
    monkeypatch.setattr("os.path.isfile", lambda path: True)  # File exists

    with pytest.raises(InvalidFileFormatError, match="MIDI format"):
        verify_paths(path_to_midi, "valid_directory")


@pytest.mark.parametrize("output_path", ["invalid_directory"])
def test_verify_paths_not_a_directory(monkeypatch, output_path):
    monkeypatch.setattr("os.path.isfile", lambda path: True)  # File exists
    monkeypatch.setattr("os.path.isdir", lambda path: False)  # Not a directory

    with pytest.raises(NotADirectoryError, match="not a valid directory"):
        verify_paths("valid_file.mid", output_path)


def test_verify_model_valid(mock_models_list):
    verify_model("model_a")


def test_verify_model_invalid(mock_models_list):
    with pytest.raises(UnknownModelError, match="is not an available model"):
        verify_model("invalid_model")


@pytest.mark.parametrize("save_tokens", [True, False])
def test_generate_midi(monkeypatch, save_tokens):
    mock_parse = MagicMock(return_value=Score())
    monkeypatch.setattr("src.models.generate_midi.converter.parse", mock_parse)
    mock_preprocess = MagicMock(return_value={})
    monkeypatch.setattr("src.models.generate_midi.preprocess_music21_song", mock_preprocess)
    mock_encode = MagicMock(return_value=[])
    monkeypatch.setattr("src.models.generate_midi.encode_song_data_singular", mock_encode)
    mock_download = MagicMock(return_value="tokenizer_path")
    monkeypatch.setattr("src.models.generate_midi.hf_hub_download", mock_download)
    mock_tokenizer = Mock()
    mock_tokenizer_obj = Mock()
    mock_tokenizer.return_value = mock_tokenizer_obj
    monkeypatch.setattr("src.models.generate_midi.PreTrainedTokenizerFast", mock_tokenizer)
    mock_model = Mock()
    mock_model_obj = Mock()
    mock_model_obj.generate.return_value = ["first token"]
    mock_model.return_value = mock_model_obj
    monkeypatch.setattr("src.models.generate_midi.GPT2LMHeadModel.from_pretrained", mock_model)
    mock_convert = MagicMock(return_value=note_seq.protobuf.music_pb2.NoteSequence())
    monkeypatch.setattr("src.models.generate_midi.token_sequence_to_note_sequence", mock_convert)
    mock_open = MagicMock()
    monkeypatch.setattr("builtins.open", mock_open)
    mock_json_dump = MagicMock()
    monkeypatch.setattr("json.dump", mock_json_dump)

    generate_midi_score(
        "/path/to/midi", 0.5, "tokenizer_repo", "model_repo", save_tokens=save_tokens
    )  # todo: parametrize save_tokens

    mock_parse.assert_called_once_with("/path/to/midi")
    mock_preprocess.assert_called_once()
    mock_encode.assert_called_once()
    mock_download.assert_called_once_with(repo_id="tokenizer_repo", filename="tokenizer.json", repo_type="dataset")
    mock_tokenizer.assert_called_once_with(tokenizer_file="tokenizer_path")
    mock_tokenizer_obj.add_special_tokens.assert_called_once_with({"pad_token": "[PAD]"})
    mock_tokenizer_obj.encode.assert_called_once()
    mock_tokenizer_obj.decode.assert_called_once()
    mock_model_obj.generate.assert_called_once()
    mock_convert.assert_called_once()

    if save_tokens:
        mock_open.assert_called_once_with(os.path.join(".", "data.json"), "w+")
        mock_json_dump.assert_called_once()
    else:
        mock_open.assert_not_called()
        mock_json_dump.assert_not_called()

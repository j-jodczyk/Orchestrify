from pydantic import BaseModel, ValidationError, field_validator, Field
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
import os
import note_seq
import tempfile
from src.models.models_list import models
from src.models.generate_midi import generate_orchestrified_midi

TOKENIZER_FILENAME = "tokenizer.json"


class GenerateParams(BaseModel):
    """
    Parameters for generating MIDI.

    Attributes:
        model (str): The name of the model to use for generation. Must be in the list of available models.
        density (float): A density value for the generation process, must be between 0 and 1.
    """

    model: str
    density: float = Field(..., ge=0, le=1, description="Density value must be between 0 and 1.")

    @field_validator("model")
    def model_should_be_in_model_list(cls, model):
        if model not in list(models.keys()):
            raise ValueError(f"Model '{model}' is not in the list of available models.")
        return model


async def handle_generate_midi(form_data: dict, file: UploadFile = File(...)):
    """
    Handles the generation of MIDI files from uploaded input.

    Args:
        form_data (dict): Form data containing the generation parameters.
        file (UploadFile): An uploaded MIDI file to be processed.

    Returns:
        StreamingResponse: A streaming response containing the generated MIDI file.

    Raises:
        HTTPException: If the file is too large or an error occurs during processing.
    """
    temp_filepath = ""
    temp_generated_filepath = ""
    generate_params = GenerateParams(**form_data)
    repos = models[generate_params.model]

    try:
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_filepath = temp_file.name

        generated_midi_score = generate_orchestrified_midi(
            temp_filepath, generate_params.density, repos["tokenizer"], repos["model"]
        )

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as temp_generated_file:
            temp_generated_filepath = temp_generated_file.name
            note_seq.note_seq.sequence_proto_to_midi_file(generated_midi_score, temp_generated_filepath)

        midi_buffer = io.BytesIO()
        with open(temp_generated_filepath, "rb") as f:
            midi_buffer.write(f.read())

        midi_buffer.seek(0)

        return StreamingResponse(
            midi_buffer,
            media_type="audio/midi",
            headers={"Content-Disposition": "attachment; filename=generated.mid"},
        )

    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The file is too large, please try with a smaller file.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    finally:
        if temp_filepath != "" and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        if temp_generated_filepath != "" and os.path.exists(temp_generated_filepath):
            os.remove(temp_generated_filepath)

from pydantic import BaseModel, ValidationError, field_validator
from fastapi import FastAPI, File, Form, UploadFile, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
import io
import os
import note_seq
import tempfile
from models.models_list import models
from src.generate_midi import generate_midi_score

TOKENIZER_FILENAME = "tokenizer.json"

class GenerateParams(BaseModel):
    model: str
    density: float = Form(...)

    @field_validator('model')
    def model_should_be_in_model_list(cls,model):
        if model not in list(models.keys()):
            raise ValidationError
        return model

async def handle_generate_midi(
        form_data: dict,
        file: UploadFile = File(...)
        ):
    generate_params = GenerateParams(**form_data)
    repos = models[generate_params.model]

    try:
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_filepath = temp_file.name

        generated_midi_score = generate_midi_score(
            temp_filepath,
            generate_params.density,
            repos["tokenizer"],
            repos["model"]
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
            headers={"Content-Disposition": "attachment; filename=generated.mid"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    finally:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        if os.path.exists(temp_generated_filepath):
            os.remove(temp_generated_filepath)





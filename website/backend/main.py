import json
from fastapi import FastAPI, Request, UploadFile, Response, File
from fastapi.middleware.cors import CORSMiddleware
from handlers.get_models import handle_get_models
from handlers.generate_midi import handle_generate_midi


app = FastAPI()

origins = ["http://localhost", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/models")
async def get_models():
    """
    Endpoint to retrieve available models.

    Returns:
        list: A list of available models, as returned by `handle_get_models`.
    """
    return handle_get_models()


@app.post("/generate/")
async def generate_midi(request: Request, file: UploadFile = None):
    """
    Endpoint to generate MIDI files from provided data and file.

    Args:
        request (Request): The HTTP request containing form data.
        file (UploadFile, optional): An uploaded file object. Defaults to None.

    Returns:
        Response: A JSON response indicating success or failure of the operation.
    """
    if file is None:
        return Response(
            content=json.dumps({"success": False, "message": "Missing file"}),
            status_code=400,
        )
    form_data = await request.form()
    form_data = {key: form_data[key] for key in form_data if key != "file"}

    res = await handle_generate_midi(form_data, file)
    return res

import json
from fastapi import FastAPI, Request, UploadFile, Response, status
from handlers.get_models import handle_get_models
from handlers.generate_midi import GenerateParams, handle_generate_midi

app = FastAPI()

# we need a way to
# - get all available models
# - upload a file to generate


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/models")
async def get_models():
    return handle_get_models()


@app.post("/generate/")
async def generate_midi(request: Request, file: UploadFile = None):
    if file is None:
        return Response(
            content=json.dumps({"success": False, "message": "Missing file"}),
            status_code=400,
        )
    form_data = await request.form()
    form_data = {key: form_data[key] for key in form_data if key != "file"}

    res = await handle_generate_midi(form_data, file)
    return res

from src.models.models_list import models


def handle_get_models():
    return {"models": list(models.keys())}

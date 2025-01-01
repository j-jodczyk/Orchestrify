from src.models.models_list import models


def handle_get_models():
    """
    Returns a list of available models.
    """
    return {"models": list(models.keys())}

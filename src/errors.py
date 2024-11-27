class InvalidFileFormatError(ValueError):
    def __init__(self, message="The file format is invalid."):
        super().__init__(message)

class UnknownModelError(ValueError):
    def __init__(self, message="Attempt to use unknown model."):
        super().__init__(message)

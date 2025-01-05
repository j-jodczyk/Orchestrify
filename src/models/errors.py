class InvalidFileFormatError(ValueError):
    """
    Exception raised for errors in the input file format.

    This exception is specifically used when the provided file is not of the expected MIDI format.

    Attributes:
        message (str): Explanation of the error. Defaults to "The file format is invalid."
    """

    def __init__(self, message="The file format is invalid."):
        super().__init__(message)


class UnknownModelError(ValueError):
    """
    Exception raised when an attempt is made to use an unknown model.

    This exception is used to indicate that the specified model name does not match any available models.

    Attributes:
        message (str): Explanation of the error. Defaults to "Attempt to use unknown model."
    """

    def __init__(self, message="Attempt to use unknown model."):
        super().__init__(message)

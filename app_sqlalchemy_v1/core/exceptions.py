class FastapiDemoError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NotFoundError(FastapiDemoError):
    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedError(FastapiDemoError):
    def __init__(self, message: str):
        super().__init__(message)

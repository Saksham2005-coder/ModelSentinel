class CLIError(Exception):
    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)

class APIError(CLIError):
    def __init__(self, message: str):
        super().__init__(message, exit_code=3)

class NotFoundError(CLIError):
    def __init__(self, message: str):
        super().__init__(message, exit_code=4)

class RejectedOperationError(CLIError):
    def __init__(self, message: str):
        super().__init__(message, exit_code=5)

class GateFailureError(CLIError):
    def __init__(self, message: str):
        super().__init__(message, exit_code=6)

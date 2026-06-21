
class NotFoundException(Exception):
    def __init__(self, error_code: str, message: str = "Resource not found"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class BusinessLogicException(Exception):
    def __init__(self, error_code: str, message: str = "Business logic error"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AlreadyExistsException(Exception):
    def __init__(self, error_code: str, message: str = "Resource already exists"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AuthException(Exception):
    def __init__(self, error_code: str, message):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationException(Exception):
    def __init__(self, error_code: str, message: str = "Validation error"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class PermissionDeniedException(Exception):
    def __init__(self, error_code: str, message: str = "Permission denied"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

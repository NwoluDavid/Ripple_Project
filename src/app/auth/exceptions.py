from app.exceptions import BaseException


class InvalidPasswordException(BaseException):
    def __init__(self, message) -> None:
        super().__init__(message)
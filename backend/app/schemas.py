import re
from pydantic import BaseModel, field_validator

LOGIN_REGEX = re.compile(r"^[A-Za-z0-9._-]{3,32}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)


class RegisterRequest(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        if not LOGIN_REGEX.match(value):
            raise ValueError(
                "Login must be 3-32 characters and contain only letters, numbers, dots, underscores, or hyphens."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
            )
        return value


class MessageResponse(BaseModel):
    message: str

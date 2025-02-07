from typing import Any, List, Optional, Self

from fastapi import Form
from pydantic import BaseModel, Field, FileUrl, PositiveInt, model_validator


class RegistrationForm(BaseModel):
    password: str = Field(min_length=8)
    repeat_password: str = Field(min_length=8)

    @classmethod
    def as_form(cls, password: str = Form(...), repeat_password: str = Form(...)) -> BaseModel:
        return cls(password=password, repeat_password=repeat_password)

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.repeat_password:
            raise ValueError('Пароли не совпадают')
        return self

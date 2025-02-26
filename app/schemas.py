import datetime
from typing import Self, Union

from fastapi import Form
from pydantic import BaseModel, Field, model_validator


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


class LoginForm(BaseModel):
    password: str = Field(min_length=8)

    @classmethod
    def as_form(cls, password: str = Form(...)) -> BaseModel:
        return cls(password=password)


class HabitForm(BaseModel):
    title: str
    description: Union[str, None] = None
    target: int
    alert_time: datetime.time

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        target: int = Form(...),
        alert_time: datetime.time = Form(...),
    ) -> BaseModel:
        return cls(title=title, description=description, target=target, alert_time=alert_time)

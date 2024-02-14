from abc import ABC
from typing import Optional, Type

import pydantic


class AbstractUser(pydantic.BaseModel, ABC):
    name: str
    password: str

    @pydantic.field_validator("name")
    @classmethod
    def name_length(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("Maxima length of name is 100")
        return v

    @pydantic.field_validator("password")
    @classmethod
    def secure_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(f"Minimal length of password is 8")
        return v

class AbstractAd(pydantic.BaseModel, ABC):
    title: str

    @pydantic.field_validator("name")
    @classmethod
    def title_length(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("Maxima length of title is 100")
        return v

class CreateUser(AbstractUser):
    name: str
    password: str

class UpdateUser(AbstractUser):
    name: Optional[str] = None
    password: Optional[str] = None

class CreateAd(AbstractAd):
    title: str

class UpdateAd(AbstractAd):
    title: Optional[str] = None


SCHEMA_CLASS = Type[CreateUser | UpdateUser | CreateAd | UpdateAd]
SCHEMA = CreateUser | UpdateAd | CreateAd | UpdateAd


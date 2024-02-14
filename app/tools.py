from errors import HttpError
from pydantic import ValidationError
from schema import SCHEMA_CLASS


def validate(schema_cls: SCHEMA_CLASS, json_data: dict | list):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)

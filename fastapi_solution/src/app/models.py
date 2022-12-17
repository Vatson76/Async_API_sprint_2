import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True

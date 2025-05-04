from sqlalchemy import inspect
from fastapi.params import Query
from pydantic import BaseModel


class Paginate(BaseModel):
    page: int
    per_page: int


def pagination_param(
    page: int = Query(ge=1, required=False, default=1, le=5000),
    per_page: int = Query(ge=1, required=False, default=10, le=100),
):
    return Paginate(page=page, per_page=per_page)


async def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

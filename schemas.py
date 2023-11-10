from pydantic import BaseModel


class AdSchema(BaseModel):
    token: str
    title: str
    description: str
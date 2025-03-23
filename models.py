from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


class DataPerjanjianPemasaranProperti(BaseModel):
    name: str
    email: str

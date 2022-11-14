from pydantic import BaseModel


class Event(BaseModel):
    image: str
    title: str
    description: str
    place: str
    date: str


class Profile(BaseModel):
    id: int
    name: str
    login: str

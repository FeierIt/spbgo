from pydantic import BaseModel


class Event(BaseModel):
    image: str
    title: str
    description: str
    place: str
    date: str
    is_free: bool
    weekday: str
    id: int
    site_url: str


class Profile(BaseModel):
    id: int
    name: str
    login: str

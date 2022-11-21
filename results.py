from pydantic import BaseModel


class UserData(BaseModel):
    access_token: str


class User:
    def __init__(self, login: str, hash_pwd="", name="", pwd=""):
        self.name = name
        self.login = login
        self.hash = hash_pwd
        self.pwd = pwd

from fastapi import FastAPI
from datetime import datetime
import requests
from models import Event, Profile

app = FastAPI()
url_api = "https://kudago.com/public-api/v1.4"


@app.post("/signin")
async def login(login: str, password: str):
    return {"access_token": "None"}  # Заглушка


@app.post("/singup")
async def register(name: str, login: str, password: str):
    return {"access_token": "None"}  # Заглушка


@app.get("/profile")
async def get_profile(access_token: str):
    profile = Profile(id=1,
                      name="None",
                      login="None")  # Заглушка
    return {"profile": profile}


@app.get("/api/events")
async def events(access_token: str, offset: int, limit: int):
    r = requests.get(f"{url_api}/events/?page={offset}&page_size={limit}&fields=dates,title,description,place,"
                     f"images&order_by=id&location=spb&")
    event_list = []
    for i in r.json()["results"]:  # Проход по всем событиям для нахождения адреса
        if i["place"] is not None:
            place = requests.get(f'https://kudago.com/public-api/v1.4/places/{i["place"]["id"]}/'
                                 f'?fields=title,address')  # Поиск адреса
            place = place.json()["address"]
            date = i["dates"][0]["end"]
            date = datetime.fromtimestamp(date).isoformat()  # Перевод даты в ISO формат
            event = Event(image=i["images"][0]["image"],
                          title=i["title"],
                          description=i["description"],
                          place=place,
                          date=date)
            event_list.append({"event": event})
    return event_list


@app.get("/api/event")
async def event(access_token: str, id: int):
    r = requests.get(f"{url_api}/events/?fields=dates,title,description,place,"f"images&location=spb&ids={id}")
    r = r.json()["results"][0]
    place = requests.get(f'https://kudago.com/public-api/v1.4/places/{r["place"]["id"]}/'
                         f'?fields=title,address')  # Поиск адреса
    place = place.json()["address"]
    date = r["dates"][0]["end"]
    date = datetime.fromtimestamp(date).isoformat()  # Перевод даты в ISO формат
    event = Event(image=r["images"][0]["image"],
                  title=r["title"],
                  description=r["description"],
                  place=place,
                  date=date)
    return {"event": event}

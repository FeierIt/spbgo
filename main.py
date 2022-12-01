import uvicorn
import math
from fastapi import FastAPI, HTTPException, Request, Header
from datetime import datetime
import requests
from models import Event, Profile
from user_interaction import UserInteractor
from results import UserData, UserForAuth, UserForReg
from weekday import WeekdayNameResolver
import time

app = FastAPI()
url_api = "https://kudago.com/public-api/v1.4"


@app.post("/signin")
async def login(user: UserForAuth):
    result = UserInteractor.authorize(user.login, user.password)
    if result.success:
        return UserData(access_token=result.token)
    raise HTTPException(400, detail=result.message)


@app.post("/signup")
async def register(user: UserForReg):
    result = UserInteractor.register(user.name, user.login, user.password)
    if result.success:
        return None
    raise HTTPException(400, detail=result.message)


@app.get("/profile")
async def get_profile(access_token: str | None = Header(default=None)):
    if access_token is None:
        raise HTTPException(400, detail="no token!")
    user = UserInteractor.authorized_request(access_token)
    if user is None:
        raise HTTPException(400, detail="wrong token!")
    return Profile(id=user[0], name=user[1], login=user[2])


@app.get("/events")
async def events(offset: int, limit: int, access_token: str | None = Header(default=None)):
    await get_profile(access_token)
    if offset % limit != 0:
        raise HTTPException(400)
    else:
        page = math.floor(offset / 100) + 1  # с какой страницы начинать загружать events
        print(page)
        offset %= 100  # оставшийся сдвиг
        offset_flag = False
        url_events = url_api + "/events/?page={}&page_size=100&" \
                               "fields=dates,title,description,id,place,images&order_by=id&location=spb&actual_since={}"  # здесь actual_since
        event_list = []
        timing = int(time.time())
        while True:
            r = requests.get(url_events.format(page, timing)).json()["results"] # здесь timing

            if not offset_flag:
                r = r[offset:]
                offset_flag = True
            for i in r:
                if i["place"] is not None:
                    place = requests.get(f'https://kudago.com/public-api/v1.4/places/{i["place"]["id"]}/'
                                         f'?fields=title,address')  # Поиск адреса
                    place = place.json()["address"]
                    date = i["dates"][0]["end"]
                    date = datetime.fromtimestamp(date)  # Перевод даты в datetime формат
                    weekday = WeekdayNameResolver.resolve(date)
                    event = Event(image=i["images"][0]["image"],
                                  title=i["title"],
                                  description=i["description"],
                                  place=place,
                                  date=date.isoformat(),  # Перевод даты в ISO формат
                                  is_free=False,  # Заглушка
                                  weekday=weekday, id=i["id"])
                    event_list.append({"event": event})
                if len(event_list) == limit:
                    break
            else:
                continue
            break
        return event_list


@app.get("/event")
async def event(id: int, access_token: str | None = Header(default=None)):
    await get_profile(access_token)
    r = requests.get(f"{url_api}/events/?fields=dates,title,description,id,place,"f"images&location=spb&ids={id}")
    r = r.json()["results"][0]
    place = requests.get(f'https://kudago.com/public-api/v1.4/places/{r["place"]["id"]}/'
                         f'?fields=title,address')  # Поиск адреса
    place = place.json()["address"]
    date = r["dates"][0]["end"]
    date = datetime.fromtimestamp(date)  # Перевод даты в datetime формат
    weekday = WeekdayNameResolver.resolve(date)
    event = Event(image=r["images"][0]["image"],
                  title=r["title"],
                  description=r["description"],
                  place=place,
                  date=date.isoformat(),  # Перевод даты в ISO формат
                  is_free=False,  # Заглушка
                  weekday=weekday, id=r["id"])
    return {"event": event}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

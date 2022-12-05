import uvicorn
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests
from models import Event, Profile
from user_interaction import UserInteractor
from results import UserData, UserForAuth, UserForReg
from weekday import WeekdayNameResolver
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
url_api = "https://kudago.com/public-api/v1.4"
places = {}


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
    profile = Profile(id=1,
                      name="None",
                      login="None")  # Заглушка
    return {"profile": profile}


@app.get("/events")
async def events(offset: int, limit: int, access_token: str | None = Header(default=None)):
    await get_profile(access_token)
    if offset % limit != 0:
        raise HTTPException(400)
    else:
        page = 1
        url_events = url_api + "/events/?page={}&page_size=100&" \
                               "fields=dates,title,description,id,place,images,site_url&" \
                               "order_by=id&location=spb&actual_since={}"  # здесь actual_since
        event_list = []
        timing = int(time.time())
        while True:
            r = requests.get(url_events.format(page, timing)).json()["results"]
            for i in r:
                if i["place"] is not None and offset == 0:
                    if i["place"]["id"] in places:
                        place = places[i["place"]["id"]]
                    else:
                        place = requests.get(f'https://kudago.com/public-api/v1.4/places/{i["place"]["id"]}/'
                                             f'?fields=title,address')  # Поиск адреса
                        place = place.json()
                        if "address" in place:
                            place = place["address"]
                        else:
                            place = "г. Санкт-Петербург"
                        places[i["place"]["id"]] = place
                    date = i["dates"][-1]["end"]
                    try:
                        date = datetime.fromtimestamp(date)  # Перевод даты в datetime формат
                    except (OSError, OverflowError):
                        date = datetime.fromtimestamp(0)
                    weekday = WeekdayNameResolver.resolve(date)
                    site_url = i["site_url"]
                    event = Event(image=i["images"][0]["image"],
                                  title=i["title"],
                                  description=i["description"],
                                  place=place,
                                  date=date.isoformat(),  # Перевод даты в ISO формат
                                  is_free=False,  # Заглушка
                                  weekday=weekday,
                                  id=i["id"],
                                  site_url=site_url)
                    event_list.append({"event": event})
                elif i["place"] is not None and offset != 0:
                    offset -= 1
                if len(event_list) == limit:
                    break
            else:
                page += 1
                continue
            break
        return event_list



@app.get("/event")
async def event(id: int, access_token: str | None = Header(default=None)):
    await get_profile(access_token)
    r = requests.get(f"{url_api}/events/?fields=dates,title,description,id,place,"f"images,site_url&location=spb&ids={id}")
    r = r.json()["results"][0]
    place = requests.get(f'https://kudago.com/public-api/v1.4/places/{r["place"]["id"]}/'
                         f'?fields=title,address')  # Поиск адреса
    place = place.json()["address"]
    date = r["dates"][-1]["end"]
    try:
        date = datetime.fromtimestamp(date)  # Перевод даты в datetime формат
    except (OSError, OverflowError):
        date = datetime.fromtimestamp(0)
    weekday = WeekdayNameResolver.resolve(date)
    site_url = r["site_url"]
    event = Event(image=r["images"][0]["image"],
                  title=r["title"],
                  description=r["description"],
                  place=place,
                  date=date.isoformat(),  # Перевод даты в ISO формат
                  is_free=False,  # Заглушка
                  weekday=weekday,
                  id=r["id"],
                  site_url=site_url)
    return {"event": event}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

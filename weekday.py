from datetime import datetime


class WeekdayNameResolver:
    @staticmethod
    def resolve(date):
        list_day = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day = date.weekday()
        return list_day[day]

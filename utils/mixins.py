from django.utils import timezone


class PersianTimeMixin:
    def persian_timesince(self, dt):
        now = timezone.now()
        diff = now - dt

        seconds = diff.total_seconds()
        minutes = seconds // 60
        hours = minutes // 60
        days = diff.days
        weeks = days // 7
        months = days // 30
        years = days // 365

        if seconds < 60:
            return "چند لحظه پیش"
        elif minutes < 60:
            return f"{int(minutes)} دقیقه پیش"
        elif hours < 24:
            return f"{int(hours)} ساعت پیش"
        elif days < 7:
            return f"{int(days)} روز پیش"
        elif weeks < 4:
            return f"{int(weeks)} هفته پیش"
        elif months < 12:
            return f"{int(months)} ماه پیش"
        else:
            return f"{int(years)} سال پیش"
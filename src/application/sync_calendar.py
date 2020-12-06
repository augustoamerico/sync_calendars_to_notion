from datetime import datetime
from src.repository import ICalendar


class CalendarSync:

    def __init__(self, calendar_origin: ICalendar, calendar_destiny: ICalendar, start_date: datetime, end_date: datetime):
        self._calendar_origin = calendar_origin
        self._calendar_destiny = calendar_destiny
        self._start_date = start_date
        self._end_date = end_date
    
    def sync(self):
        origin_events = self._calendar_origin.get_events(self._start_date, self._end_date)
        destiny_events = self._calendar_destiny.get_events(self._start_date, self._end_date)

        origin_events_map = dict(map(lambda event: (event["id"], event), origin_events))
        destiny_events_map = dict(map(lambda event: (event["id"], event), destiny_events))

        already_synched_events = set(origin_events_map.keys()).intersection(set(destiny_events_map.keys()))

        events_to_create_in_destiny = set(origin_events_map.keys()).difference(already_synched_events)
        events_id_not_in_origin = set(destiny_events_map.keys()).difference(set(origin_events_map.keys()))
        event_ids_to_remove_in_destiny = list(map(lambda event: event["id"], filter(
            lambda event: event["id"] in events_id_not_in_origin and
                          event["owner"] == self._calendar_origin.get_ownership_tag(), destiny_events)))

        self._calendar_destiny.create_events(
            list(filter(lambda event: event["id"] in events_to_create_in_destiny, origin_events)))

        self._calendar_destiny.remove_events(
            event_ids_to_remove_in_destiny
        )


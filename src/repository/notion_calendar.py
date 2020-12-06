from src.repository.i_calendar import ICalendar
from typing import List, Dict
from datetime import datetime, date
from notion.client import NotionClient
from notion.collection import NotionDate, CollectionRowBlock

class NotionCalendar(ICalendar):

    def __init__(self, tokenv2: str, notion_calendar_url: str, schema_map: Dict[str, str]):
        self._client = NotionClient(token_v2=tokenv2)
        self._notion_calendar_url = notion_calendar_url
        self._calendar = self._client.get_collection_view(self._notion_calendar_url)
        self._schema_map = schema_map

    def create_events(self, events: List[Dict[str, str]]):
        for event in events:
            self._create_event(event)

    def _create_event(self, event: Dict[str, str]):
        new_event = self._calendar.collection.add_row()
        self._attribute_events_properties(new_event, event)

    def _attribute_events_properties(self, model_event, json_event):

        for key in self._schema_map:
            if type(self._schema_map[key]) is not list:
                value = json_event[key]
                if type(json_event[key]) is datetime or type(json_event[key]) is date:
                    value = NotionDate(value)
                setattr(model_event, self._schema_map[key], value)
            else:
                value = json_event[key]
                nested = self._schema_map[key][0]["nested"]
                if type(json_event[key]) is datetime or type(json_event[key]) is date:
                    value = NotionDate(value)
                    setattr(model_event, nested[0], value)
                else:
                    accumulated_value = model_event
                    for i in len(nested):
                        if i == len(nested)-1:
                            setattr(accumulated_value, key, nested[i])
                        else:
                            accumulated_value = getattr(accumulated_value, nested[i])

        """model_event.Id = json_event["id"]
        model_event.name = json_event["name"]
        model_event.url = json_event["url"]
        model_event.start_date = NotionDate(json_event["start"])
        model_event.end_date = NotionDate(json_event["end"])
        model_event.organizer = json_event["organizer"]
        model_event.status = json_event["status"]"""

    
    def remove_events(self, ids: List[str]):
        events_stored = self._calendar.collection.get_rows()
        events_to_remove = list(filter(lambda event: event.Id in set(ids), events_stored))
        for event in events_to_remove:
            event.remove()
    
    def update_events(self, events: List[Dict[str, str]]):
        events_stored = self._calendar.collection.get_rows()
        events_to_update = set(list(map(lambda event: event.Id, events)))
        events_stored_to_update = dict(list(filter(lambda tuple: tuple[0] in events_to_update, map(lambda event: (event.Id, event), events_stored))))
        for event in events:
            self._attribute_events_properties(events_stored_to_update[event.Id], event)


    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, object]]:
        start_date_timestamp = datetime.timestamp(start_date)
        end_date_timestamp = datetime.timestamp(end_date)

        events = self._calendar.collection.get_rows()
        events_dates_in_datetime = map(lambda event: self._convert_dates_to_datetime(event), events)
        return list(filter(lambda event: self._get_timestamp(event["start"]) >= start_date_timestamp and
                                            self._get_timestamp(event["start"]) <= end_date_timestamp, events_dates_in_datetime))

    def _convert_dates_to_datetime(self, event: CollectionRowBlock) -> Dict[str, object]:
        event_json = {}
        for key in self._schema_map:
            if type(self._schema_map[key]) is not list:
                event_json[key] = getattr(event, self._schema_map[key])
            else:
                nested = self._schema_map[key][0]["nested"]
                accumulated_value = event
                for nested_key in nested:
                    accumulated_value = getattr(accumulated_value, nested_key)
                event_json[key] = accumulated_value

        """event_json["id"] = event.Id
        event_json["name"] = event.name 
        event_json["url"] = event.url
        event_json["start"] = event.start_date.start
        event_json["end"] = event.end_date.start
        event_json["organizer"] = event.organizer
        event_json["status"] = event.status
        event_json["owner"] = event.owner"""
        return event_json
    
    def get_ownership_tag(self):
        # self._notion_calendar_url
        return ""

    @staticmethod
    def _get_timestamp(moment):
        if type(moment) is datetime:
            return datetime.timestamp(moment)

        elif type(moment) is date:
            return datetime.timestamp(
                datetime(year=moment.year, month=moment.month, day=moment.day)
            )
        else:
            raise Exception("")

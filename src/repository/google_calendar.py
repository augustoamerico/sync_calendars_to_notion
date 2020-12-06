from typing import List, Dict
from datetime import datetime, date

from src.repository.i_calendar import ICalendar

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from google.oauth2 import service_account

class GoogleCalendar(ICalendar):

    def __init__(self, scopes: List[str], calendar_id: str, app_service_credentials_path: str, schema_map: Dict[str, str], fetch_size : int = 10):
        self._credentials = None
        self._scopes = scopes
        self._calendar_id = calendar_id
        self._app_service_credentials_path = app_service_credentials_path
        self._get_or_refresh_credentials(scopes, app_service_credentials_path, calendar_id)
        self._service = build('calendar', 'v3', credentials=self._credentials)
        self._fetch_size = fetch_size
        self._schema_map = schema_map

    def _get_or_refresh_credentials(self, scopes: List[str], app_service_credentials_path: str, calendar_id: str) -> Dict:
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # If there are no (valid) credentials available, let the user log in.
        if not self._credentials or not self._credentials:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
            else:
                self._credentials = service_account.Credentials.from_service_account_file(
                    app_service_credentials_path, scopes=scopes)

    def create_events(self, emax_timestampvents: List[Dict[str, str]]):
        raise NotImplemented()

    def _create_event(self, event: Dict[str, str]):
        raise NotImplemented()
    
    def remove_events(self, ids: List[str]):
        raise NotImplemented()
    
    def update_events(self, events: List[Dict[str, str]]):
        raise NotImplemented()

    def get_events(self, start_date: datetime, end_date: datetime) -> Dict[str, object]:
        min_date = start_date.isoformat() + 'Z' # 'Z' indicates UTC time
        start_date_timestamp = self._get_timestamp(start_date)
        end_date_timestamp = self._get_timestamp(end_date)
        max_timestamp = start_date_timestamp
        events = []
        while max_timestamp < end_date_timestamp:
            events_result = self._service.events().list(calendarId=self._calendar_id, timeMin=min_date,
                                            maxResults=self._fetch_size, singleEvents=True, orderBy='startTime').execute().get('items', [])
            events_dates_in_datetime = list(map(lambda event: self._convert_dates_to_datetime(event), events_result))
            
            events.extend(
                filter(lambda event: 
                    self._get_timestamp(event["start"]) <= end_date_timestamp, 
                events_dates_in_datetime))
            
            max_timestamp = max(map(lambda event: self._get_timestamp(event["start"]), events_dates_in_datetime))
            min_date = datetime.fromtimestamp(max_timestamp).isoformat() + 'Z'
        return events
    
    @staticmethod
    def _get_timestamp(moment):
        if type(moment) is datetime:
            return datetime.timestamp(moment)
        
        elif type(moment) is date:
            return datetime.timestamp(
                datetime(year=moment.year, month = moment.month, day = moment.day)
            )
        else:
            raise Exception("")

    def _convert_dates_to_datetime(self, event: Dict[str, object]):
        try:
            event["start"] = datetime.strptime(event["start"]["dateTime"], '%Y-%m-%dT%H:%M:%S%z')
        except KeyError:
            event["start"] = datetime.strptime(event["start"]["date"], '%Y-%m-%d').date()
        try:
            event["end"] = datetime.strptime(event["end"]["dateTime"], '%Y-%m-%dT%H:%M:%S%z')
        except KeyError:
            event["end"] = datetime.strptime(event["end"]["date"], '%Y-%m-%d').date()
        
        event["name"] = event["summary"]
        event["url"] = event["htmlLink"]
        event["organizer"] = event["organizer"]["email"]
        event["owner"] = self._calendar_id
        del event["summary"]
        del event["htmlLink"]
        return event

    def get_ownership_tag(self):
        return self._calendar_id

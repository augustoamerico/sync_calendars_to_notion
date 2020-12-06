from abc import ABC
from datetime import datetime
from typing import List, Dict

class ICalendar(ABC):
    
    def create_events(self, events: List[Dict[str, str]]):
        pass

    def _create_event(self, event: Dict[str, str]):
        pass
    
    def remove_events(self, ids: List[str]):
        pass
    
    def update_events(self, events: List[Dict[str, str]]):
        pass 

    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, str]]:
        pass

    def get_ownership_tag(self):
        pass
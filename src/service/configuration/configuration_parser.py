from src.repository import GoogleCalendar, NotionCalendar
from src.application.sync_calendar import CalendarSync
from datetime import datetime, timedelta


class UnknownCalendarType(Exception):
    pass


def parse_calendars(calendars_yaml_entry):
    calendar_by_name = {}
    for calendar_name in calendars_yaml_entry:
        calendar_by_name[calendar_name] = parse_calendar(calendars_yaml_entry[calendar_name], calendar_name)
    return calendar_by_name


def parse_calendar(calendar_yaml_entry, calendar_name):
    calendar_type = calendar_yaml_entry["type"].lower().strip()
    if calendar_type == "googlecalendar":
        credentials_file = calendar_yaml_entry["credentials_file_path"]
        scopes = calendar_yaml_entry["scopes"]
        calendar_id = calendar_yaml_entry["calendar_id"]
        schema_map = calendar_yaml_entry["schema"]
        return GoogleCalendar(scopes, calendar_id, credentials_file, schema_map)
    elif calendar_type == "notioncalendar":
        token = calendar_yaml_entry["notion_token"]
        calendar_url = calendar_yaml_entry["notion_calendar_url"]
        schema_map = calendar_yaml_entry["schema"]
        return NotionCalendar(token, calendar_url, schema_map)
    else:
        raise UnknownCalendarType(f"Unknown calendar type {calendar_type}")


def parse_sync_flow(flow_yaml_entry, calendars_by_name):
    assert "sync_from" in flow_yaml_entry and "sync_to" in flow_yaml_entry and "sync_time" in flow_yaml_entry
    sync_frequency = list(flow_yaml_entry["sync_time"].keys())[0]
    start_date = datetime.now()
    end_date = None
    if sync_frequency == "days":
        end_date = start_date + timedelta(days=flow_yaml_entry["sync_time"][sync_frequency])
    else:
        raise NotImplementedError()
    return CalendarSync(
        calendar_origin=calendars_by_name[flow_yaml_entry["sync_from"]],
        calendar_destiny=calendars_by_name[flow_yaml_entry["sync_to"]],
        start_date=start_date, end_date=end_date)


def parse_sync_flows(sync_yaml_entry, calendars_by_name):
    sync_flow_by_name = {}
    for sync_flow_name in sync_yaml_entry:
        sync_flow_by_name[sync_flow_name] = parse_sync_flow(sync_yaml_entry[sync_flow_name], calendars_by_name)
    return sync_flow_by_name

